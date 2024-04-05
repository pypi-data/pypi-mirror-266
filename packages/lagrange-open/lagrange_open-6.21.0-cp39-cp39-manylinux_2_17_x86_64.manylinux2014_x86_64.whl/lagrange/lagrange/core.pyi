from typing import Any, Optional, overload, Typing, Sequence
from enum import Enum
import lagrange.core

class Attribute:
    """
    Mesh attribute
    """

    def __init__(*args, **kwargs):
        """
        Initialize self.  See help(type(self)) for accurate signature.
        """
        ...
    
    def clear(self) -> None:
        """
        Clear the attribute so it has no elements.
        """
        ...
    
    @property
    def copy_policy(self) -> lagrange.core.AttributeCopyPolicy:
        """
        Copy policy of the attribute.
        """
        ...
    @copy_policy.setter
    def copy_policy(self, arg: lagrange.core.AttributeCopyPolicy, /) -> None:
        """
        Copy policy of the attribute.
        """
        ...
    
    def create_internal_copy(self) -> None:
        """
        Create an internal copy of the attribute.
        """
        ...
    
    @property
    def data(self) -> object:
        """
        Raw data buffer of the attribute.
        """
        ...
    @data.setter
    def data(self, arg: object, /) -> None:
        """
        Raw data buffer of the attribute.
        """
        ...
    
    @property
    def default_value(self) -> object:
        """
        Default value of the attribute.
        """
        ...
    @default_value.setter
    def default_value(self, arg: float, /) -> None:
        """
        Default value of the attribute.
        """
        ...
    
    @property
    def dtype(self) -> Optional[type]:
        """
        Value type of the attribute.
        """
        ...
    
    @property
    def element_type(self) -> lagrange.core.AttributeElement:
        """
        Element type of the attribute.
        """
        ...
    
    def empty(self) -> bool:
        """
        Return true if the attribute is empty.
        """
        ...
    
    @property
    def external(self) -> bool:
        """
        Return true if the attribute wraps external buffer.
        """
        ...
    
    @property
    def growth_policy(self) -> lagrange.core.AttributeGrowthPolicy:
        """
        Growth policy of the attribute.
        """
        ...
    @growth_policy.setter
    def growth_policy(self, arg: lagrange.core.AttributeGrowthPolicy, /) -> None:
        """
        Growth policy of the attribute.
        """
        ...
    
    def insert_elements(self, tensor: object) -> None:
        """
        Insert new elements to the attribute.
        
        :param tensor: A tensor with shape (num_elements, num_channels) or (num_elements,).
        """
        ...
    
    @overload
    def insert_elements(self, num_elements: int) -> None:
        """
        Insert new elements with default value to the attribute.
        
        :param num_elements: Number of elements to insert.
        """
        ...
    
    @property
    def num_channels(self) -> int:
        """
        Number of channels in the attribute.
        """
        ...
    
    @property
    def num_elements(self) -> int:
        """
        Number of elements in the attribute.
        """
        ...
    
    @property
    def readonly(self) -> bool:
        """
        Return true if the attribute is read-only.
        """
        ...
    
    def reserve_entries(self, num_entries: int) -> None:
        """
        Reserve enough memory for `num_entries` entries.
        
        :param num_entries: Number of entries to reserve. It does not need to be a multiple of `num_channels`.
        """
        ...
    
    @property
    def shrink_policy(self) -> lagrange.core.AttributeShrinkPolicy:
        """
        Shrink policy of the attribute.
        """
        ...
    @shrink_policy.setter
    def shrink_policy(self, arg: lagrange.core.AttributeShrinkPolicy, /) -> None:
        """
        Shrink policy of the attribute.
        """
        ...
    
    @property
    def usage(self) -> lagrange.core.AttributeUsage:
        """
        Usage of the attribute.
        """
        ...
    
    @property
    def write_policy(self) -> lagrange.core.AttributeWritePolicy:
        """
        Write policy of the attribute.
        """
        ...
    @write_policy.setter
    def write_policy(self, arg: lagrange.core.AttributeWritePolicy, /) -> None:
        """
        Write policy of the attribute.
        """
        ...
    
class AttributeCopyPolicy(Enum):
    """
    <attribute '__doc__' of 'AttributeCopyPolicy' objects>
    """

    CopyIfExternal: Any
    
    ErrorIfExternal: Any
    
    KeepExternalPtr: Any
    
class AttributeCreatePolicy(Enum):
    """
    <attribute '__doc__' of 'AttributeCreatePolicy' objects>
    """

    ErrorIfReserved: Any
    
    Force: Any
    
class AttributeDeletePolicy(Enum):
    """
    <attribute '__doc__' of 'AttributeDeletePolicy' objects>
    """

    ErrorIfReserved: Any
    
    Force: Any
    
class AttributeElement(Enum):
    """
    <attribute '__doc__' of 'AttributeElement' objects>
    """

    Corner: Any
    
    Edge: Any
    
    Facet: Any
    
    Indexed: Any
    
    Value: Any
    
    Vertex: Any
    
class AttributeExportPolicy(Enum):
    """
    <attribute '__doc__' of 'AttributeExportPolicy' objects>
    """

    CopyIfExternal: Any
    
    CopyIfUnmanaged: Any
    
    ErrorIfExternal: Any
    
    KeepExternalPtr: Any
    
class AttributeGrowthPolicy(Enum):
    """
    <attribute '__doc__' of 'AttributeGrowthPolicy' objects>
    """

    AllowWithinCapacity: Any
    
    ErrorIfExtenal: Any
    
    SilentCopy: Any
    
    WarnAndCopy: Any
    
class AttributeShrinkPolicy(Enum):
    """
    <attribute '__doc__' of 'AttributeShrinkPolicy' objects>
    """

    ErrorIfExternal: Any
    
    IgnoreIfExternal: Any
    
    SilentCopy: Any
    
    WarnAndCopy: Any
    
class AttributeUsage(Enum):
    """
    <attribute '__doc__' of 'AttributeUsage' objects>
    """

    Bitangent: Any
    
    Color: Any
    
    CornerIndex: Any
    
    EdgeIndex: Any
    
    FacetIndex: Any
    
    Normal: Any
    
    Position: Any
    
    Scalar: Any
    
    Tangent: Any
    
    UV: Any
    
    Vector: Any
    
    VertexIndex: Any
    
class AttributeWritePolicy(Enum):
    """
    <attribute '__doc__' of 'AttributeWritePolicy' objects>
    """

    ErrorIfReadOnly: Any
    
    SilentCopy: Any
    
    WarnAndCopy: Any
    
class CentroidWeightingType(Enum):
    """
    <attribute '__doc__' of 'CentroidWeightingType' objects>
    """

    Area: Any
    
    Uniform: Any
    
class ConnectivityType(Enum):
    """
    <attribute '__doc__' of 'ConnectivityType' objects>
    """

    Edge: Any
    
    Vertex: Any
    
class DistortionMetric(Enum):
    """
    <attribute '__doc__' of 'DistortionMetric' objects>
    """

    AreaRatio: Any
    
    Dirichlet: Any
    
    InverseDirichlet: Any
    
    MIPS: Any
    
    SymmetricDirichlet: Any
    
class FacetAreaOptions:
    """
    Options for computing facet area.
    """

    def __init__(self) -> None:
        ...
    
    @property
    def output_attribute_name(self) -> str:
        """
        The name of the output attribute.
        """
        ...
    @output_attribute_name.setter
    def output_attribute_name(self, arg: str, /) -> None:
        """
        The name of the output attribute.
        """
        ...
    
