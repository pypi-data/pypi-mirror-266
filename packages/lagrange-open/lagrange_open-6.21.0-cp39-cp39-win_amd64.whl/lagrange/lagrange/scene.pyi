from typing import Any, Optional, overload, Typing, Sequence
from enum import Enum
import lagrange.scene

class Animation:

    def __init__(self) -> None:
        ...
    
    @property
    def extensions(self) -> lagrange.scene.Extensions:
        ...
    @extensions.setter
    def extensions(self, arg: lagrange.scene.Extensions, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
class AnimationList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.scene.Animation], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.AnimationList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.scene.Animation, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.AnimationList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.scene.Animation, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.scene.Animation:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class BufferList:
    """
    None
    """

    def __init__(self, arg: Iterable[int], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.BufferList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: int, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def count(self, arg: int, /) -> int:
        """
        Return number of occurrences of `arg`.
        """
        ...
    
    def extend(self, arg: lagrange.scene.BufferList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: int, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> int:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
    def remove(self, arg: int, /) -> None:
        """
        Remove first occurrence of `arg`.
        """
        ...
    
class Camera:
    """
    Camera
    """

    class Type(Enum):
        """
        <attribute '__doc__' of 'Type' objects>
        """
    
        Orthographic: Any
        
        Perspective: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def aspect_ratio(self) -> float:
        ...
    @aspect_ratio.setter
    def aspect_ratio(self, arg: float, /) -> None:
        ...
    
    @property
    def extensions(self) -> lagrange.scene.Extensions:
        ...
    @extensions.setter
    def extensions(self, arg: lagrange.scene.Extensions, /) -> None:
        ...
    
    @property
    def far_plane(self) -> float:
        ...
    @far_plane.setter
    def far_plane(self, arg: float, /) -> None:
        ...
    
    @property
    def get_vertical_fov(self) -> float:
        ...
    
    @property
    def horizontal_fov(self) -> float:
        ...
    @horizontal_fov.setter
    def horizontal_fov(self, arg: float, /) -> None:
        ...
    
    @property
    def look_at(self) -> numpy.typing.NDArray:
        ...
    @look_at.setter
    def look_at(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def near_plane(self) -> float:
        ...
    @near_plane.setter
    def near_plane(self, arg: float, /) -> None:
        ...
    
    @property
    def orthographic_width(self) -> float:
        ...
    @orthographic_width.setter
    def orthographic_width(self, arg: float, /) -> None:
        ...
    
    @property
    def position(self) -> numpy.typing.NDArray:
        ...
    @position.setter
    def position(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def set_horizontal_fov_from_vertical_fov(self, arg: float, /) -> None:
        ...
    
    @property
    def type(self) -> lagrange.scene.Camera.Type:
        ...
    @type.setter
    def type(self, arg: lagrange.scene.Camera.Type, /) -> None:
        ...
    
    @property
    def up(self) -> numpy.typing.NDArray:
        ...
    @up.setter
    def up(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
class CameraList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.scene.Camera], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.CameraList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.scene.Camera, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.CameraList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.scene.Camera, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.scene.Camera:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class ElementIdList:
    """
    None
    """

    def __init__(self, arg: Iterable[int], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.ElementIdList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: int, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def count(self, arg: int, /) -> int:
        """
        Return number of occurrences of `arg`.
        """
        ...
    
    def extend(self, arg: lagrange.scene.ElementIdList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: int, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> int:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
    def remove(self, arg: int, /) -> None:
        """
        Remove first occurrence of `arg`.
        """
        ...
    
class Extensions:
    """
    None
    """

    def __init__(*args, **kwargs):
        """
        Initialize self.  See help(type(self)) for accurate signature.
        """
        ...
    
    @property
    def data(self) -> lagrange.scene.ValueUnorderedMap:
        ...
    @data.setter
    def data(self, arg: lagrange.scene.ValueUnorderedMap, /) -> None:
        ...
    
    @property
    def empty(self) -> bool:
        ...
    
    @property
    def size(self) -> int:
        ...
    
class FacetAllocationStrategy(Enum):
    """
    <attribute '__doc__' of 'FacetAllocationStrategy' objects>
    """

    EvenSplit: Any
    
    RelativeToMeshArea: Any
    
    RelativeToNumFacets: Any
    
    Synchronized: Any
    
class Image:
    """
    None
    """

    def __init__(self) -> None:
        ...
    
    @property
    def extensions(self) -> lagrange.scene.Extensions:
        """
        Additional data associated with the image
        """
        ...
    @extensions.setter
    def extensions(self, arg: lagrange.scene.Extensions, /) -> None:
        """
        Additional data associated with the image
        """
        ...
    
    @property
    def image(self) -> lagrange.scene.ImageBuffer:
        """
        Image buffer
        """
        ...
    @image.setter
    def image(self, arg: lagrange.scene.ImageBuffer, /) -> None:
        """
        Image buffer
        """
        ...
    
    @property
    def name(self) -> str:
        """
        Name of the image object
        """
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        """
        Name of the image object
        """
        ...
    
    @property
    def uri(self) -> os.PathLike:
        """
        URI of the image file
        """
        ...
    @uri.setter
    def uri(self, arg: os.PathLike, /) -> None:
        """
        URI of the image file
        """
        ...
    
class ImageBuffer:
    """
    None
    """

    def __init__(self) -> None:
        ...
    
    @property
    def data(self) -> object:
        """
        Raw image data.
        """
        ...
    @data.setter
    def data(self, arg: numpy.typing.NDArray, /) -> None:
        """
        Raw image data.
        """
        ...
    
    @property
    def dtype(self) -> Optional[type]:
        """
        The element data type of the image buffer.
        """
        ...
    
    @property
    def height(self) -> int:
        """
        Image height
        """
        ...
    
    @property
    def num_channels(self) -> int:
        """
        Number of channels in each pixel
        """
        ...
    
    @property
    def width(self) -> int:
        """
        Image width
        """
        ...
    
class ImageList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.scene.Image], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.ImageList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.scene.Image, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.ImageList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.scene.Image, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.scene.Image:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class Light:
    """
    Light
    """

    class Type(Enum):
        """
        <attribute '__doc__' of 'Type' objects>
        """
    
        Ambient: Any
        
        Area: Any
        
        Directional: Any
        
        Point: Any
        
        Spot: Any
        
        Undefined: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def angle_inner_cone(self) -> float:
        ...
    @angle_inner_cone.setter
    def angle_inner_cone(self, arg: float, /) -> None:
        ...
    
    @property
    def angle_outer_cone(self) -> float:
        ...
    @angle_outer_cone.setter
    def angle_outer_cone(self, arg: float, /) -> None:
        ...
    
    @property
    def attenuation_constant(self) -> float:
        ...
    @attenuation_constant.setter
    def attenuation_constant(self, arg: float, /) -> None:
        ...
    
    @property
    def attenuation_cubic(self) -> float:
        ...
    @attenuation_cubic.setter
    def attenuation_cubic(self, arg: float, /) -> None:
        ...
    
    @property
    def attenuation_linear(self) -> float:
        ...
    @attenuation_linear.setter
    def attenuation_linear(self, arg: float, /) -> None:
        ...
    
    @property
    def attenuation_quadratic(self) -> float:
        ...
    @attenuation_quadratic.setter
    def attenuation_quadratic(self, arg: float, /) -> None:
        ...
    
    @property
    def color_ambient(self) -> numpy.typing.NDArray:
        ...
    @color_ambient.setter
    def color_ambient(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def color_diffuse(self) -> numpy.typing.NDArray:
        ...
    @color_diffuse.setter
    def color_diffuse(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def color_specular(self) -> numpy.typing.NDArray:
        ...
    @color_specular.setter
    def color_specular(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def direction(self) -> numpy.typing.NDArray:
        ...
    @direction.setter
    def direction(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def extensions(self) -> lagrange.scene.Extensions:
        ...
    @extensions.setter
    def extensions(self, arg: lagrange.scene.Extensions, /) -> None:
        ...
    
    @property
    def intensity(self) -> float:
        ...
    @intensity.setter
    def intensity(self, arg: float, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def position(self) -> numpy.typing.NDArray:
        ...
    @position.setter
    def position(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def range(self) -> float:
        ...
    @range.setter
    def range(self, arg: float, /) -> None:
        ...
    
    @property
    def size(self) -> numpy.typing.NDArray:
        ...
    @size.setter
    def size(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def type(self) -> lagrange.scene.Light.Type:
        ...
    @type.setter
    def type(self, arg: lagrange.scene.Light.Type, /) -> None:
        ...
    
    @property
    def up(self) -> numpy.typing.NDArray:
        ...
    @up.setter
    def up(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
class LightList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.scene.Light], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.LightList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.scene.Light, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.LightList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.scene.Light, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.scene.Light:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class Material:
    """
    None
    """

    class AlphaMode(Enum):
        """
        <attribute '__doc__' of 'AlphaMode' objects>
        """
    
        Blend: Any
        
        Mask: Any
        
        Opaque: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def alpha_cutoff(self) -> float:
        ...
    @alpha_cutoff.setter
    def alpha_cutoff(self, arg: float, /) -> None:
        ...
    
    @property
    def alpha_mode(self) -> lagrange.scene.Material.AlphaMode:
        ...
    @alpha_mode.setter
    def alpha_mode(self, arg: lagrange.scene.Material.AlphaMode, /) -> None:
        ...
    
    @property
    def base_color_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @base_color_texture.setter
    def base_color_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def base_color_value(self) -> numpy.typing.NDArray:
        ...
    @base_color_value.setter
    def base_color_value(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def double_sided(self) -> bool:
        ...
    @double_sided.setter
    def double_sided(self, arg: bool, /) -> None:
        ...
    
    @property
    def emissive_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @emissive_texture.setter
    def emissive_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def emissive_value(self) -> numpy.typing.NDArray:
        ...
    @emissive_value.setter
    def emissive_value(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def extensions(self) -> lagrange.scene.Extensions:
        ...
    @extensions.setter
    def extensions(self, arg: lagrange.scene.Extensions, /) -> None:
        ...
    
    @property
    def metallic_roughness_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @metallic_roughness_texture.setter
    def metallic_roughness_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def metallic_value(self) -> float:
        ...
    @metallic_value.setter
    def metallic_value(self, arg: float, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def normal_scale(self) -> float:
        ...
    @normal_scale.setter
    def normal_scale(self, arg: float, /) -> None:
        ...
    
    @property
    def normal_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @normal_texture.setter
    def normal_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def occlusion_strength(self) -> float:
        ...
    @occlusion_strength.setter
    def occlusion_strength(self, arg: float, /) -> None:
        ...
    
    @property
    def occlusion_texture(self) -> lagrange.scene.TextureInfo:
        ...
    @occlusion_texture.setter
    def occlusion_texture(self, arg: lagrange.scene.TextureInfo, /) -> None:
        ...
    
    @property
    def roughness_value(self) -> float:
        ...
    @roughness_value.setter
    def roughness_value(self, arg: float, /) -> None:
        ...
    
class MaterialList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.scene.Material], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.MaterialList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.scene.Material, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.MaterialList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.scene.Material, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.scene.Material:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class MeshInstance3D:
    """
    A single mesh instance in a scene
    """

    def __init__(self) -> None:
        ...
    
    @property
    def mesh_index(self) -> int:
        ...
    @mesh_index.setter
    def mesh_index(self, arg: int, /) -> None:
        ...
    
    @property
    def transform(self) -> numpy.typing.NDArray:
        ...
    @transform.setter
    def transform(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
class Node:
    """
    None
    """

    def __init__(self) -> None:
        ...
    
    @property
    def cameras(self) -> lagrange.scene.ElementIdList:
        ...
    @cameras.setter
    def cameras(self, arg: lagrange.scene.ElementIdList, /) -> None:
        ...
    
    @property
    def children(self) -> lagrange.scene.ElementIdList:
        ...
    @children.setter
    def children(self, arg: lagrange.scene.ElementIdList, /) -> None:
        ...
    
    @property
    def extensions(self) -> lagrange.scene.Extensions:
        ...
    @extensions.setter
    def extensions(self, arg: lagrange.scene.Extensions, /) -> None:
        ...
    
    @property
    def lights(self) -> lagrange.scene.ElementIdList:
        ...
    @lights.setter
    def lights(self, arg: lagrange.scene.ElementIdList, /) -> None:
        ...
    
    @property
    def meshes(self) -> lagrange.scene.SceneMeshInstanceList:
        ...
    @meshes.setter
    def meshes(self, arg: lagrange.scene.SceneMeshInstanceList, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def parent(self) -> int:
        ...
    @parent.setter
    def parent(self, arg: int, /) -> None:
        ...
    
    @property
    def transform(self) -> numpy.typing.NDArray:
        """
        The affine transform associated with this node
        """
        ...
    @transform.setter
    def transform(self, arg: numpy.typing.NDArray, /) -> None:
        """
        The affine transform associated with this node
        """
        ...
    
class NodeList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.scene.Node], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.NodeList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.scene.Node, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.NodeList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.scene.Node, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.scene.Node:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class RemeshingOptions:
    """
    None
    """

    def __init__(self) -> None:
        ...
    
    @property
    def facet_allocation_strategy(self) -> lagrange.scene.FacetAllocationStrategy:
        ...
    @facet_allocation_strategy.setter
    def facet_allocation_strategy(self, arg: lagrange.scene.FacetAllocationStrategy, /) -> None:
        ...
    
    @property
    def min_facets(self) -> int:
        ...
    @min_facets.setter
    def min_facets(self, arg: int, /) -> None:
        ...
    
class Scene:
    """
    A 3D scene
    """

    def __init__(self) -> None:
        ...
    
    def add(self, element: Union[lagrange.scene.Node, lagrange.core.SurfaceMesh, lagrange.scene.Image, lagrange.scene.Texture, lagrange.scene.Material, lagrange.scene.Light, lagrange.scene.Camera, lagrange.scene.Skeleton, lagrange.scene.Animation]) -> int:
        """
        Add an element to the scene.
        
        :param element: The element to add to the scene. E.g. node, mesh, image, texture, material, light, camera, skeleton, or animation.
        
        :returns: The id of the added element.
        """
        ...
    
    def add_child(self, parent_id: int, child_id: int) -> None:
        """
        Add a child node to a parent node.
        
        :param parent_id: The parent node id.
        :param child_id: The child node id.
        
        :returns: The id of the added child node.
        """
        ...
    
    @property
    def animations(self) -> lagrange.scene.AnimationList:
        ...
    @animations.setter
    def animations(self, arg: lagrange.scene.AnimationList, /) -> None:
        ...
    
    @property
    def cameras(self) -> lagrange.scene.CameraList:
        ...
    @cameras.setter
    def cameras(self, arg: lagrange.scene.CameraList, /) -> None:
        ...
    
    @property
    def extensions(self) -> lagrange.scene.Extensions:
        ...
    @extensions.setter
    def extensions(self, arg: lagrange.scene.Extensions, /) -> None:
        ...
    
    @property
    def images(self) -> lagrange.scene.ImageList:
        ...
    @images.setter
    def images(self, arg: lagrange.scene.ImageList, /) -> None:
        ...
    
    @property
    def lights(self) -> lagrange.scene.LightList:
        ...
    @lights.setter
    def lights(self, arg: lagrange.scene.LightList, /) -> None:
        ...
    
    @property
    def materials(self) -> lagrange.scene.MaterialList:
        ...
    @materials.setter
    def materials(self, arg: lagrange.scene.MaterialList, /) -> None:
        ...
    
    @property
    def meshes(self) -> lagrange.scene.SurfaceMeshList:
        ...
    @meshes.setter
    def meshes(self, arg: lagrange.scene.SurfaceMeshList, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def nodes(self) -> lagrange.scene.NodeList:
        ...
    @nodes.setter
    def nodes(self, arg: lagrange.scene.NodeList, /) -> None:
        ...
    
    @property
    def root_nodes(self) -> lagrange.scene.ElementIdList:
        ...
    @root_nodes.setter
    def root_nodes(self, arg: lagrange.scene.ElementIdList, /) -> None:
        ...
    
    @property
    def skeletons(self) -> lagrange.scene.SkeletonList:
        ...
    @skeletons.setter
    def skeletons(self, arg: lagrange.scene.SkeletonList, /) -> None:
        ...
    
    @property
    def textures(self) -> lagrange.scene.TextureList:
        ...
    @textures.setter
    def textures(self, arg: lagrange.scene.TextureList, /) -> None:
        ...
    
class SceneMeshInstance:
    """
    Mesh and material index of a node
    """

    def __init__(self) -> None:
        ...
    
    @property
    def materials(self) -> lagrange.scene.ElementIdList:
        ...
    @materials.setter
    def materials(self, arg: lagrange.scene.ElementIdList, /) -> None:
        ...
    
    @property
    def mesh(self) -> int:
        ...
    @mesh.setter
    def mesh(self, arg: int, /) -> None:
        ...
    
class SceneMeshInstanceList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.scene.SceneMeshInstance], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.SceneMeshInstanceList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.scene.SceneMeshInstance, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.SceneMeshInstanceList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.scene.SceneMeshInstance, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.scene.SceneMeshInstance:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class SimpleScene3D:
    """
    Simple scene container for instanced meshes
    """

    def __init__(self) -> None:
        ...
    
    def add_instance(self, instance: lagrange.scene.MeshInstance3D) -> int:
        ...
    
    def add_mesh(self, mesh: lagrange.core.SurfaceMesh) -> int:
        ...
    
    def get_instance(self, mesh_index: int, instance_index: int) -> lagrange.scene.MeshInstance3D:
        ...
    
    def get_mesh(self, mesh_index: int) -> lagrange.core.SurfaceMesh:
        ...
    
    def num_instances(self, mesh_index: int) -> int:
        ...
    
    @property
    def num_meshes(self) -> int:
        """
        Number of meshes in the scene
        """
        ...
    
    def ref_mesh(self, mesh_index: int) -> lagrange.core.SurfaceMesh:
        ...
    
    def reserve_instances(self, mesh_index: int, num_instances: int) -> None:
        ...
    
    def reserve_meshes(self, num_meshes: int) -> None:
        ...
    
    @property
    def total_num_instances(self) -> int:
        """
        Total number of instances for all meshes in the scene
        """
        ...
    
class Skeleton:

    def __init__(self) -> None:
        ...
    
    @property
    def extensions(self) -> lagrange.scene.Extensions:
        ...
    @extensions.setter
    def extensions(self, arg: lagrange.scene.Extensions, /) -> None:
        ...
    
    @property
    def meshes(self) -> lagrange.scene.ElementIdList:
        ...
    @meshes.setter
    def meshes(self, arg: lagrange.scene.ElementIdList, /) -> None:
        ...
    
class SkeletonList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.scene.Skeleton], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.SkeletonList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.scene.Skeleton, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.SkeletonList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.scene.Skeleton, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.scene.Skeleton:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class SurfaceMeshList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.core.SurfaceMesh], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.SurfaceMeshList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.core.SurfaceMesh, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.SurfaceMeshList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.core.SurfaceMesh, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.core.SurfaceMesh:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class Texture:
    """
    Texture
    """

    class TextureFilter(Enum):
        """
        <attribute '__doc__' of 'TextureFilter' objects>
        """
    
        Linear: Any
        
        LinearMipmapLinear: Any
        
        LinearMipmapNearest: Any
        
        Nearest: Any
        
        NearestMimpapNearest: Any
        
        NearestMipmapLinear: Any
        
        Undefined: Any
        
    class WrapMode(Enum):
        """
        <attribute '__doc__' of 'WrapMode' objects>
        """
    
        Clamp: Any
        
        Decal: Any
        
        Mirror: Any
        
        Wrap: Any
        
    def __init__(self) -> None:
        ...
    
    @property
    def extensions(self) -> lagrange.scene.Extensions:
        ...
    @extensions.setter
    def extensions(self, arg: lagrange.scene.Extensions, /) -> None:
        ...
    
    @property
    def image(self) -> int:
        ...
    @image.setter
    def image(self, arg: int, /) -> None:
        ...
    
    @property
    def mag_filter(self) -> lagrange.scene.Texture.TextureFilter:
        ...
    @mag_filter.setter
    def mag_filter(self, arg: lagrange.scene.Texture.TextureFilter, /) -> None:
        ...
    
    @property
    def min_filter(self) -> lagrange.scene.Texture.TextureFilter:
        ...
    @min_filter.setter
    def min_filter(self, arg: lagrange.scene.Texture.TextureFilter, /) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    @name.setter
    def name(self, arg: str, /) -> None:
        ...
    
    @property
    def offset(self) -> numpy.typing.NDArray:
        ...
    @offset.setter
    def offset(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def rotation(self) -> float:
        ...
    @rotation.setter
    def rotation(self, arg: float, /) -> None:
        ...
    
    @property
    def scale(self) -> numpy.typing.NDArray:
        ...
    @scale.setter
    def scale(self, arg: numpy.typing.NDArray, /) -> None:
        ...
    
    @property
    def wrap_u(self) -> lagrange.scene.Texture.WrapMode:
        ...
    @wrap_u.setter
    def wrap_u(self, arg: lagrange.scene.Texture.WrapMode, /) -> None:
        ...
    
    @property
    def wrap_v(self) -> lagrange.scene.Texture.WrapMode:
        ...
    @wrap_v.setter
    def wrap_v(self, arg: lagrange.scene.Texture.WrapMode, /) -> None:
        ...
    
class TextureInfo:
    """
    None
    """

    def __init__(self) -> None:
        ...
    
    @property
    def index(self) -> int:
        ...
    @index.setter
    def index(self, arg: int, /) -> None:
        ...
    
    @property
    def texcoord(self) -> int:
        ...
    @texcoord.setter
    def texcoord(self, arg: int, /) -> None:
        ...
    
class TextureList:
    """
    None
    """

    def __init__(self, arg: Iterable[lagrange.scene.Texture], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.TextureList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: lagrange.scene.Texture, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.TextureList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: lagrange.scene.Texture, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> lagrange.scene.Texture:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class ValueList:
    """
    None
    """

    def __init__(self, arg: Iterable[Value], /) -> None:
        """
        Construct from an iterable object
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.ValueList) -> None:
        """
        Copy constructor
        """
        ...
    
    def append(self, arg: Value, /) -> None:
        """
        Append `arg` to the end of the list.
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items from list.
        """
        ...
    
    def extend(self, arg: lagrange.scene.ValueList, /) -> None:
        """
        Extend `self` by appending elements from `arg`.
        """
        ...
    
    def insert(self, arg0: int, arg1: Value, /) -> None:
        """
        Insert object `arg1` before index `arg0`.
        """
        ...
    
    def pop(self, index: int = -1) -> Value:
        """
        Remove and return item at `index` (default last).
        """
        ...
    
class ValueMap:
    """
    None
    """

    class ItemView:
        """
        None
        """
    
        def __init__(*args, **kwargs):
            """
            Initialize self.  See help(type(self)) for accurate signature.
            """
            ...
        
    class KeyView:
        """
        None
        """
    
        def __init__(*args, **kwargs):
            """
            Initialize self.  See help(type(self)) for accurate signature.
            """
            ...
        
    class ValueView:
        """
        None
        """
    
        def __init__(*args, **kwargs):
            """
            Initialize self.  See help(type(self)) for accurate signature.
            """
            ...
        
    def __init__(self, arg: dict[str, Value], /) -> None:
        """
        Construct from a dictionary
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.ValueMap) -> None:
        """
        Copy constructor
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items
        """
        ...
    
    def items(self) -> lagrange.scene.ValueMap.ItemView:
        """
        Returns an iterable view of the map's items.
        """
        ...
    
    def keys(self) -> lagrange.scene.ValueMap.KeyView:
        """
        Returns an iterable view of the map's keys.
        """
        ...
    
    def update(self, arg: lagrange.scene.ValueMap, /) -> None:
        """
        Update the map with element from `arg`
        """
        ...
    
    def values(self) -> lagrange.scene.ValueMap.ValueView:
        """
        Returns an iterable view of the map's values.
        """
        ...
    
class ValueUnorderedMap:
    """
    None
    """

    class ItemView:
        """
        None
        """
    
        def __init__(*args, **kwargs):
            """
            Initialize self.  See help(type(self)) for accurate signature.
            """
            ...
        
    class KeyView:
        """
        None
        """
    
        def __init__(*args, **kwargs):
            """
            Initialize self.  See help(type(self)) for accurate signature.
            """
            ...
        
    class ValueView:
        """
        None
        """
    
        def __init__(*args, **kwargs):
            """
            Initialize self.  See help(type(self)) for accurate signature.
            """
            ...
        
    def __init__(self, arg: dict[str, Value], /) -> None:
        """
        Construct from a dictionary
        """
        ...
    
    @overload
    def __init__(self) -> None:
        """
        Default constructor
        """
        ...
    
    @overload
    def __init__(self, arg: lagrange.scene.ValueUnorderedMap) -> None:
        """
        Copy constructor
        """
        ...
    
    def clear(self) -> None:
        """
        Remove all items
        """
        ...
    
    def items(self) -> lagrange.scene.ValueUnorderedMap.ItemView:
        """
        Returns an iterable view of the map's items.
        """
        ...
    
    def keys(self) -> lagrange.scene.ValueUnorderedMap.KeyView:
        """
        Returns an iterable view of the map's keys.
        """
        ...
    
    def update(self, arg: lagrange.scene.ValueUnorderedMap, /) -> None:
        """
        Update the map with element from `arg`
        """
        ...
    
    def values(self) -> lagrange.scene.ValueUnorderedMap.ValueView:
        """
        Returns an iterable view of the map's values.
        """
        ...
    
def compute_global_node_transform(scene: lagrange.scene.Scene, node_idx: int) -> numpy.typing.NDArray:
    """
    Compute the global transform associated with a node.
    
    :param scene: The input node.
    :param node_idx: The index of the taget node.
    
    :returns: The global transform of the target node, which is the combination of transforms from this node all the way to the root.
    """
    ...

def mesh_to_simple_scene(mesh: lagrange.core.SurfaceMesh) -> lagrange.scene.SimpleScene3D:
    """
    Converts a single mesh into a simple scene with a single identity instance of the input mesh.
    
    :param mesh: Input mesh to convert.
    
    :return: Simple scene containing the input mesh.
    """
    ...

def meshes_to_simple_scene(meshes: lagrange.scene.SurfaceMeshList) -> lagrange.scene.SimpleScene3D:
    """
    Converts a list of meshes into a simple scene with a single identity instance of each input mesh.
    
    :param meshes: Input meshes to convert.
    
    :return: Simple scene containing the input meshes.
    """
    ...

def simple_scene_to_mesh(scene: lagrange.scene.SimpleScene3D, normalize_normals: bool = True, normalize_tangents_bitangents: bool = True, preserve_attributes: bool = True) -> lagrange.core.SurfaceMesh:
    """
    Converts a scene into a concatenated mesh with all the transforms applied.
    
    :param scene: Scene to convert.
    :param normalize_normals: If enabled, normals are normalized after transformation.
    :param normalize_tangents_bitangents: If enabled, tangents and bitangents are normalized after transformation.
    :param preserve_attributes: Preserve shared attributes and map them to the output mesh.
    
    :return: Concatenated mesh.
    """
    ...

