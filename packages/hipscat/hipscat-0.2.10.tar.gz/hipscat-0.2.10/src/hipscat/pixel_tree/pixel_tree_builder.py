# pylint: disable=duplicate-code

from __future__ import annotations

from typing import List

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.healpix_pixel_convertor import HealpixInputTypes, get_healpix_pixel
from hipscat.pixel_tree.pixel_node import PixelNode
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree import PixelTree


class PixelTreeBuilder:
    """Build a PixelTree

    Initially a root node is created when the builder is initialized.
    Nodes can then be added to the tree.
    To create a pixel tree object once the tree is built, call the `build` method

    """

    def __init__(self):
        self.root_pixel = PixelNode((-1, -1), PixelNodeType.ROOT, None)
        self.pixels = {-1: {-1: self.root_pixel}}

    def build(self) -> PixelTree:
        """Build a `PixelTree` object from the nodes created

        Returns:
            The pixel tree with the nodes created in the builder
        """
        return PixelTree(self.root_pixel, self.pixels)

    @staticmethod
    def from_healpix(healpix_pixels: List[HealpixPixel]) -> PixelTree:
        """Build a tree from a list of constituent healpix pixels

        Args:
            healpix_pixels: list of healpix pixels

        Returns:
            The pixel tree with the leaf pixels specified in the list
        """
        builder = PixelTreeBuilder()
        for pixel in healpix_pixels:
            builder.create_node_and_parent_if_not_exist((pixel.order, pixel.pixel), PixelNodeType.LEAF)
        return builder.build()

    def contains(self, pixel: HealpixInputTypes) -> bool:
        """Check if tree contains a node at a given order and pixel

        Args:
            pixel: HEALPix pixel to check. Either of type `HealpixPixel`
                or a tuple of (order, pixel)

        Returns:
            True if the tree contains the pixel, False if not
        """
        if isinstance(pixel, HealpixPixel):
            return pixel.order in self.pixels and pixel.pixel in self.pixels[pixel.order]
        if isinstance(pixel, tuple):
            return pixel[0] in self.pixels and pixel[1] in self.pixels[pixel[0]]
        raise TypeError("pixel must be either a HealpixPixel object or a Tuple of (order, pixel)")

    def __contains__(self, item):
        return self.contains(item)

    def get_node(self, pixel: HealpixInputTypes) -> PixelNode | None:
        """Get the node at a given pixel

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)

        Returns:
            The PixelNode at the index, or None if a node does not exist
        """
        pixel = get_healpix_pixel(pixel)
        if self.contains(pixel):
            return self.pixels[pixel.order][pixel.pixel]
        return None

    def __getitem__(self, item) -> PixelNode:
        return self.get_node(item)

    def create_node_and_parent_if_not_exist(self, pixel: HealpixInputTypes, node_type: PixelNodeType):
        """Creates a node and adds to `self.pixels` in the tree, and recursively creates parent
        node if parent does not exist

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)
            node_type: Node type of the node to create
        """
        pixel = get_healpix_pixel(pixel)
        if self.contains(pixel):
            raise ValueError("Incorrectly configured catalog: catalog contains duplicate pixels")

        if pixel.order == 0:
            self.create_node(pixel, node_type, self.root_pixel)
            return

        parents_to_add = []
        for delta_order in range(1, pixel.order + 1):
            parent_order = pixel.order - delta_order
            parent_pixel = pixel.pixel >> (2 * delta_order)
            if not self.contains((parent_order, parent_pixel)):
                parents_to_add.insert(0, (parent_order, parent_pixel))
            else:
                break

        for add_order, add_pixel in parents_to_add:
            parent_order = add_order - 1
            parent_pixel = add_pixel >> 2 if add_order > 0 else -1
            self.create_node(
                (add_order, add_pixel), PixelNodeType.INNER, self.pixels[parent_order][parent_pixel]
            )
        parent_order = pixel.order - 1
        parent_pixel = pixel.pixel >> 2 if pixel.order > 0 else -1

        parent = self.pixels[parent_order][parent_pixel]

        if parent.node_type != PixelNodeType.INNER:
            raise ValueError(
                "Incorrectly configured catalog: catalog contains pixels defined at multiple orders"
            )

        self.create_node(pixel, node_type, parent)

    def create_node(
        self,
        pixel: HealpixInputTypes,
        node_type: PixelNodeType,
        parent: PixelNode = None,
        replace_existing_node=False,
    ):
        """Create a node and add to `self.pixels` in the tree

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)
            node_type: Node type of the node to create
            parent: (Default: None) Parent node of the node to create. If None, will get parent from
                existing node in tree at correct position based on pixel
            replace_existing_node: (Default: False) If True and node at `pixel` already exists,
                the existing node will be removed and replaced with the new node.
        """
        pixel = get_healpix_pixel(pixel)
        if parent is None:
            if pixel.order == 0:
                parent = self.root_pixel
            else:
                parent_pixel = pixel.convert_to_lower_order(delta_order=1)
                if parent_pixel not in self:
                    raise ValueError(
                        f"Cannot create node at {str(pixel)}, "
                        f"no parent node exists at {str(parent_pixel)}"
                    )
                parent = self[parent_pixel]
        if parent.node_type == PixelNodeType.LEAF:
            raise ValueError(
                f"Cannot create node at {str(pixel)}, "
                f"parent node at {str(parent.pixel)} has node type leaf"
            )
        node_to_replace = None
        if pixel in self:
            if not replace_existing_node:
                raise ValueError(f"Cannot create node at {str(pixel)}, node already exists")
            node_to_replace = self[pixel]
            parent.remove_child_link(node_to_replace)
        node = PixelNode(pixel, node_type, parent)
        if pixel.order not in self.pixels:
            self.pixels[pixel.order] = {}
        self.pixels[pixel.order][pixel.pixel] = node
        if node_to_replace is not None:
            if node.node_type != PixelNodeType.LEAF:
                for child in node_to_replace.children:
                    child.parent = node
                    node.add_child_node(child)
            else:
                for child in node_to_replace.children:
                    self._remove_node_and_children_from_tree(child.pixel)

    def remove_node(self, pixel: HealpixInputTypes):
        """Remove node in tree

        Removes a node at a specified pixel in the tree. Raises a `ValueError` if no node at
        specified pixel.

        Args:
            pixel: HEALPix pixel to remove the node at

        Raises:
            ValueError: No node in tree at pixel
        """
        pixel = get_healpix_pixel(pixel)
        if pixel not in self:
            raise ValueError(f"No node at pixel {str(pixel)}")
        node = self[pixel]
        node.parent.remove_child_link(node)
        self._remove_node_and_children_from_tree(pixel)

    def _remove_node_and_children_from_tree(self, pixel: HealpixPixel):
        node = self.pixels[pixel.order].pop(pixel.pixel)
        if len(self.pixels[pixel.order]) == 0:
            self.pixels.pop(pixel.order)
        for child_node in node.children:
            self._remove_node_and_children_from_tree(child_node.pixel)

    def add_all_descendants_from_node(self, node: PixelNode):
        """Adds all descendents from a given node to the current tree

        Used to make the current tree being built mirror the subtree from the specified node in
        another tree.

        A node at the specified position must exist in the current tree with the correct node type.

        Args:
            node: The node from another tree to match

        Raises:
            ValueError: No node exists in the current tree at the same location as the specified
            node
        """
        if node.pixel not in self:
            raise ValueError("No node in tree matching given node")
        nodes_to_add = list(node.children)
        while len(nodes_to_add) > 0:
            node = nodes_to_add.pop(0)
            nodes_to_add += node.children
            self.create_node(node.pixel, node.node_type)

    def split_leaf_to_match_partitioning(self, node_to_match: PixelNode):
        """Split a given leaf node into higher order nodes to match another node's partitioning

        Args:
            node_to_match: The node in another tree to match the partitioning of

        Raises:
            ValueError if no node in tree at the same position as node_to_match,
             or node in tree isn't a leaf node.
        """
        if node_to_match.pixel not in self:
            raise ValueError("No node in tree matching given node")
        if self[node_to_match.pixel].node_type != PixelNodeType.LEAF:
            raise ValueError("Node in tree is not a leaf node")
        nodes_to_add = list(node_to_match.children)
        while len(nodes_to_add) > 0:
            node = nodes_to_add.pop(0)
            nodes_to_add += node.children
            parent_node = self[node.parent.pixel]
            if parent_node.node_type == PixelNodeType.LEAF:
                parent_node.node_type = PixelNodeType.INNER
                for child_pixel in parent_node.pixel.convert_to_higher_order(delta_order=1):
                    self.create_node(child_pixel, PixelNodeType.LEAF, parent=parent_node)