class FacetCentroidOptions:
    """
    Facet centroid options.
    """

    def __init__(self) -> None:
        ...
    
    @property
    def output_attribute_name(self) -> str:
        """
        The name of the output attribute.
        """
        ...
    @output_attribute_name.setter
    def output_attribute_name(self, arg: str, /) -> None:
        """
        The name of the output attribute.
        """
        ...
    
class FacetNormalOptions:
    """
    Facet normal computation options.
    """

    def __init__(self) -> None:
        ...
    
    @property
    def output_attribute_name(self) -> str:
        """
        Output attribute name. Default: '@facet_normal'
        """
        ...
    @output_attribute_name.setter
    def output_attribute_name(self, arg: str, /) -> None:
        """
        Output attribute name. Default: '@facet_normal'
        """
        ...
    
class IndexedAttribute:
    """
    None
    """

    def __init__(*args, **kwargs):
        """
        Initialize self.  See help(type(self)) for accurate signature.
        """
        ...
    
    @property
    def element_type(self) -> lagrange.core.AttributeElement:
        ...
    
    @property
    def indices(self) -> lagrange.core.Attribute:
        ...
    
    @property
    def num_channels(self) -> int:
        ...
    
    @property
    def usage(self) -> lagrange.core.AttributeUsage:
        ...
    
    @property
    def values(self) -> lagrange.core.Attribute:
        ...
    
class MappingPolicy(Enum):
    """
    <attribute '__doc__' of 'MappingPolicy' objects>
    """

    Average: Any
    
    Error: Any
    
    KeepFirst: Any
    
class MeshAreaOptions:
    """
    Options for computing mesh area.
    """

    def __init__(self) -> None:
        ...
    
    @property
    def input_attribute_name(self) -> str:
        """
        The name of the pre-computed facet area attribute, default is '@facet_area'.
        """
        ...
    @input_attribute_name.setter
    def input_attribute_name(self, arg: str, /) -> None:
        """
        The name of the pre-computed facet area attribute, default is '@facet_area'.
        """
        ...
    
    @property
    def use_signed_area(self) -> bool:
        """
        Whether to use signed area.
        """
        ...
    @use_signed_area.setter
    def use_signed_area(self, arg: bool, /) -> None:
        """
        Whether to use signed area.
        """
        ...
    
class MeshCentroidOptions:
    """
    Mesh centroid options.
    """

    def __init__(self) -> None:
        ...
    
    @property
    def facet_area_attribute_name(self) -> str:
        """
        The name of the pre-computed facet area attribute if available.
        """
        ...
    @facet_area_attribute_name.setter
    def facet_area_attribute_name(self, arg: str, /) -> None:
        """
        The name of the pre-computed facet area attribute if available.
        """
        ...
    
    @property
    def facet_centroid_attribute_name(self) -> str:
        """
        The name of the pre-computed facet centroid attribute if available.
        """
        ...
    @facet_centroid_attribute_name.setter
    def facet_centroid_attribute_name(self, arg: str, /) -> None:
        """
        The name of the pre-computed facet centroid attribute if available.
        """
        ...
    
    @property
    def weighting_type(self) -> lagrange.core.CentroidWeightingType:
        """
        The weighting type.
        """
        ...
    @weighting_type.setter
    def weighting_type(self, arg: lagrange.core.CentroidWeightingType, /) -> None:
        """
        The weighting type.
        """
        ...
    
class NormalOptions:
    """
    Normal computation options.
    """

    def __init__(self) -> None:
        ...
    
    @property
    def facet_normal_attribute_name(self) -> str:
        """
        Facet normal attribute name to use. Default is '@facet_normal'.
        """
        ...
    @facet_normal_attribute_name.setter
    def facet_normal_attribute_name(self, arg: str, /) -> None:
        """
        Facet normal attribute name to use. Default is '@facet_normal'.
        """
        ...
    
    @property
    def keep_facet_normals(self) -> bool:
        """
        Whether to keep the computed facet normal attribute. Default is false.
        """
        ...
    @keep_facet_normals.setter
    def keep_facet_normals(self, arg: bool, /) -> None:
        """
        Whether to keep the computed facet normal attribute. Default is false.
        """
        ...
    
    @property
    def output_attribute_name(self) -> str:
        """
        Output attribute name. Default: '@normal'
        """
        ...
    @output_attribute_name.setter
    def output_attribute_name(self, arg: str, /) -> None:
        """
        Output attribute name. Default: '@normal'
        """
        ...
    
    @property
    def recompute_facet_normals(self) -> bool:
        """
        Whether to recompute facet normals. Default is false.
        """
        ...
    @recompute_facet_normals.setter
    def recompute_facet_normals(self, arg: bool, /) -> None:
        """
        Whether to recompute facet normals. Default is false.
        """
        ...
    
    @property
    def weight_type(self) -> lagrange.core.NormalWeightingType:
        """
        Weighting type for normal computation. Default is Angle.
        """
        ...
    @weight_type.setter
    def weight_type(self, arg: lagrange.core.NormalWeightingType, /) -> None:
        """
        Weighting type for normal computation. Default is Angle.
        """
        ...
    
class NormalWeightingType(Enum):
    """
    <attribute '__doc__' of 'NormalWeightingType' objects>
    """

    Angle: Any
    
    CornerTriangleArea: Any
    
    Uniform: Any
    
class RemapVerticesOptions:
    """
    Options for remapping vertices.
    """

    def __init__(self) -> None:
        ...
    
    @property
    def collision_policy_float(self) -> lagrange.core.MappingPolicy:
        """
        The collision policy for float attributes.
        """
        ...
    @collision_policy_float.setter
    def collision_policy_float(self, arg: lagrange.core.MappingPolicy, /) -> None:
        """
        The collision policy for float attributes.
        """
        ...
    
    @property
    def collision_policy_integral(self) -> lagrange.core.MappingPolicy:
        """
        The collision policy for integral attributes.
        """
        ...
    @collision_policy_integral.setter
    def collision_policy_integral(self, arg: lagrange.core.MappingPolicy, /) -> None:
        """
        The collision policy for integral attributes.
        """
        ...
    
class SurfaceMesh:
    """
    None
    """

    def __init__(self, dimension: int = 3) -> None:
        ...
    
    def add_hybrid(self, arg0: numpy.typing.NDArray, arg1: numpy.typing.NDArray, /) -> None:
        ...
    
    def add_polygon(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    def add_polygons(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    def add_quad(self, arg0: int, arg1: int, arg2: int, arg3: int, /) -> None:
        ...
    
    def add_quads(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    def add_triangle(self, arg0: int, arg1: int, arg2: int, /) -> None:
        ...
    
    def add_triangles(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    def add_vertex(self, vertex: numpy.typing.NDArray) -> None:
        """
        add_vertex(self, arg: list, /) -> None
        
        Add a vertex to the mesh.
        
        :param vertex: vertex coordinates
        :type vertex: numpy.ndarray or list
        """
        ...
    
    def add_vertices(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def attr_id_corner_to_edge(self) -> int:
        ...
    
    @property
    def attr_id_corner_to_facet(self) -> int:
        ...
    
    @property
    def attr_id_corner_to_vertex(self) -> int:
        ...
    
    @property
    def attr_id_edge_to_first_corner(self) -> int:
        ...
    
    @property
    def attr_id_facet_to_first_corner(self) -> int:
        ...
    
    @property
    def attr_id_next_corner_around_edge(self) -> int:
        ...
    
    @property
    def attr_id_next_corner_around_vertex(self) -> int:
        ...
    
    @property
    def attr_id_vertex_to_first_corner(self) -> int:
        ...
    
    @property
    def attr_id_vertex_to_position(self) -> int:
        ...
    
    attr_name_corner_to_edge: str
    
    attr_name_corner_to_facet: str
    
    attr_name_corner_to_vertex: str
    
    attr_name_edge_to_first_corner: str
    
    attr_name_facet_to_first_corner: str
    
    def attr_name_is_reserved(arg: str, /) -> bool:
        ...
    
    attr_name_next_corner_around_edge: str
    
    attr_name_next_corner_around_vertex: str
    
    attr_name_vertex_to_first_corner: str
    
    attr_name_vertex_to_position: str
    
    def attribute(self, name: str, sharing: bool = True) -> lagrange.core.Attribute:
        """
        Get an attribute by name.
        
        :param name: Name of the attribute.
        :type name: str
        :param sharing: Whether to allow sharing the attribute with other meshes.
        :type sharing: bool
        
        :return: The attribute.
        """
        ...
    
    @overload
    def attribute(self, id: int, sharing: bool = True) -> lagrange.core.Attribute:
        """
        Get an attribute by id.
        
        :param id: Id of the attribute.
        :type id: AttributeId
        :param sharing: Whether to allow sharing the attribute with other meshes.
        :type sharing: bool
        
        :returns: The attribute.
        """
        ...
    
    def clear_edges(self) -> None:
        ...
    
    def clear_facets(self) -> None:
        ...
    
    def clear_vertices(self) -> None:
        ...
    
    def clone(self) -> object:
        """
        Create a deep copy of this mesh.
        """
        ...
    
    def compress_if_regular(self) -> None:
        ...
    
    def count_num_corners_around_edge(self, arg: int, /) -> int:
        ...
    
    def count_num_corners_around_vertex(self, arg: int, /) -> int:
        ...
    
    def create_attribute(self, name: str, element: Optional[lagrange.core.AttributeElement] = None, usage: Optional[lagrange.core.AttributeUsage] = None, initial_values: Optional[Union[numpy.typing.NDArray, list]] = None, initial_indices: Optional[Union[numpy.typing.NDArray, numpy.typing.NDArray, list]] = None, num_channels: Optional[int] = None, dtype: Optional[type] = None) -> int:
        """
        Create an attribute.
        
        :param name: Name of the attribute.
        :type name: str
        :param element: Element type of the attribute. If None, derive from the shape of initial values.
        :type element: AttributeElement, optional
        :param usage: Usage type of the attribute. If None, derive from the shape of initial values or the number of channels.
        :type usage: AttributeUsage, optional
        :param initial_values: Initial values of the attribute.
        :type initial_values: numpy.ndarray, optional
        :param initial_indices: Initial indices of the attribute (Indexed attribute only).
        :type initial_indices: numpy.ndarray, optional
        :param num_channels: Number of channels of the attribute.
        :type num_channels: int, optional
        :param dtype: Data type of the attribute.
        :type dtype: valid numpy.dtype, optional
        
        .. note::
        If `element` is None, it will be derived based on the cardinality of the mesh elements.
        If there is an ambiguity, an exception will be raised.
        In addition, explicit `element` specification is required for value attributes.
        
        .. note::
        If `usage` is None, it will be derived based on the shape of `initial_values` or `num_channels` if specified.
        
        :returns: The id of the created attribute.
        """
        ...
    
    def create_attribute_from(self, name: str, source_mesh: lagrange.core.SurfaceMesh, source_name: str = '') -> int:
        """
        Shallow copy an attribute from another mesh.
        
        :param name: Name of the attribute.
        :type name: str
        :param source_mesh: Source mesh.
        :type source_mesh: SurfaceMesh
        :param source_name: Name of the attribute in the source mesh. If empty, use the same name as `name`.
        :type source_name: str, optional
        
        :returns: The id of the created attribute.
        """
        ...
    
    def delete_attribute(self, name: str) -> None:
        """
        delete_attribute(self, name: str) -> None
        """
        ...
    
    @overload
    def delete_attribute(self, name: str, policy: lagrange.core.AttributeDeletePolicy) -> None:
        """
        delete_attribute(self, name: str, policy: lagrange.core.AttributeDeletePolicy) -> None
        """
        ...
    
    @property
    def dimension(self) -> int:
        ...
    
    def duplicate_attribute(self, arg0: str, arg1: str, /) -> int:
        ...
    
    @property
    def facets(self) -> numpy.typing.NDArray:
        """
        Facets of the mesh.
        """
        ...
    @facets.setter
    def facets(self, arg: numpy.typing.NDArray, /) -> None:
        """
        Facets of the mesh.
        """
        ...
    
    def find_edge_from_vertices(self, arg0: int, arg1: int, /) -> int:
        ...
    
    def get_attribute_id(self, arg: str, /) -> int:
        ...
    
    def get_attribute_name(self, arg: int, /) -> str:
        ...
    
    def get_corner_edge(self, arg: int, /) -> int:
        ...
    
    def get_corner_facet(self, arg: int, /) -> int:
        ...
    
    def get_corner_vertex(self, arg: int, /) -> int:
        ...
    
    def get_edge(self, arg0: int, arg1: int, /) -> int:
        ...
    
    def get_edge_vertices(self, arg: int, /) -> list[int]:
        ...
    
    def get_facet_corner_begin(self, arg: int, /) -> int:
        ...
    
    def get_facet_corner_end(self, arg: int, /) -> int:
        ...
    
    def get_facet_size(self, arg: int, /) -> int:
        ...
    
    def get_facet_vertex(self, arg0: int, arg1: int, /) -> int:
        ...
    
    def get_facet_vertices(self, arg: int, /) -> numpy.typing.NDArray:
        ...
    
    def get_first_corner_around_edge(self, arg: int, /) -> int:
        ...
    
    def get_first_corner_around_vertex(self, arg: int, /) -> int:
        ...
    
    def get_matching_attribute_ids(self, element: Optional[lagrange.core.AttributeElement] = None, usage: Optional[lagrange.core.AttributeUsage] = None, num_channels: int = 0) -> list[int]:
        """
        Get all matching attribute ids with the desired element type, usage and number of channels.
        
        :param element:       The target element type. None matches all element types.
        :param usage:         The target usage type.  None matches all usage types.
        :param num_channels:  The target number of channels. 0 matches arbitrary number of channels.
        
        :returns: A list of attribute ids matching the target element, usage and number of channels.
        """
        ...
    
    def get_next_corner_around_edge(self, arg: int, /) -> int:
        ...
    
    def get_next_corner_around_vertex(self, arg: int, /) -> int:
        ...
    
    def get_one_corner_around_edge(self, arg: int, /) -> int:
        ...
    
    def get_one_corner_around_vertex(self, arg: int, /) -> int:
        ...
    
    def get_one_facet_around_edge(self, arg: int, /) -> int:
        ...
    
    def get_position(self, arg: int, /) -> numpy.typing.NDArray:
        ...
    
    def has_attribute(self, arg: str, /) -> bool:
        ...
    
    @property
    def has_edges(self) -> bool:
        ...
    
    def indexed_attribute(self, name: str, sharing: bool = True) -> lagrange.core.IndexedAttribute:
        """
        Get an indexed attribute by name.
        
        :param name: Name of the attribute.
        :type name: str
        :param sharing: Whether to allow sharing the attribute with other meshes.
        :type sharing: bool
        
        :returns: The indexed attribute.
        """
        ...
    
    @overload
    def indexed_attribute(self, id: int, sharing: bool = True) -> lagrange.core.IndexedAttribute:
        """
        Get an indexed attribute by id.
        
        :param id: Id of the attribute.
        :type id: AttributeId
        :param sharing: Whether to allow sharing the attribute with other meshes.
        :type sharing: bool
        
        :returns: The indexed attribute.
        """
        ...
    
    def initialize_edges(self, edges: Optional[numpy.typing.NDArray] = None) -> None:
        """
        Initialize the edges.
        
        The `edges` tensor provides a predefined ordering of the edges.
        If not provided, the edges are initialized in an arbitrary order.
        
        :param edges: M x 2 tensor of predefined edge vertex indices, where M is the number of edges.
        :type edges: numpy.ndarray, optional
        """
        ...
    
    def is_attribute_indexed(self, arg: str, /) -> bool:
        """
        is_attribute_indexed(self, arg: str, /) -> bool
        """
        ...
    
    @overload
    def is_attribute_indexed(self, arg: int, /) -> bool:
        """
        is_attribute_indexed(self, arg: int, /) -> bool
        """
        ...
    
    def is_boundary_edge(self, arg: int, /) -> bool:
        ...
    
    @property
    def is_hybrid(self) -> bool:
        ...
    
    @property
    def is_quad_mesh(self) -> bool:
        ...
    
    @property
    def is_regular(self) -> bool:
        ...
    
    @property
    def is_triangle_mesh(self) -> bool:
        ...
    
    @property
    def num_corners(self) -> int:
        ...
    
    @property
    def num_edges(self) -> int:
        ...
    
    @property
    def num_facets(self) -> int:
        ...
    
    @property
    def num_vertices(self) -> int:
        ...
    
    def ref_facet_vertices(self, arg: int, /) -> numpy.typing.NDArray:
        ...
    
    def ref_position(self, arg: int, /) -> numpy.typing.NDArray:
        ...
    
    def remove_facets(self, arg: numpy.typing.NDArray, /) -> None:
        """
        remove_facets(self, facets: list) -> None
        
        Remove selected facets from the mesh.
        
        :param facets: list of facet indices to remove
        """
        ...
    
    def remove_vertices(self, arg: numpy.typing.NDArray, /) -> None:
        """
        remove_vertices(self, vertices: list) -> None
        
        Remove selected vertices from the mesh.
        
        :param vertices: list of vertex indices to remove
        """
        ...
    
    def rename_attribute(self, arg0: str, arg1: str, /) -> None:
        ...
    
    def shrink_to_fit(self) -> None:
        ...
    
    @property
    def vertex_per_facet(self) -> int:
        ...
    
    @property
    def vertices(self) -> numpy.typing.NDArray:
        """
        Vertices of the mesh.
        """
        ...
    @vertices.setter
    def vertices(self, arg: numpy.typing.NDArray, /) -> None:
        """
        Vertices of the mesh.
        """
        ...
    
    def wrap_as_attribute(self, name: str, element: lagrange.core.AttributeElement, usage: lagrange.core.AttributeUsage, values: numpy.typing.NDArray) -> int:
        """
        Wrap an existing numpy array as an attribute.
        
        :param name: Name of the attribute.
        :type name: str
        :param element: Element type of the attribute.
        :type element: AttributeElement
        :param usage: Usage type of the attribute.
        :type usage: AttributeUsage
        :param values: Values of the attribute.
        :type values: numpy.ndarray
        
        :returns: The id of the created attribute.
        """
        ...
    
    def wrap_as_facets(self, offsets: numpy.typing.NDArray, num_facets: int, facets: numpy.typing.NDArray, num_corners: int) -> int:
        """
        Wrap a tensor as a list of hybrid facets.
        
        :param offsets: The offset indices into the facets array.
        :type offsets: numpy.ndarray
        :param num_facets: Number of facets.
        :type num_facets: int
        :param facets: The indices of the vertices of the facets.
        :type facets: numpy.ndarray
        :param num_corners: Number of corners.
        :type num_corners: int
        
        :return: The id of the wrapped facet attribute.
        """
        ...
    
    @overload
    def wrap_as_facets(self, tensor: numpy.typing.NDArray, num_facets: int, vertex_per_facet: int) -> int:
        """
        Wrap a tensor as a list of regular facets.
        
        :param tensor: The tensor to wrap.
        :type tensor: numpy.ndarray
        :param num_facets: Number of facets.
        :type num_facets: int
        :param vertex_per_facet: Number of vertices per facet.
        :type vertex_per_facet: int
        
        :return: The id of the wrapped facet attribute.
        """
        ...
    
    def wrap_as_indexed_attribute(self, name: str, usage: lagrange.core.AttributeUsage, values: numpy.typing.NDArray, indices: numpy.typing.NDArray) -> int:
        """
        Wrap an existing numpy array as an indexed attribute.
        
        :param name: Name of the attribute.
        :type name: str
        :param usage: Usage type of the attribute.
        :type usage: AttributeUsage
        :param values: Values of the attribute.
        :type values: numpy.ndarray
        :param indices: Indices of the attribute.
        :type indices: numpy.ndarray
        
        :returns: The id of the created attribute.
        """
        ...
    
    def wrap_as_vertices(self, tensor: numpy.typing.NDArray, num_vertices: int) -> int:
        """
        Wrap a tensor as vertices.
        
        :param tensor: The tensor to wrap.
        :type tensor: numpy.ndarray
        :param num_vertices: Number of vertices.
        :type num_vertices: int
        
        :return: The id of the wrapped vertices attribute.
        """
        ...
    
class TangentBitangentOptions:
    """
    Tangent bitangent options
    """

    def __init__(self) -> None:
        ...
    
    @property
    def bitangent_attribute_name(self) -> str:
        """
        The name of the output bitangent attribute, default is '@bitangent'
        """
        ...
    @bitangent_attribute_name.setter
    def bitangent_attribute_name(self, arg: str, /) -> None:
        """
        The name of the output bitangent attribute, default is '@bitangent'
        """
        ...
    
    @property
    def normal_attribute_name(self) -> str:
        """
        The name of the normal attribute
        """
        ...
    @normal_attribute_name.setter
    def normal_attribute_name(self, arg: str, /) -> None:
        """
        The name of the normal attribute
        """
        ...
    
    @property
    def output_element_type(self) -> lagrange.core.AttributeElement:
        """
        The output element type
        """
        ...
    @output_element_type.setter
    def output_element_type(self, arg: lagrange.core.AttributeElement, /) -> None:
        """
        The output element type
        """
        ...
    
    @property
    def pad_with_sign(self) -> bool:
        """
        Whether to pad the output tangent/bitangent with sign
        """
        ...
    @pad_with_sign.setter
    def pad_with_sign(self, arg: bool, /) -> None:
        """
        Whether to pad the output tangent/bitangent with sign
        """
        ...
    
    @property
    def tangent_attribute_name(self) -> str:
        """
        The name of the output tangent attribute, default is '@tangent'
        """
        ...
    @tangent_attribute_name.setter
    def tangent_attribute_name(self, arg: str, /) -> None:
        """
        The name of the output tangent attribute, default is '@tangent'
        """
        ...
    
    @property
    def uv_attribute_name(self) -> str:
        """
        The name of the uv attribute
        """
        ...
    @uv_attribute_name.setter
    def uv_attribute_name(self, arg: str, /) -> None:
        """
        The name of the uv attribute
        """
        ...
    
class TangentBitangentResult:
    """
    Tangent bitangent result
    """

    def __init__(self) -> None:
        ...
    
    @property
    def bitangent_id(self) -> int:
        """
        The output bitangent attribute id
        """
        ...
    @bitangent_id.setter
    def bitangent_id(self, arg: int, /) -> None:
        """
        The output bitangent attribute id
        """
        ...
    
    @property
    def tangent_id(self) -> int:
        """
        The output tangent attribute id
        """
        ...
    @tangent_id.setter
    def tangent_id(self, arg: int, /) -> None:
        """
        The output tangent attribute id
        """
        ...
    
class VertexNormalOptions:
    """
    Options for computing vertex normals
    """

    def __init__(self) -> None:
        ...
    
    @property
    def keep_weighted_corner_normals(self) -> bool:
        """
        Whether to keep the weighted corner normal attribute. Default is false.
        """
        ...
    @keep_weighted_corner_normals.setter
    def keep_weighted_corner_normals(self, arg: bool, /) -> None:
        """
        Whether to keep the weighted corner normal attribute. Default is false.
        """
        ...
    
    @property
    def output_attribute_name(self) -> str:
        """
        Output attribute name. Default is '@vertex_normal'.
        """
        ...
    @output_attribute_name.setter
    def output_attribute_name(self, arg: str, /) -> None:
        """
        Output attribute name. Default is '@vertex_normal'.
        """
        ...
    
    @property
    def recompute_weighted_corner_normals(self) -> bool:
        """
        Whether to recompute weighted corner normals. Default is false
        """
        ...
    @recompute_weighted_corner_normals.setter
    def recompute_weighted_corner_normals(self, arg: bool, /) -> None:
        """
        Whether to recompute weighted corner normals. Default is false
        """
        ...
    
    @property
    def weight_type(self) -> lagrange.core.NormalWeightingType:
        """
        Weighting type for normal computation. Default is Angle.
        """
        ...
    @weight_type.setter
    def weight_type(self, arg: lagrange.core.NormalWeightingType, /) -> None:
        """
        Weighting type for normal computation. Default is Angle.
        """
        ...
    
    @property
    def weighted_corner_normal_attribute_name(self) -> str:
        """
        Precomputed weighted corner normals attribute name.Default is '@weighted_corner_normal'. If attribute exists, the weighted corner normals will be used instead of recomputing them.
        """
        ...
    @weighted_corner_normal_attribute_name.setter
    def weighted_corner_normal_attribute_name(self, arg: str, /) -> None:
        """
        Precomputed weighted corner normals attribute name.Default is '@weighted_corner_normal'. If attribute exists, the weighted corner normals will be used instead of recomputing them.
        """
        ...
    
class VertexValenceOptions:
    """
    Vertex valence options
    """

    def __init__(self) -> None:
        ...
    
    @property
    def output_attribute_name(self) -> str:
        """
        The name of the output attribute
        """
        ...
    @output_attribute_name.setter
    def output_attribute_name(self, arg: str, /) -> None:
        """
        The name of the output attribute
        """
        ...
    
def cast_attribute(mesh: lagrange.core.SurfaceMesh, input_attribute: Union[int, str], dtype: type, output_attribute_name: Optional[str] = None) -> int:
    """
    Cast an attribute to a new dtype.
    
    :param mesh:            The input mesh.
    :param input_attribute: The input attribute id or name.
    :param dtype:           The new dtype.
    :param output_attribute_name: The output attribute name. If none, cast will replace the input attribute.
    
    :returns: The id of the new attribute.
    """
    ...

def combine_meshes(meshes: list[lagrange.core.SurfaceMesh], preserve_attributes: bool = True) -> lagrange.core.SurfaceMesh:
    """
    Combine a list of meshes into a single mesh.
    
    :param meshes: input meshes
    :type meshes: list[SurfaceMesh]
    :param preserve_attributes: whether to preserve attributes
    :type preserve_attributes: bool
    
    :returns: the combined mesh
    """
    ...

def compute_components(mesh: lagrange.core.SurfaceMesh, output_attribute_name: Optional[str] = None, connectivity_type: Optional[lagrange.core.ConnectivityType] = None, blocker_elements: Optional[list] = None) -> int:
    """
    Compute connected components.
    
    This method will create a per-facet component id attribute named by the `output_attribute_name`
    argument. Each component id is in [0, num_components-1] range.
    
    :param mesh: The input mesh.
    :param output_attribute_name: The name of the output attribute.
    :param connectivity_type: The connectivity type.  Either "Vertex" or "Edge".
    :param blocker_elements: The list of blocker element indices. If `connectivity_type` is `Edge`, facets adjacent to a blocker edge are not considered as connected through this edge. If `connectivity_type` is `Vertex`, facets sharing a blocker vertex are not considered as connected through this vertex.
    
    :returns: The total number of components.
    """
    ...

def compute_dihedral_angles(mesh: lagrange.core.SurfaceMesh, output_attribute_name: Optional[str] = None, facet_normal_attribute_name: Optional[str] = None, recompute_facet_normals: Optional[bool] = None, keep_facet_normals: Optional[bool] = None) -> int:
    """
    Compute dihedral angles for each edge.
    
    The dihedral angle of an edge is defined as the angle between the __normals__ of two facets adjacent
    to the edge. The dihedral angle is always in the range [0, pi] for manifold edges. For boundary
    edges, the dihedral angle defaults to 0.  For non-manifold edges, the dihedral angle is not
    well-defined and will be set to the special value 2 * M_PI.
    
    :param mesh:                        The source mesh.
    :param output_attribute_name:       The optional edge attribute name to store the dihedral angles.
    :param facet_normal_attribute_name: The optional attribute name to store the facet normals.
    :param recompute_facet_normals:     Whether to recompute facet normals.
    :param keep_facet_normals:          Whether to keep newly computed facet normals. It has no effect on pre-existing facet normals.
    
    :return: The edge attribute id of dihedral angles.
    """
    ...

def compute_dijkstra_distance(mesh: lagrange.core.SurfaceMesh, seed_facet: int, barycentric_coords: list, radius: Optional[float] = None, output_attribute_name: str = '@dijkstra_distance', output_involved_vertices: bool = False) -> Optional[list[int]]:
    """
    Compute Dijkstra distance from a seed facet.
    
    :param mesh:                  The source mesh.
    :param seed_facet:            The seed facet index.
    :param barycentric_coords:    The barycentric coordinates of the seed facet.
    :param radius:                The maximum radius of the dijkstra distance.
    :param output_attribute_name: The output attribute name to store the dijkstra distance.
    :param output_involved_vertices: Whether to output the list of involved vertices.
    """
    ...

def compute_edge_lengths(mesh: lagrange.core.SurfaceMesh, output_attribute_name: Optional[str] = None) -> int:
    """
    Compute edge lengths.
    
    :param mesh:                  The source mesh.
    :param output_attribute_name: The optional edge attribute name to store the edge lengths.
    
    :return: The edge attribute id of edge lengths.
    """
    ...

def compute_euler(mesh: lagrange.core.SurfaceMesh) -> int:
    """
    Compute the Euler characteristic.
    
    :param mesh: The source mesh.
    
    :return: The Euler characteristic.
    """
    ...

def compute_facet_area(mesh: lagrange.core.SurfaceMesh, output_attribute_name: Optional[str] = None) -> int:
    """
    Compute facet area (Pythonic API).
    
    :param mesh: The input mesh.
    :param output_attribute_name: The name of the output attribute.
    
    :returns: The id of the new attribute.
    """
    ...

@overload
def compute_facet_area(mesh: lagrange.core.SurfaceMesh, options: lagrange.core.FacetAreaOptions = ...) -> int:
    """
    Compute facet area.
    
    :param mesh: The input mesh.
    :param options: The options for computing facet area.
    
    :returns: The id of the new attribute.
    """
    ...

def compute_facet_centroid(mesh: lagrange.core.SurfaceMesh, output_attribute_name: Optional[str] = None) -> int:
    """
    Compute facet centroid (Pythonic API).
    
    :param mesh: The input mesh.
    :param output_attribute_name: The name of the output attribute.
    
    :returns: The id of the new attribute.
    """
    ...

@overload
def compute_facet_centroid(mesh: lagrange.core.SurfaceMesh, options: lagrange.core.FacetCentroidOptions = ...) -> int:
    """
    Compute facet centroid.
    
    :param mesh: The input mesh.
    :param options: The options for computing facet centroid.
    
    :returns: The id of the new attribute.
    """
    ...

def compute_facet_normal(mesh: lagrange.core.SurfaceMesh, output_attribute_name: Optional[str] = None) -> int:
    """
    Compute facet normal (Pythonic API).
    
    :param mesh: Input mesh.
    :param output_attribute_name: Output attribute name.
    
    :returns: Facet normal attribute id.
    """
    ...

@overload
def compute_facet_normal(mesh: lagrange.core.SurfaceMesh, options: lagrange.core.FacetNormalOptions = ...) -> int:
    """
    Compute facet normal.
    
    :param mesh: Input mesh.
    :param options: Options for computing facet normals.
    
    :returns: Facet normal attribute id.
    """
    ...

def compute_greedy_coloring(mesh: lagrange.core.SurfaceMesh, element_type: lagrange.core.AttributeElement = lagrange.core.AttributeElement.Facet, num_color_used: int = 8, output_attribute_name: Optional[str] = None) -> int:
    """
    Compute greedy coloring of mesh elements.
    
    :param mesh: Input mesh.
    :param element_type: Element type to be colored. Can be either Vertex or Facet.
    :param num_color_used: Minimum number of colors to use. The algorithm will cycle through them but may use more.
    :param output_attribute_name: Output attribute name.
    
    :returns: Color attribute id.
    """
    ...

def compute_mesh_area(mesh: lagrange.core.SurfaceMesh, input_attribute_name: Optional[str] = None, use_signed_area: Optional[bool] = None) -> float:
    """
    Compute mesh area (Pythonic API).
    
    :param mesh: The input mesh.
    :param input_attribute_name: The name of the pre-computed facet area attribute.
    :param use_signed_area: Whether to use signed area.
    
    :returns: The mesh area.
    """
    ...

@overload
def compute_mesh_area(mesh: lagrange.core.SurfaceMesh, options: lagrange.core.MeshAreaOptions = ...) -> float:
    """
    Compute mesh area.
    
    :param mesh: The input mesh.
    :param options: The options for computing mesh area.
    
    :returns: The mesh area.
    """
    ...

def compute_mesh_centroid(mesh: lagrange.core.SurfaceMesh, weighting_type: Optional[lagrange.core.CentroidWeightingType] = None, facet_centroid_attribute_name: Optional[str] = None, facet_area_attribute_name: Optional[str] = None) -> list[float]:
    """
    Compute mesh centroid (Pythonic API).
    
    :param mesh: The input mesh.
    :param weighting_type: The weighting type. Default is `Area`.
    :param facet_centroid_attribute_name: The name of the pre-computed facet centroid attribute if available. Default is '@facet_centroid'.
    :param facet_area_attribute_name: The name of the pre-computed facet area attribute if available. Default is '@facet_area'.
    
    :returns: The mesh centroid.
    """
    ...

@overload
def compute_mesh_centroid(mesh: lagrange.core.SurfaceMesh, options: lagrange.core.MeshCentroidOptions = ...) -> list[float]:
    """
    Compute mesh centroid.
    
    :param mesh: The input mesh.
    :param options: The options for computing mesh centroid.
    
    :returns: The mesh centroid.
    """
    ...

def compute_normal(mesh: lagrange.core.SurfaceMesh, feature_angle_threshold: float = 0.7853981633974483, cone_vertices: Optional[object] = None, output_attribute_name: Optional[str] = None, weight_type: Optional[lagrange.core.NormalWeightingType] = None, facet_normal_attribute_name: Optional[str] = None, recompute_facet_normals: Optional[bool] = None, keep_facet_normals: Optional[bool] = None) -> int:
    """
    Compute indexed normal attribute (Pythonic API).
    
    :param mesh: input mesh
    :type mesh: SurfaceMesh
    :param feature_angle_threshold: feature angle threshold
    :type feature_angle_threshold: float, optional
    :param cone_vertices: cone vertices
    :type cone_vertices: list[int] or numpy.ndarray, optional
    :param output_attribute_name: output normal attribute name
    :type output_attribute_name: str, optional
    :param weight_type: normal weighting type
    :type weight_type: NormalWeightingType, optional
    :param facet_normal_attribute_name: facet normal attribute name
    :type facet_normal_attribute_name: str, optional
    :param recompute_facet_normals: whether to recompute facet normals
    :type recompute_facet_normals: bool, optional
    :param keep_facet_normals: whether to keep the computed facet normal attribute
    :type keep_facet_normals: bool, optional
    
    :returns: the id of the indexed normal attribute.
    """
    ...

@overload
def compute_normal(mesh: lagrange.core.SurfaceMesh, feature_angle_threshold: float = 0.7853981633974483, cone_vertices: Optional[object] = None, options: Optional[lagrange.core.NormalOptions] = None) -> int:
    """
    Compute indexed normal attribute.
    
    Edge with dihedral angles larger than `feature_angle_threshold` are considered as sharp edges.
    Vertices listed in `cone_vertices` are considered as cone vertices, which is always sharp.
    
    :param mesh: input mesh
    :type mesh: SurfaceMesh
    :param feature_angle_threshold: feature angle threshold
    :type feature_angle_threshold: float, optional
    :param cone_vertices: cone vertices
    :type cone_vertices: list[int] or numpy.ndarray, optional
    :param options: normal options
    :type optional: NormalOptions, optional
    
    :returns: the id of the indexed normal attribute.
    """
    ...

def compute_seam_edges(mesh: lagrange.core.SurfaceMesh, indexed_attribute_id: int, output_attribute_name: Optional[str] = None) -> int:
    """
    Computer seam edges for a given indexed attribute.
    
    :param mesh: Input mesh.
    :param indexed_attribute_id: Input indexed attribute id.
    :param output_attribute_name: Output attribute name.
    
    :returns: Attribute id for the output per-edge seam attribute (1 is a seam, 0 is not).
    """
    ...

def compute_tangent_bitangent(mesh: lagrange.core.SurfaceMesh, tangent_attribute_name: Optional[str] = None, bitangent_attribute_name: Optional[str] = None, uv_attribute_name: Optional[str] = None, normal_attribute_name: Optional[str] = None, output_attribute_type: Optional[lagrange.core.AttributeElement] = None, pad_with_sign: Optional[bool] = None) -> tuple[int, int]:
    """
    Compute tangent and bitangent vector attributes (Pythonic API).
    
    :param mesh: The input mesh.
    :param tangent_attribute_name: The name of the output tangent attribute.
    :param bitangent_attribute_name: The name of the output bitangent attribute.
    :param uv_attribute_name: The name of the uv attribute.
    :param normal_attribute_name: The name of the normal attribute.
    :param output_attribute_type: The output element type.
    :param pad_with_sign: Whether to pad the output tangent/bitangent with sign.
    
    :returns: The tangent and bitangent attribute ids
    """
    ...

@overload
def compute_tangent_bitangent(mesh: lagrange.core.SurfaceMesh, options: lagrange.core.TangentBitangentOptions = ...) -> lagrange.core.TangentBitangentResult:
    """
    Compute tangent and bitangent vector attributes.
    
    :param mesh: The input mesh.
    :param options: The tangent bitangent options.
    
    :returns: The tangent and bitangent attribute ids
    """
    ...

def compute_uv_distortion(mesh: lagrange.core.SurfaceMesh, uv_attribute_name: str = '@uv', output_attribute_name: str = '@uv_measure', metric: lagrange.core.DistortionMetric = lagrange.core.DistortionMetric.MIPS) -> int:
    """
    Compute UV distortion.
    
    :param mesh:                  The source mesh.
    :param uv_attribute_name:     The input UV attribute name. Default is "@uv".
    :param output_attribute_name: The output attribute name to store the distortion. Default is "@uv_measure".
    :param metric:                The distortion metric. Default is MIPS.
    
    :return: The facet attribute id for distortion.
    """
    ...

def compute_vertex_normal(mesh: lagrange.core.SurfaceMesh, output_attribute_name: Optional[str] = None, weight_type: Optional[lagrange.core.NormalWeightingType] = None, weighted_corner_normal_attribute_name: Optional[str] = None, recompute_weighted_corner_normals: Optional[bool] = None, keep_weighted_corner_normals: Optional[bool] = None) -> int:
    """
    Computer vertex normal (Pythonic API).
    
    :param mesh: Input mesh.
    :param output_attribute_name: Output attribute name.
    :param weight_type: Weighting type for normal computation.
    :param weighted_corner_normal_attribute_name: Precomputed weighted corner normals attribute name.
    :param recompute_weighted_corner_normals: Whether to recompute weighted corner normals.
    :param keep_weighted_corner_normals: Whether to keep the weighted corner normal attribute.
    
    :returns: Vertex normal attribute id.
    """
    ...

@overload
def compute_vertex_normal(mesh: lagrange.core.SurfaceMesh, options: lagrange.core.VertexNormalOptions = ...) -> int:
    """
    Computer vertex normal.
    
    :param mesh: Input mesh.
    :param options: Options for computing vertex normals.
    
    :returns: Vertex normal attribute id.
    """
    ...

def compute_vertex_valence(mesh: lagrange.core.SurfaceMesh, output_attribute_name: Optional[str] = None) -> int:
    """
    Compute vertex valence);
    
    :param mesh: The input mesh.
    :param output_attribute_name: The name of the output attribute.
    
    :returns: The vertex valence attribute id
    """
    ...

@overload
def compute_vertex_valence(mesh: lagrange.core.SurfaceMesh, options: lagrange.core.VertexValenceOptions = ...) -> int:
    """
    Compute vertex valence
    
    :param mesh: The input mesh.
    :param options: The vertex valence options.
    
    :returns: The vertex valence attribute id.
    """
    ...

def detect_degenerate_facets(mesh: lagrange.core.SurfaceMesh) -> list[int]:
    """
    Detect degenerate facets in a mesh.
    
    .. note:
    Only __exaxtly__ degenerate facets are detected.
    
    :param mesh: The input mesh.
    
    :returns: A list of indices of degenerate facets.
    """
    ...

def extract_submesh(mesh: lagrange.core.SurfaceMesh, selected_facets: numpy.typing.NDArray, source_vertex_attr_name: str = '', source_facet_attr_name: str = '', map_attributes: bool = False) -> lagrange.core.SurfaceMesh:
    """
    Extract a submesh based on the selected facets.
    
    :param mesh:                    The source mesh.
    :param selected_facets:         A listed of facet ids to extract.
    :param source_vertex_attr_name: The optional attribute name to track source vertices.
    :param source_facet_attr_name:  The optional attribute name to track source facets.
    :param map_attributes:          Map attributes from the source to target meshes.
    
    :returns: A mesh that contains only the selected facets.
    """
    ...

def filter_attributes(mesh: lagrange.core.SurfaceMesh, included_attributes: Optional[list[Union[int, str]]] = None, excluded_attributes: Optional[list[Union[int, str]]] = None, included_usages: Optional[set[lagrange.core.AttributeUsage]] = None, included_element_types: Optional[set[lagrange.core.AttributeElement]] = None) -> lagrange.core.SurfaceMesh:
    """
    Filters the attributes of mesh according to user specifications.
    
    :param mesh: Input mesh.
    :param included_attributes: List of attribute names or ids to include. By default, all attributes are included.
    :param excluded_attributes: List of attribute names or ids to exclude. By default, no attribute is excluded.
    :param included_usages: List of attribute usages to include. By default, all usages are included.
    :param included_element_types: List of attribute element types to include. By default, all element types are included.
    """
    ...

invalid_index: int

invalid_scalar: float

def is_edge_manifold(mesh: lagrange.core.SurfaceMesh) -> bool:
    """
    Check if the mesh is edge manifold.
    
    :param mesh: The source mesh.
    
    :return: Whether the mesh is edge manifold.
    """
    ...

def is_manifold(mesh: lagrange.core.SurfaceMesh) -> bool:
    """
    Check if the mesh is manifold.
    
    A mesh considered as manifold if it is both vertex and edge manifold.
    
    :param mesh: The source mesh.
    
    :return: Whether the mesh is manifold.
    """
    ...

def is_vertex_manifold(mesh: lagrange.core.SurfaceMesh) -> bool:
    """
    Check if the mesh is vertex manifold.
    
    :param mesh: The source mesh.
    
    :return: Whether the mesh is vertex manifold.
    """
    ...

def map_attribute(mesh: lagrange.core.SurfaceMesh, old_attribute_name: str, new_attribute_name: str, new_element: lagrange.core.AttributeElement) -> int:
    """
    Map an attribute to a new element type.
    
    :param mesh: The input mesh.
    :param old_attribute_name: The name of the input attribute.
    :param new_attribute_name: The name of the new attribute.
    :param new_element: The new element type.
    
    :returns: The id of the new attribute.
    """
    ...

@overload
def map_attribute(mesh: lagrange.core.SurfaceMesh, old_attribute_id: int, new_attribute_name: str, new_element: lagrange.core.AttributeElement) -> int:
    """
    Map an attribute to a new element type.
    
    :param mesh: The input mesh.
    :param old_attribute_id: The id of the input attribute.
    :param new_attribute_name: The name of the new attribute.
    :param new_element: The new element type.
    
    :returns: The id of the new attribute.
    """
    ...

def map_attribute_in_place(mesh: lagrange.core.SurfaceMesh, name: str, new_element: lagrange.core.AttributeElement) -> int:
    """
    Map an attribute to a new element type in place.
    
    :param mesh: The input mesh.
    :param name: The name of the input attribute.
    :param new_element: The new element type.
    
    :returns: The id of the new attribute.
    """
    ...

@overload
def map_attribute_in_place(mesh: lagrange.core.SurfaceMesh, id: int, new_element: lagrange.core.AttributeElement) -> int:
    """
    Map an attribute to a new element type in place.
    
    :param mesh: The input mesh.
    :param id: The id of the input attribute.
    :param new_element: The new element type.
    
    :returns: The id of the new attribute.
    """
    ...

def normalize_mesh(mesh: lagrange.core.SurfaceMesh) -> None:
    """
    Normalize a mesh to fit into a unit box centered at the origin.
    
    :param mesh: input mesh
    """
    ...

def normalize_meshes(meshes: list[lagrange.core.SurfaceMesh]) -> None:
    """
    Normalize a list of meshes to fit into a unit box centered at the origin.
    
    :param meshes: input meshes
    """
    ...

def permute_facets(mesh: lagrange.core.SurfaceMesh, new_to_old: numpy.typing.NDArray) -> None:
    """
    Reorder facets of a mesh in place based on a permutation.
    
    :param mesh: input mesh
    :param new_to_old: permutation vector for facets
    """
    ...

def permute_vertices(mesh: lagrange.core.SurfaceMesh, new_to_old: numpy.typing.NDArray) -> None:
    """
    Reorder vertices of a mesh in place based on a permutation.
    
    :param mesh: input mesh
    :param new_to_old: permutation vector for vertices
    """
    ...

def remap_vertices(mesh: lagrange.core.SurfaceMesh, old_to_new: numpy.typing.NDArray, collision_policy_float: Optional[lagrange.core.MappingPolicy] = None, collision_policy_integral: Optional[lagrange.core.MappingPolicy] = None) -> None:
    """
    Remap vertices of a mesh in place based on a permutation (Pythonic API).
    
    :param mesh: input mesh
    :param old_to_new: permutation vector for vertices
    :param collision_policy_float: The collision policy for float attributes.
    :param collision_policy_integral: The collision policy for integral attributes.
    """
    ...

@overload
def remap_vertices(mesh: lagrange.core.SurfaceMesh, old_to_new: numpy.typing.NDArray, options: lagrange.core.RemapVerticesOptions = ...) -> None:
    """
    Remap vertices of a mesh in place based on a permutation.
    
    :param mesh: input mesh
    :param old_to_new: permutation vector for vertices
    :param options: options for remapping vertices
    """
    ...

def remove_duplicate_facets(mesh: lagrange.core.SurfaceMesh, consider_orientation: bool = False) -> None:
    """
    Remove duplicate facets from a mesh.
    
    Facets of different orientations (e.g. (0, 1, 2) and (2, 1, 0)) are considered as duplicates.
    If both orientations have equal number of duplicate facets, all of them are removed.
    If one orientation has more duplicate facets, all but one facet with the majority orientation are removed.
    
    :param mesh: The input mesh. The mesh is modified in place.
    :param consider_orientation: Whether to consider orientation when detecting duplicate facets.
    """
    ...

def remove_duplicate_vertices(mesh: lagrange.core.SurfaceMesh, extra_attributes: Optional[list[int]] = None) -> None:
    """
    Remove duplicate vertices from a mesh.
    
    :param mesh:             The input mesh.
    :param extra_attributes: Two vertices are considered duplicates if they have the same position and the same values for all attributes in `extra_attributes`.
    """
    ...

def remove_isolated_vertices(mesh: lagrange.core.SurfaceMesh) -> None:
    """
    Remove isolated vertices from a mesh.
    
    .. note:
    A vertex is considered isolated if it is not referenced by any facet.
    
    :param mesh: The input mesh for inplace modification.
    """
    ...

def remove_null_area_facets(mesh: lagrange.core.SurfaceMesh, null_area_threshold: float = 0, remove_isolated_vertices: bool = False) -> None:
    """
    Remove facets with unsigned facets area <= `null_area_threhsold`.
    
    :param mesh:                     The input mesh.
    :param null_area_threshold:      The area threshold below which a facet is considered as null facet.
    :param remove_isolated_vertices: Whether to remove isolated vertices after removing null area facets.
    """
    ...

def remove_topologically_degenerate_facets(mesh: lagrange.core.SurfaceMesh) -> None:
    """
    Remove topologically degenerate facets such as (0, 1, 1)
    
    For general polygons, topologically degeneracy means that the polygon is made of at most two unique
    vertices. E.g. a quad of the form (0, 0, 1, 1) is degenerate, while a quad of the form (1, 1, 2, 3)
    is not.
    
    :param mesh: The input mesh for inplace modification.
    """
    ...

def separate_by_components(mesh: lagrange.core.SurfaceMesh, source_vertex_attr_name: str = '', source_facet_attr_name: str = '', map_attributes: bool = False, connectivity_type: lagrange.core.ConnectivityType = lagrange.core.ConnectivityType.Edge) -> list[lagrange.core.SurfaceMesh]:
    """
    Extract a set of submeshes based on connected components.
    
    :param mesh:                    The source mesh.
    :param source_vertex_attr_name: The optional attribute name to track source vertices.
    :param source_facet_attr_name:  The optional attribute name to track source facets.
    :param map_attributes:          Map attributes from the source to target meshes.
    :param connectivity_type:       The connectivity used for component computation.
    
    :returns: A list of meshes, one for each connected component.
    """
    ...

def separate_by_facet_groups(mesh: lagrange.core.SurfaceMesh, facet_group_indices: numpy.typing.NDArray, source_vertex_attr_name: str = '', source_facet_attr_name: str = '', map_attributes: bool = False) -> list[lagrange.core.SurfaceMesh]:
    """
    Extract a set of submeshes based on facet groups.
    
    :param mesh:                    The source mesh.
    :param facet_group_indices:     The group index for each facet. Each group index must be in the range of [0, max(facet_group_indices)]
    :param source_vertex_attr_name: The optional attribute name to track source vertices.
    :param source_facet_attr_name:  The optional attribute name to track source facets.
    
    :returns: A list of meshes, one for each facet group.
    """
    ...

def transform_mesh(mesh: lagrange.core.SurfaceMesh, affine_transform: numpy.typing.NDArray, normalize_normals: bool = True, normalize_tangents_bitangents: bool = True, in_place: bool = True) -> Optional[lagrange.core.SurfaceMesh]:
    """
    Apply affine transformation to a mesh.
    
    :param mesh:                          The source mesh.
    :param affine_transform:              The affine transformation matrix.
    :param normalize_normals:             Whether to normalize normals.
    :param normalize_tangents_bitangents: Whether to normalize tangents and bitangents.
    :param in_place:                      Whether to apply the transformation in place.
    
    :return: The transformed mesh if in_place is False.
    """
    ...

def triangulate_polygonal_facets(mesh: lagrange.core.SurfaceMesh) -> None:
    """
    Triangulate polygonal facets of the mesh.
    
    :param mesh: The input mesh.
    """
    ...

def unify_index_buffer(mesh: lagrange.core.SurfaceMesh, attribute_names: list[str]) -> lagrange.core.SurfaceMesh:
    """
    Unify the index buffer of the mesh for selected attributes.
    
    :param mesh: The mesh to unify.
    :type mesh: SurfaceMesh
    :param attribute_names: The selected attribute names to unify.
    :type attribute_names: list of str
    
    :returns: The unified mesh.
    """
    ...

@overload
def unify_index_buffer(mesh: lagrange.core.SurfaceMesh) -> lagrange.core.SurfaceMesh:
    """
    Unify the index buffer of the mesh.  All indexed attributes will be unified.
    
    :param mesh: The mesh to unify.
    :type mesh: SurfaceMesh
    
    :returns: The unified mesh.
    """
    ...

@overload
def unify_index_buffer(mesh: lagrange.core.SurfaceMesh, attribute_ids: list[int]) -> lagrange.core.SurfaceMesh:
    """
    Unify the index buffer of the mesh for selected attributes.
    
    :param mesh: The mesh to unify.
    :type mesh: SurfaceMesh
    :param attribute_ids: The selected attribute ids to unify.
    :type attribute_ids: list of int
    
    :returns: The unified mesh.
    """
    ...

def weld_indexed_attribute(mesh: lagrange.core.SurfaceMesh, attribute_id: int) -> None:
    """
    Weld indexed attribute.
    
    :param mesh:         The source mesh.
    :param attribute_id: The indexed attribute id to weld.
    """
    ...

