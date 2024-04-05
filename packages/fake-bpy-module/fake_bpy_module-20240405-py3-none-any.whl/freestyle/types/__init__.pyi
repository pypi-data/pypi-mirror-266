import typing
import mathutils

GenericType = typing.TypeVar("GenericType")

class AdjacencyIterator:
    """Class hierarchy: `Iterator` > `AdjacencyIterator`Class for representing adjacency iterators used in the chaining
    process. An AdjacencyIterator is created in the increment() and
    decrement() methods of a `ChainingIterator` and passed to the
    traverse() method of the ChainingIterator.
    """

    is_incoming: bool
    """ True if the current ViewEdge is coming towards the iteration vertex, and
False otherwise.

    :type: bool
    """

    object: ViewEdge
    """ The ViewEdge object currently pointed to by this iterator.

    :type: ViewEdge
    """

    def __init__(self):
        """Builds an `AdjacencyIterator` using the default constructor,
        copy constructor or the overloaded constructor.

        """
        ...

    def __init__(self, brother: AdjacencyIterator):
        """Builds an `AdjacencyIterator` using the default constructor,
        copy constructor or the overloaded constructor.

                :param brother: An AdjacencyIterator object.
                :type brother: AdjacencyIterator
        """
        ...

    def __init__(
        self,
        vertex: ViewVertex,
        restrict_to_selection: bool = True,
        restrict_to_unvisited: bool = True,
    ):
        """Builds an `AdjacencyIterator` using the default constructor,
        copy constructor or the overloaded constructor.

                :param vertex: The vertex which is the next crossing.
                :type vertex: ViewVertex
                :param restrict_to_selection: Indicates whether to force the chaining
        to stay within the set of selected ViewEdges or not.
                :type restrict_to_selection: bool
                :param restrict_to_unvisited: Indicates whether a ViewEdge that has
        already been chained must be ignored ot not.
                :type restrict_to_unvisited: bool
        """
        ...

class BBox:
    """Class for representing a bounding box."""

    def __init__(self):
        """Default constructor."""
        ...

class BinaryPredicate0D:
    """Base class for binary predicates working on `Interface0D`
    objects. A BinaryPredicate0D is typically an ordering relation
    between two Interface0D objects. The predicate evaluates a relation
    between the two Interface0D instances and returns a boolean value (true
    or false). It is used by invoking the __call__() method.
    """

    name: str
    """ The name of the binary 0D predicate.

    :type: str
    """

    def __init__(self):
        """Default constructor."""
        ...

    def __call__(self, inter1: Interface0D, inter2: Interface0D) -> Interface0D:
        """Must be overload by inherited classes. It evaluates a relation
        between two Interface0D objects.

                :param inter1: The first Interface0D object.
                :type inter1: Interface0D
                :param inter2: The second Interface0D object.
                :type inter2: Interface0D
                :return: True or false.
                :rtype: bool
        """
        ...

class BinaryPredicate1D:
    """Base class for binary predicates working on `Interface1D`
    objects. A BinaryPredicate1D is typically an ordering relation
    between two Interface1D objects. The predicate evaluates a relation
    between the two Interface1D instances and returns a boolean value (true
    or false). It is used by invoking the __call__() method.
    """

    name: str
    """ The name of the binary 1D predicate.

    :type: str
    """

    def __init__(self):
        """Default constructor."""
        ...

    def __call__(self, inter1: Interface1D, inter2: Interface1D) -> Interface1D:
        """Must be overload by inherited classes. It evaluates a relation
        between two Interface1D objects.

                :param inter1: The first Interface1D object.
                :type inter1: Interface1D
                :param inter2: The second Interface1D object.
                :type inter2: Interface1D
                :return: True or false.
                :rtype: bool
        """
        ...

class Chain:
    """Class hierarchy: `Interface1D` > `Curve` > `Chain`Class to represent a 1D elements issued from the chaining process. A
    Chain is the last step before the `Stroke` and is used in the
    Splitting and Creation processes.
    """

    def __init__(self):
        """Builds a `Chain` using the default constructor,
        copy constructor or from an `Id`.

        """
        ...

    def __init__(self, brother: Chain):
        """Builds a `Chain` using the default constructor,
        copy constructor or from an `Id`.

                :param brother: A Chain object.
                :type brother: Chain
        """
        ...

    def __init__(self, id: Id):
        """Builds a `Chain` using the default constructor,
        copy constructor or from an `Id`.

                :param id: An Id object.
                :type id: Id
        """
        ...

    def push_viewedge_back(self, viewedge: ViewEdge, orientation: bool):
        """Adds a ViewEdge at the end of the Chain.

                :param viewedge: The ViewEdge that must be added.
                :type viewedge: ViewEdge
                :param orientation: The orientation with which the ViewEdge must be
        processed.
                :type orientation: bool
        """
        ...

    def push_viewedge_front(self, viewedge: ViewEdge, orientation: bool):
        """Adds a ViewEdge at the beginning of the Chain.

                :param viewedge: The ViewEdge that must be added.
                :type viewedge: ViewEdge
                :param orientation: The orientation with which the ViewEdge must be
        processed.
                :type orientation: bool
        """
        ...

class ChainingIterator:
    """Class hierarchy: `Iterator` > `ViewEdgeIterator` > `ChainingIterator`Base class for chaining iterators. This class is designed to be
    overloaded in order to describe chaining rules. It makes the
    description of chaining rules easier. The two main methods that need
    to overloaded are traverse() and init(). traverse() tells which
    `ViewEdge` to follow, among the adjacent ones. If you specify
    restriction rules (such as "Chain only ViewEdges of the selection"),
    they will be included in the adjacency iterator (i.e, the adjacent
    iterator will only stop on "valid" edges).
    """

    is_incrementing: bool
    """ True if the current iteration is an incrementation.

    :type: bool
    """

    next_vertex: ViewVertex
    """ The ViewVertex that is the next crossing.

    :type: ViewVertex
    """

    object: ViewEdge
    """ The ViewEdge object currently pointed by this iterator.

    :type: ViewEdge
    """

    def __init__(
        self,
        restrict_to_selection: bool = True,
        restrict_to_unvisited: bool = True,
        begin=None,
        orientation: bool = True,
    ):
        """Builds a Chaining Iterator from the first ViewEdge used for
        iteration and its orientation or by using the copy constructor.

                :param restrict_to_selection: Indicates whether to force the chaining
        to stay within the set of selected ViewEdges or not.
                :type restrict_to_selection: bool
                :param restrict_to_unvisited: Indicates whether a ViewEdge that has
        already been chained must be ignored ot not.
                :type restrict_to_unvisited: bool
                :param begin: The ViewEdge from which to start the chain.
                :param orientation: The direction to follow to explore the graph. If
        true, the direction indicated by the first ViewEdge is used.
                :type orientation: bool
        """
        ...

    def __init__(self, brother: ChainingIterator):
        """Builds a Chaining Iterator from the first ViewEdge used for
        iteration and its orientation or by using the copy constructor.

                :param brother:
                :type brother: ChainingIterator
        """
        ...

    def init(self):
        """Initializes the iterator context. This method is called each
        time a new chain is started. It can be used to reset some
        history information that you might want to keep.

        """
        ...

    def traverse(self, it: AdjacencyIterator) -> AdjacencyIterator:
        """This method iterates over the potential next ViewEdges and returns
        the one that will be followed next. Returns the next ViewEdge to
        follow or None when the end of the chain is reached.

                :param it: The iterator over the ViewEdges adjacent to the end vertex
        of the current ViewEdge. The adjacency iterator reflects the
        restriction rules by only iterating over the valid ViewEdges.
                :type it: AdjacencyIterator
                :return: Returns the next ViewEdge to follow, or None if chaining ends.
        """
        ...

class Curve:
    """Class hierarchy: `Interface1D` > `Curve`Base class for curves made of CurvePoints. `SVertex` is the
    type of the initial curve vertices. A `Chain` is a
    specialization of a Curve.
    """

    is_empty: bool
    """ True if the Curve doesn't have any Vertex yet.

    :type: bool
    """

    segments_size: typing.Any
    """ The number of segments in the polyline constituting the Curve."""

    def __init__(self):
        """Builds a `FrsCurve` using a default constructor,
        copy constructor or from an `Id`.

        """
        ...

    def __init__(self, brother: Curve):
        """Builds a `FrsCurve` using a default constructor,
        copy constructor or from an `Id`.

                :param brother: A Curve object.
                :type brother: Curve
        """
        ...

    def __init__(self, id: Id):
        """Builds a `FrsCurve` using a default constructor,
        copy constructor or from an `Id`.

                :param id: An Id object.
                :type id: Id
        """
        ...

    def push_vertex_back(self, vertex: typing.Union[SVertex, CurvePoint]):
        """Adds a single vertex at the end of the Curve.

        :param vertex: A vertex object.
        :type vertex: typing.Union[SVertex, CurvePoint]
        """
        ...

    def push_vertex_front(self, vertex: typing.Union[SVertex, CurvePoint]):
        """Adds a single vertex at the front of the Curve.

        :param vertex: A vertex object.
        :type vertex: typing.Union[SVertex, CurvePoint]
        """
        ...

class CurvePoint:
    """Class hierarchy: `Interface0D` > `CurvePoint`Class to represent a point of a curve. A CurvePoint can be any point
    of a 1D curve (it doesn't have to be a vertex of the curve). Any
    `Interface1D` is built upon ViewEdges, themselves built upon
    FEdges. Therefore, a curve is basically a polyline made of a list of
    `SVertex` objects. Thus, a CurvePoint is built by linearly
    interpolating two `SVertex` instances. CurvePoint can be used
    as virtual points while querying 0D information along a curve at a
    given resolution.
    """

    fedge: FEdge
    """ Gets the FEdge for the two SVertices that given CurvePoints consists out of.
A shortcut for CurvePoint.first_svertex.get_fedge(CurvePoint.second_svertex).

    :type: FEdge
    """

    first_svertex: SVertex
    """ The first SVertex upon which the CurvePoint is built.

    :type: SVertex
    """

    second_svertex: SVertex
    """ The second SVertex upon which the CurvePoint is built.

    :type: SVertex
    """

    t2d: typing.Any
    """ The 2D interpolation parameter."""

    def __init__(self):
        """Builds a CurvePoint using the default constructor, copy constructor,
        or one of the overloaded constructors. The over loaded constructors
        can either take two `SVertex` or two `CurvePoint`
        objects and an interpolation parameter

        """
        ...

    def __init__(self, brother: CurvePoint):
        """Builds a CurvePoint using the default constructor, copy constructor,
        or one of the overloaded constructors. The over loaded constructors
        can either take two `SVertex` or two `CurvePoint`
        objects and an interpolation parameter

                :param brother: A CurvePoint object.
                :type brother: CurvePoint
        """
        ...

    def __init__(self, first_vertex: SVertex, second_vertex: SVertex, t2d):
        """Builds a CurvePoint using the default constructor, copy constructor,
        or one of the overloaded constructors. The over loaded constructors
        can either take two `SVertex` or two `CurvePoint`
        objects and an interpolation parameter

                :param first_vertex: The first SVertex.
                :type first_vertex: SVertex
                :param second_vertex: The second SVertex.
                :type second_vertex: SVertex
                :param t2d: A 2D interpolation parameter used to linearly interpolate
        first_vertex and second_vertex or first_point and second_point.
        """
        ...

    def __init__(self, first_point: CurvePoint, second_point: CurvePoint, t2d):
        """Builds a CurvePoint using the default constructor, copy constructor,
        or one of the overloaded constructors. The over loaded constructors
        can either take two `SVertex` or two `CurvePoint`
        objects and an interpolation parameter

                :param first_point: The first CurvePoint.
                :type first_point: CurvePoint
                :param second_point: The second CurvePoint.
                :type second_point: CurvePoint
                :param t2d: A 2D interpolation parameter used to linearly interpolate
        first_vertex and second_vertex or first_point and second_point.
        """
        ...

class CurvePointIterator:
    """Class hierarchy: `Iterator` > `CurvePointIterator`Class representing an iterator on a curve. Allows an iterating
    outside initial vertices. A CurvePoint is instantiated and returned
    through the .object attribute.
    """

    object: CurvePoint
    """ The CurvePoint object currently pointed by this iterator.

    :type: CurvePoint
    """

    t: typing.Any
    """ The curvilinear abscissa of the current point."""

    u: typing.Any
    """ The point parameter at the current point in the stroke (0 <= u <= 1)."""

    def __init__(self):
        """Builds a CurvePointIterator object using either the default constructor,
        copy constructor, or the overloaded constructor.

        """
        ...

    def __init__(self, brother: CurvePointIterator):
        """Builds a CurvePointIterator object using either the default constructor,
        copy constructor, or the overloaded constructor.

                :param brother: A CurvePointIterator object.
                :type brother: CurvePointIterator
        """
        ...

    def __init__(self, step=0.0):
        """Builds a CurvePointIterator object using either the default constructor,
        copy constructor, or the overloaded constructor.

                :param step: A resampling resolution with which the curve is resampled.
        If zero, no resampling is done (i.e., the iterator iterates over
        initial vertices).
        """
        ...

class FEdge:
    """Class hierarchy: `Interface1D` > `FEdge`Base Class for feature edges. This FEdge can represent a silhouette,
    a crease, a ridge/valley, a border or a suggestive contour. For
    silhouettes, the FEdge is oriented so that the visible face lies on
    the left of the edge. For borders, the FEdge is oriented so that the
    face lies on the left of the edge. An FEdge can represent an initial
    edge of the mesh or runs across a face of the initial mesh depending
    on the smoothness or sharpness of the mesh. This class is specialized
    into a smooth and a sharp version since their properties slightly vary
    from one to the other.
    """

    first_svertex: SVertex
    """ The first SVertex constituting this FEdge.

    :type: SVertex
    """

    id: Id
    """ The Id of this FEdge.

    :type: Id
    """

    is_smooth: bool
    """ True if this FEdge is a smooth FEdge.

    :type: bool
    """

    nature: Nature
    """ The nature of this FEdge.

    :type: Nature
    """

    next_fedge: FEdge
    """ The FEdge following this one in the ViewEdge. The value is None if
this FEdge is the last of the ViewEdge.

    :type: FEdge
    """

    previous_fedge: FEdge
    """ The FEdge preceding this one in the ViewEdge. The value is None if
this FEdge is the first one of the ViewEdge.

    :type: FEdge
    """

    second_svertex: SVertex
    """ The second SVertex constituting this FEdge.

    :type: SVertex
    """

    viewedge: ViewEdge
    """ The ViewEdge to which this FEdge belongs to.

    :type: ViewEdge
    """

    def FEdge(self):
        """Builds an `FEdge` using the default constructor,
        copy constructor, or between two `SVertex` objects.

        """
        ...

    def FEdge(self, brother: FEdge):
        """Builds an `FEdge` using the default constructor,
        copy constructor, or between two `SVertex` objects.

                :param brother: An FEdge object.
                :type brother: FEdge
        """
        ...

class FEdgeSharp:
    """Class hierarchy: `Interface1D` > `FEdge` > `FEdgeSharp`Class defining a sharp FEdge. A Sharp FEdge corresponds to an initial
    edge of the input mesh. It can be a silhouette, a crease or a border.
    If it is a crease edge, then it is bordered by two faces of the mesh.
    Face a lies on its right whereas Face b lies on its left. If it is a
    border edge, then it doesn't have any face on its right, and thus Face
    a is None.
    """

    face_mark_left: bool
    """ The face mark of the face lying on the left of the FEdge.

    :type: bool
    """

    face_mark_right: bool
    """ The face mark of the face lying on the right of the FEdge. If this FEdge
is a border, it has no face on the right and thus this property is set to
false.

    :type: bool
    """

    material_index_left: typing.Any
    """ The index of the material of the face lying on the left of the FEdge."""

    material_index_right: typing.Any
    """ The index of the material of the face lying on the right of the FEdge.
If this FEdge is a border, it has no Face on its right and therefore
no material."""

    material_left: Material
    """ The material of the face lying on the left of the FEdge.

    :type: Material
    """

    material_right: Material
    """ The material of the face lying on the right of the FEdge. If this FEdge
is a border, it has no Face on its right and therefore no material.

    :type: Material
    """

    normal_left: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ The normal to the face lying on the left of the FEdge.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    normal_right: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ The normal to the face lying on the right of the FEdge. If this FEdge
is a border, it has no Face on its right and therefore no normal.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    def __init__(self):
        """Builds an `FEdgeSharp` using the default constructor,
        copy constructor, or between two `SVertex` objects.

        """
        ...

    def __init__(self, brother: FEdgeSharp):
        """Builds an `FEdgeSharp` using the default constructor,
        copy constructor, or between two `SVertex` objects.

                :param brother: An FEdgeSharp object.
                :type brother: FEdgeSharp
        """
        ...

    def __init__(self, first_vertex: SVertex, second_vertex: SVertex):
        """Builds an `FEdgeSharp` using the default constructor,
        copy constructor, or between two `SVertex` objects.

                :param first_vertex: The first SVertex object.
                :type first_vertex: SVertex
                :param second_vertex: The second SVertex object.
                :type second_vertex: SVertex
        """
        ...

class FEdgeSmooth:
    """Class hierarchy: `Interface1D` > `FEdge` > `FEdgeSmooth`Class defining a smooth edge. This kind of edge typically runs across
    a face of the input mesh. It can be a silhouette, a ridge or valley,
    a suggestive contour.
    """

    face_mark: bool
    """ The face mark of the face that this FEdge is running across.

    :type: bool
    """

    material: Material
    """ The material of the face that this FEdge is running across.

    :type: Material
    """

    material_index: typing.Any
    """ The index of the material of the face that this FEdge is running across."""

    normal: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ The normal of the face that this FEdge is running across.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    def __init__(self):
        """Builds an `FEdgeSmooth` using the default constructor,
        copy constructor, or between two `SVertex`.

        """
        ...

    def __init__(self, brother: FEdgeSmooth):
        """Builds an `FEdgeSmooth` using the default constructor,
        copy constructor, or between two `SVertex`.

                :param brother: An FEdgeSmooth object.
                :type brother: FEdgeSmooth
        """
        ...

    def __init__(self, first_vertex: SVertex, second_vertex: SVertex):
        """Builds an `FEdgeSmooth` using the default constructor,
        copy constructor, or between two `SVertex`.

                :param first_vertex: The first SVertex object.
                :type first_vertex: SVertex
                :param second_vertex: The second SVertex object.
                :type second_vertex: SVertex
        """
        ...

class Id:
    """Class for representing an object Id."""

    first: typing.Any
    """ The first number constituting the Id."""

    second: typing.Any
    """ The second number constituting the Id."""

    def __init__(self, brother):
        """Build the Id from two numbers or another `Id` using the copy constructor.

        :param brother: An Id object.
        """
        ...

    def __init__(self, first=0, second=0):
        """Build the Id from two numbers or another `Id` using the copy constructor.

        :param first:
        :param second: The second number.
        """
        ...

class IntegrationType:
    """Class hierarchy: int > `IntegrationType`Different integration methods that can be invoked to integrate into a
    single value the set of values obtained from each 0D element of an 1D
    element:
    """

    ...

class Interface0D:
    """Base class for any 0D element."""

    id: Id
    """ The Id of this 0D element.

    :type: Id
    """

    name: str
    """ The string of the name of this 0D element.

    :type: str
    """

    nature: Nature
    """ The nature of this 0D element.

    :type: Nature
    """

    point_2d: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ The 2D point of this 0D element.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    point_3d: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ The 3D point of this 0D element.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    projected_x: typing.Any
    """ The X coordinate of the projected 3D point of this 0D element."""

    projected_y: typing.Any
    """ The Y coordinate of the projected 3D point of this 0D element."""

    projected_z: typing.Any
    """ The Z coordinate of the projected 3D point of this 0D element."""

    def __init__(self):
        """Default constructor."""
        ...

    def get_fedge(self, inter: Interface0D) -> Interface0D:
        """Returns the FEdge that lies between this 0D element and the 0D
        element given as the argument.

                :param inter: A 0D element.
                :type inter: Interface0D
                :return: The FEdge lying between the two 0D elements.
                :rtype: FEdge
        """
        ...

class Interface0DIterator:
    """Class hierarchy: `Iterator` > `Interface0DIterator`Class defining an iterator over Interface0D elements. An instance of
    this iterator is always obtained from a 1D element.
    """

    at_last: bool
    """ True if the iterator points to the last valid element.
For its counterpart (pointing to the first valid element), use it.is_begin.

    :type: bool
    """

    object: Interface0D
    """ The 0D object currently pointed to by this iterator. Note that the object
may be an instance of an Interface0D subclass. For example if the iterator
has been created from the vertices_begin() method of the `Stroke`
class, the .object property refers to a `StrokeVertex` object.

    :type: Interface0D
    """

    t: typing.Any
    """ The curvilinear abscissa of the current point."""

    u: typing.Any
    """ The point parameter at the current point in the 1D element (0 <= u <= 1)."""

    def __init__(self, brother: Interface0DIterator):
        """Construct a nested Interface0DIterator using either the copy constructor
        or the constructor that takes an he argument of a Function0D.

                :param brother: An Interface0DIterator object.
                :type brother: Interface0DIterator
        """
        ...

    def __init__(self, it: typing.Union[SVertexIterator, CurvePointIterator]):
        """Construct a nested Interface0DIterator using either the copy constructor
        or the constructor that takes an he argument of a Function0D.

                :param it: An iterator object to be nested.
                :type it: typing.Union[SVertexIterator, CurvePointIterator]
        """
        ...

class Interface1D:
    """Base class for any 1D element."""

    id: Id
    """ The Id of this Interface1D.

    :type: Id
    """

    length_2d: typing.Any
    """ The 2D length of this Interface1D."""

    name: str
    """ The string of the name of the 1D element.

    :type: str
    """

    nature: Nature
    """ The nature of this Interface1D.

    :type: Nature
    """

    time_stamp: typing.Any
    """ The time stamp of the 1D element, mainly used for selection."""

    def __init__(self):
        """Default constructor."""
        ...

    def points_begin(self, t=0.0):
        """Returns an iterator over the Interface1D points, pointing to the
        first point. The difference with vertices_begin() is that here we can
        iterate over points of the 1D element at a any given sampling.
        Indeed, for each iteration, a virtual point is created.

                :param t: A sampling with which we want to iterate over points of
        this 1D element.
                :return: An Interface0DIterator pointing to the first point.
                :rtype: Interface0DIterator
        """
        ...

    def points_end(self, t=0.0):
        """Returns an iterator over the Interface1D points, pointing after the
        last point. The difference with vertices_end() is that here we can
        iterate over points of the 1D element at a given sampling. Indeed,
        for each iteration, a virtual point is created.

                :param t: A sampling with which we want to iterate over points of
        this 1D element.
                :return: An Interface0DIterator pointing after the last point.
                :rtype: Interface0DIterator
        """
        ...

    def vertices_begin(self) -> Interface0DIterator:
        """Returns an iterator over the Interface1D vertices, pointing to the
        first vertex.

                :return: An Interface0DIterator pointing to the first vertex.
                :rtype: Interface0DIterator
        """
        ...

    def vertices_end(self) -> Interface0DIterator:
        """Returns an iterator over the Interface1D vertices, pointing after
        the last vertex.

                :return: An Interface0DIterator pointing after the last vertex.
                :rtype: Interface0DIterator
        """
        ...

class Iterator:
    """Base class to define iterators."""

    is_begin: bool
    """ True if the iterator points to the first element.

    :type: bool
    """

    is_end: bool
    """ True if the iterator points to the last element.

    :type: bool
    """

    name: str
    """ The string of the name of this iterator.

    :type: str
    """

    def __init__(self):
        """Default constructor."""
        ...

    def decrement(self):
        """Makes the iterator point the previous element."""
        ...

    def increment(self):
        """Makes the iterator point the next element."""
        ...

class Material:
    """Class defining a material."""

    ambient: typing.Union[typing.Sequence[float], mathutils.Color]
    """ RGBA components of the ambient color of the material.

    :type: typing.Union[typing.Sequence[float], mathutils.Color]
    """

    diffuse: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ RGBA components of the diffuse color of the material.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    emission: typing.Union[typing.Sequence[float], mathutils.Color]
    """ RGBA components of the emissive color of the material.

    :type: typing.Union[typing.Sequence[float], mathutils.Color]
    """

    line: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ RGBA components of the line color of the material.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    priority: typing.Any
    """ Line color priority of the material."""

    shininess: typing.Any
    """ Shininess coefficient of the material."""

    specular: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ RGBA components of the specular color of the material.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    def __init__(self):
        """Creates a `FrsMaterial` using either default constructor,
        copy constructor, or an overloaded constructor

        """
        ...

    def __init__(self, brother: Material):
        """Creates a `FrsMaterial` using either default constructor,
        copy constructor, or an overloaded constructor

                :param brother: A Material object to be used as a copy constructor.
                :type brother: Material
        """
        ...

    def __init__(
        self,
        line: typing.Union[typing.Sequence[float], mathutils.Vector, list],
        diffuse: typing.Union[typing.Sequence[float], mathutils.Vector, list],
        ambient: typing.Union[typing.Sequence[float], mathutils.Vector, list],
        specular: typing.Union[typing.Sequence[float], mathutils.Vector, list],
        emission: typing.Union[typing.Sequence[float], mathutils.Vector, list],
        shininess,
        priority,
    ):
        """Creates a `FrsMaterial` using either default constructor,
        copy constructor, or an overloaded constructor

                :param line: The line color.
                :type line: typing.Union[typing.Sequence[float], mathutils.Vector, list]
                :param diffuse: The diffuse color.
                :type diffuse: typing.Union[typing.Sequence[float], mathutils.Vector, list]
                :param ambient: The ambient color.
                :type ambient: typing.Union[typing.Sequence[float], mathutils.Vector, list]
                :param specular: The specular color.
                :type specular: typing.Union[typing.Sequence[float], mathutils.Vector, list]
                :param emission: The emissive color.
                :type emission: typing.Union[typing.Sequence[float], mathutils.Vector, list]
                :param shininess: The shininess coefficient.
                :param priority: The line color priority.
        """
        ...

class MediumType:
    """Class hierarchy: int > `MediumType`The different blending modes available to simulate the interaction
    media-medium:
    """

    ...

class Nature:
    """Class hierarchy: int > `Nature`Different possible natures of 0D and 1D elements of the ViewMap.Vertex natures:Edge natures:"""

    ...

class Noise:
    """Class to provide Perlin noise functionalities.Undocumented, consider contributing.Undocumented, consider contributing."""

    def __init__(self, seed=-1):
        """Builds a Noise object. Seed is an optional argument. The seed value is used
        as a seed for random number generation if it is equal to or greater than zero;
        otherwise, time is used as a seed.

                :param seed: Seed for random number generation.
        """
        ...

    def smoothNoise1(self, v):
        """Returns a smooth noise value for a 1D element.

        :param v: One-dimensional sample point.
        :return: A smooth noise value.
        """
        ...

    def smoothNoise2(
        self, v: typing.Union[typing.Sequence[float], mathutils.Vector, list]
    ) -> typing.Union[typing.Sequence[float], mathutils.Vector, list]:
        """Returns a smooth noise value for a 2D element.

        :param v: Two-dimensional sample point.
        :type v: typing.Union[typing.Sequence[float], mathutils.Vector, list]
        :return: A smooth noise value.
        """
        ...

    def smoothNoise3(
        self, v: typing.Union[typing.Sequence[float], mathutils.Vector, list]
    ) -> typing.Union[typing.Sequence[float], mathutils.Vector, list]:
        """Returns a smooth noise value for a 3D element.

        :param v: Three-dimensional sample point.
        :type v: typing.Union[typing.Sequence[float], mathutils.Vector, list]
        :return: A smooth noise value.
        """
        ...

    def turbulence1(self, v, freq, amp, oct=4):
        """Returns a noise value for a 1D element.

        :param v: One-dimensional sample point.
        :param freq: Noise frequency.
        :param amp: Amplitude.
        :param oct: Number of octaves.
        :return: A noise value.
        """
        ...

    def turbulence2(
        self,
        v: typing.Union[typing.Sequence[float], mathutils.Vector, list],
        freq,
        amp,
        oct=4,
    ):
        """Returns a noise value for a 2D element.

        :param v: Two-dimensional sample point.
        :type v: typing.Union[typing.Sequence[float], mathutils.Vector, list]
        :param freq: Noise frequency.
        :param amp: Amplitude.
        :param oct: Number of octaves.
        :return: A noise value.
        """
        ...

    def turbulence3(
        self,
        v: typing.Union[typing.Sequence[float], mathutils.Vector, list],
        freq,
        amp,
        oct=4,
    ):
        """Returns a noise value for a 3D element.

        :param v: Three-dimensional sample point.
        :type v: typing.Union[typing.Sequence[float], mathutils.Vector, list]
        :param freq: Noise frequency.
        :param amp: Amplitude.
        :param oct: Number of octaves.
        :return: A noise value.
        """
        ...

class NonTVertex:
    """Class hierarchy: `Interface0D` > `ViewVertex` > `NonTVertex`View vertex for corners, cusps, etc. associated to a single SVertex.
    Can be associated to 2 or more view edges.
    """

    svertex: SVertex
    """ The SVertex on top of which this NonTVertex is built.

    :type: SVertex
    """

    def __init__(self):
        """Builds a `NonTVertex` using the default constructor or a `SVertex`."""
        ...

    def __init__(self, svertex: SVertex):
        """Builds a `NonTVertex` using the default constructor or a `SVertex`.

        :param svertex: An SVertex object.
        :type svertex: SVertex
        """
        ...

class Operators:
    """Class defining the operators used in a style module. There are five
    types of operators: Selection, chaining, splitting, sorting and
    creation. All these operators are user controlled through functors,
    predicates and shaders that are taken as arguments.
    """

    @staticmethod
    def bidirectional_chain(it: ChainingIterator, pred: UnaryPredicate1D):
        """Builds a set of chains from the current set of ViewEdges. Each
        ViewEdge of the current list potentially starts a new chain. The
        chaining operator then iterates over the ViewEdges of the ViewMap
        using the user specified iterator. This operator iterates both using
        the increment and decrement operators and is therefore bidirectional.
        This operator works with a ChainingIterator which contains the
        chaining rules. It is this last one which can be told to chain only
        edges that belong to the selection or not to process twice a ViewEdge
        during the chaining. Each time a ViewEdge is added to a chain, its
        chaining time stamp is incremented. This allows you to keep track of
        the number of chains to which a ViewEdge belongs to.

                :param it: The ChainingIterator on the ViewEdges of the ViewMap. It
        contains the chaining rule.
                :type it: ChainingIterator
                :param pred: The predicate on the ViewEdge that expresses the stopping condition.
        This parameter is optional, you make not want to pass a stopping criterion
        when the stopping criterion is already contained in the iterator definition.
                :type pred: UnaryPredicate1D
        """
        ...

    @staticmethod
    def bidirectional_chain(it: ChainingIterator):
        """Builds a set of chains from the current set of ViewEdges. Each
        ViewEdge of the current list potentially starts a new chain. The
        chaining operator then iterates over the ViewEdges of the ViewMap
        using the user specified iterator. This operator iterates both using
        the increment and decrement operators and is therefore bidirectional.
        This operator works with a ChainingIterator which contains the
        chaining rules. It is this last one which can be told to chain only
        edges that belong to the selection or not to process twice a ViewEdge
        during the chaining. Each time a ViewEdge is added to a chain, its
        chaining time stamp is incremented. This allows you to keep track of
        the number of chains to which a ViewEdge belongs to.

                :param it: The ChainingIterator on the ViewEdges of the ViewMap. It
        contains the chaining rule.
                :type it: ChainingIterator
        """
        ...

    @staticmethod
    def chain(
        it: ViewEdgeIterator, pred: UnaryPredicate1D, modifier: UnaryFunction1DVoid
    ):
        """Builds a set of chains from the current set of ViewEdges. Each
        ViewEdge of the current list starts a new chain. The chaining
        operator then iterates over the ViewEdges of the ViewMap using the
        user specified iterator. This operator only iterates using the
        increment operator and is therefore unidirectional.

                :param it: The iterator on the ViewEdges of the ViewMap. It contains
        the chaining rule.
                :type it: ViewEdgeIterator
                :param pred: The predicate on the ViewEdge that expresses the
        stopping condition.
                :type pred: UnaryPredicate1D
                :param modifier: A function that takes a ViewEdge as argument and
        that is used to modify the processed ViewEdge state (the
        timestamp incrementation is a typical illustration of such a modifier).
        If this argument is not given, the time stamp is automatically managed.
                :type modifier: UnaryFunction1DVoid
        """
        ...

    @staticmethod
    def chain(it: ViewEdgeIterator, pred: UnaryPredicate1D):
        """Builds a set of chains from the current set of ViewEdges. Each
        ViewEdge of the current list starts a new chain. The chaining
        operator then iterates over the ViewEdges of the ViewMap using the
        user specified iterator. This operator only iterates using the
        increment operator and is therefore unidirectional.

                :param it: The iterator on the ViewEdges of the ViewMap. It contains
        the chaining rule.
                :type it: ViewEdgeIterator
                :param pred: The predicate on the ViewEdge that expresses the
        stopping condition.
                :type pred: UnaryPredicate1D
        """
        ...

    @staticmethod
    def create(pred: UnaryPredicate1D, shaders):
        """Creates and shades the strokes from the current set of chains. A
        predicate can be specified to make a selection pass on the chains.

                :param pred: The predicate that a chain must verify in order to be
        transform as a stroke.
                :type pred: UnaryPredicate1D
                :param shaders: The list of shaders used to shade the strokes.
        """
        ...

    @staticmethod
    def get_chain_from_index(i):
        """Returns the Chain at the index in the current set of Chains.

        :param i: index (0 <= i < Operators.get_chains_size()).
        :return: The Chain object.
        :rtype: Chain
        """
        ...

    @staticmethod
    def get_chains_size() -> Chain:
        """Returns the number of Chains.

        :return: The number of Chains.
        """
        ...

    @staticmethod
    def get_stroke_from_index(i):
        """Returns the Stroke at the index in the current set of Strokes.

        :param i: index (0 <= i < Operators.get_strokes_size()).
        :return: The Stroke object.
        :rtype: Stroke
        """
        ...

    @staticmethod
    def get_strokes_size() -> Stroke:
        """Returns the number of Strokes.

        :return: The number of Strokes.
        """
        ...

    @staticmethod
    def get_view_edges_size():
        """Returns the number of ViewEdges.

        :return: The number of ViewEdges.
        """
        ...

    @staticmethod
    def get_viewedge_from_index(i):
        """Returns the ViewEdge at the index in the current set of ViewEdges.

        :param i: index (0 <= i < Operators.get_view_edges_size()).
        :return: The ViewEdge object.
        :rtype: ViewEdge
        """
        ...

    @staticmethod
    def recursive_split(
        func: UnaryFunction0DDouble, pred_1d: UnaryPredicate1D, sampling=0.0
    ):
        """Splits the current set of chains in a recursive way. We process the
        points of each chain (with a specified sampling) to find the point
        minimizing a specified function. The chain is split in two at this
        point and the two new chains are processed in the same way. The
        recursivity level is controlled through a predicate 1D that expresses
        a stopping condition on the chain that is about to be processed.The user can also specify a 0D predicate to make a first selection on the points
        that can potentially be split. A point that doesn't verify the 0D
        predicate won't be candidate in realizing the min.

                :param func: The Unary Function evaluated at each point of the chain.
        The splitting point is the point minimizing this function.
                :type func: UnaryFunction0DDouble
                :param pred_1d: The Unary Predicate expressing the recursivity stopping
        condition. This predicate is evaluated for each curve before it
        actually gets split. If pred_1d(chain) is true, the curve won't be
        split anymore.
                :type pred_1d: UnaryPredicate1D
                :param sampling: The resolution used to sample the chain for the
        predicates evaluation. (The chain is not actually resampled; a
        virtual point only progresses along the curve using this
        resolution.)
        """
        ...

    @staticmethod
    def recursive_split(
        func: UnaryFunction0DDouble,
        pred_0d: UnaryPredicate0D,
        pred_1d: UnaryPredicate1D,
        sampling=0.0,
    ):
        """Splits the current set of chains in a recursive way. We process the
        points of each chain (with a specified sampling) to find the point
        minimizing a specified function. The chain is split in two at this
        point and the two new chains are processed in the same way. The
        recursivity level is controlled through a predicate 1D that expresses
        a stopping condition on the chain that is about to be processed.The user can also specify a 0D predicate to make a first selection on the points
        that can potentially be split. A point that doesn't verify the 0D
        predicate won't be candidate in realizing the min.

                :param func: The Unary Function evaluated at each point of the chain.
        The splitting point is the point minimizing this function.
                :type func: UnaryFunction0DDouble
                :param pred_0d: The Unary Predicate 0D used to select the candidate
        points where the split can occur. For example, it is very likely
        that would rather have your chain splitting around its middle
        point than around one of its extremities. A 0D predicate working
        on the curvilinear abscissa allows to add this kind of constraints.
                :type pred_0d: UnaryPredicate0D
                :param pred_1d: The Unary Predicate expressing the recursivity stopping
        condition. This predicate is evaluated for each curve before it
        actually gets split. If pred_1d(chain) is true, the curve won't be
        split anymore.
                :type pred_1d: UnaryPredicate1D
                :param sampling: The resolution used to sample the chain for the
        predicates evaluation. (The chain is not actually resampled; a
        virtual point only progresses along the curve using this
        resolution.)
        """
        ...

    @staticmethod
    def reset(delete_strokes: bool = True):
        """Resets the line stylization process to the initial state. The results of
        stroke creation are accumulated if delete_strokes is set to False.

                :param delete_strokes: Delete the strokes that are currently stored.
                :type delete_strokes: bool
        """
        ...

    @staticmethod
    def select(pred: UnaryPredicate1D):
        """Selects the ViewEdges of the ViewMap verifying a specified
        condition.

                :param pred: The predicate expressing this condition.
                :type pred: UnaryPredicate1D
        """
        ...

    @staticmethod
    def sequential_split(
        starting_pred: UnaryPredicate0D, stopping_pred: UnaryPredicate0D, sampling=0.0
    ):
        """Splits each chain of the current set of chains in a sequential way.
        The points of each chain are processed (with a specified sampling)
        sequentially. The first point of the initial chain is the
        first point of one of the resulting chains. The splitting ends when
        no more chain can start.

                :param starting_pred: The predicate on a point that expresses the
        starting condition. Each time this condition is verified, a new chain begins
                :type starting_pred: UnaryPredicate0D
                :param stopping_pred: The predicate on a point that expresses the
        stopping condition. The chain ends as soon as this predicate is verified.
                :type stopping_pred: UnaryPredicate0D
                :param sampling: The resolution used to sample the chain for the
        predicates evaluation. (The chain is not actually resampled;
        a virtual point only progresses along the curve using this
        resolution.)
        """
        ...

    @staticmethod
    def sequential_split(pred: UnaryPredicate0D, sampling=0.0):
        """Splits each chain of the current set of chains in a sequential way.
        The points of each chain are processed (with a specified sampling)
        sequentially. The first point of the initial chain is the
        first point of one of the resulting chains. The splitting ends when
        no more chain can start.

                :param pred: The predicate on a point that expresses the splitting condition.
        Each time the condition is verified, the chain is split into two chains.
        The resulting set of chains is a partition of the initial chain
                :type pred: UnaryPredicate0D
                :param sampling: The resolution used to sample the chain for the
        predicates evaluation. (The chain is not actually resampled;
        a virtual point only progresses along the curve using this
        resolution.)
        """
        ...

    @staticmethod
    def sort(pred: BinaryPredicate1D):
        """Sorts the current set of chains (or viewedges) according to the
        comparison predicate given as argument.

                :param pred: The binary predicate used for the comparison.
                :type pred: BinaryPredicate1D
        """
        ...

class SShape:
    """Class to define a feature shape. It is the gathering of feature
    elements from an identified input shape.
    """

    bbox: BBox
    """ The bounding box of the SShape.

    :type: BBox
    """

    edges: typing.List[FEdge]
    """ The list of edges constituting this SShape.

    :type: typing.List[FEdge]
    """

    id: Id
    """ The Id of this SShape.

    :type: Id
    """

    name: str
    """ The name of the SShape.

    :type: str
    """

    vertices: typing.List[SVertex]
    """ The list of vertices constituting this SShape.

    :type: typing.List[SVertex]
    """

    def __init__(self):
        """Creates a `SShape` class using either a default constructor or copy constructor."""
        ...

    def __init__(self, brother: SShape):
        """Creates a `SShape` class using either a default constructor or copy constructor.

        :param brother: An SShape object.
        :type brother: SShape
        """
        ...

    def add_edge(self, edge: FEdge):
        """Adds an FEdge to the list of FEdges.

        :param edge: An FEdge object.
        :type edge: FEdge
        """
        ...

    def add_vertex(self, vertex: SVertex):
        """Adds an SVertex to the list of SVertex of this Shape. The SShape
        attribute of the SVertex is also set to this SShape.

                :param vertex: An SVertex object.
                :type vertex: SVertex
        """
        ...

    def compute_bbox(self):
        """Compute the bbox of the SShape."""
        ...

class SVertex:
    """Class hierarchy: `Interface0D` > `SVertex`Class to define a vertex of the embedding."""

    curvatures: typing.Tuple
    """ Curvature information expressed in the form of a seven-element tuple
(K1, e1, K2, e2, Kr, er, dKr), where K1 and K2 are scalar values
representing the first (maximum) and second (minimum) principal
curvatures at this SVertex, respectively; e1 and e2 are
three-dimensional vectors representing the first and second principal
directions, i.e. the directions of the normal plane where the
curvature takes its maximum and minimum values, respectively; and Kr,
er and dKr are the radial curvature, radial direction, and the
derivative of the radial curvature at this SVertex, respectively.

    :type: typing.Tuple
    """

    id: Id
    """ The Id of this SVertex.

    :type: Id
    """

    normals: typing.Any
    """ The normals for this Vertex as a list. In a sharp surface, an SVertex
has exactly one normal. In a smooth surface, an SVertex can have any
number of normals."""

    normals_size: typing.Any
    """ The number of different normals for this SVertex."""

    point_2d: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ The projected 3D coordinates of the SVertex.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    point_3d: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ The 3D coordinates of the SVertex.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    viewvertex: ViewVertex
    """ If this SVertex is also a ViewVertex, this property refers to the
ViewVertex, and None otherwise.

    :type: ViewVertex
    """

    def __init__(self):
        """Builds a `SVertex` using the default constructor,
        copy constructor or the overloaded constructor which builds   a `SVertex` from 3D coordinates and an Id.

        """
        ...

    def __init__(self, brother: SVertex):
        """Builds a `SVertex` using the default constructor,
        copy constructor or the overloaded constructor which builds   a `SVertex` from 3D coordinates and an Id.

                :param brother: A SVertex object.
                :type brother: SVertex
        """
        ...

    def __init__(
        self, point_3d: typing.Union[typing.Sequence[float], mathutils.Vector], id: Id
    ):
        """Builds a `SVertex` using the default constructor,
        copy constructor or the overloaded constructor which builds   a `SVertex` from 3D coordinates and an Id.

                :param point_3d: A three-dimensional vector.
                :type point_3d: typing.Union[typing.Sequence[float], mathutils.Vector]
                :param id: An Id object.
                :type id: Id
        """
        ...

    def add_fedge(self, fedge: FEdge):
        """Add an FEdge to the list of edges emanating from this SVertex.

        :param fedge: An FEdge.
        :type fedge: FEdge
        """
        ...

    def add_normal(
        self, normal: typing.Union[typing.Sequence[float], mathutils.Vector, list]
    ):
        """Adds a normal to the SVertex's set of normals. If the same normal
        is already in the set, nothing changes.

                :param normal: A three-dimensional vector.
                :type normal: typing.Union[typing.Sequence[float], mathutils.Vector, list]
        """
        ...

class SVertexIterator:
    """Class hierarchy: `Iterator` > `SVertexIterator`Class representing an iterator over `SVertex` of a
    `ViewEdge`. An instance of an SVertexIterator can be obtained
    from a ViewEdge by calling verticesBegin() or verticesEnd().
    """

    object: SVertex
    """ The SVertex object currently pointed by this iterator.

    :type: SVertex
    """

    t: typing.Any
    """ The curvilinear abscissa of the current point."""

    u: typing.Any
    """ The point parameter at the current point in the 1D element (0 <= u <= 1)."""

    def __init__(self):
        """Build an SVertexIterator using either the default constructor, copy constructor,or the overloaded constructor that starts iteration from an SVertex object vertex."""
        ...

    def __init__(self, brother: SVertexIterator):
        """Build an SVertexIterator using either the default constructor, copy constructor,or the overloaded constructor that starts iteration from an SVertex object vertex.

        :param brother: An SVertexIterator object.
        :type brother: SVertexIterator
        """
        ...

    def __init__(
        self, vertex: SVertex, begin: SVertex, previous_edge: FEdge, next_edge: FEdge, t
    ):
        """Build an SVertexIterator using either the default constructor, copy constructor,or the overloaded constructor that starts iteration from an SVertex object vertex.

        :param vertex: The SVertex from which the iterator starts iteration.
        :type vertex: SVertex
        :param begin: The first SVertex of a ViewEdge.
        :type begin: SVertex
        :param previous_edge: The previous FEdge coming to vertex.
        :type previous_edge: FEdge
        :param next_edge: The next FEdge going out from vertex.
        :type next_edge: FEdge
        :param t: The curvilinear abscissa at vertex.
        """
        ...

class Stroke:
    """Class hierarchy: `Interface1D` > `Stroke`Class to define a stroke. A stroke is made of a set of 2D vertices
    (`StrokeVertex`), regularly spaced out. This set of vertices
    defines the stroke's backbone geometry. Each of these stroke vertices
    defines the stroke's shape and appearance at this vertex position.
    """

    id: Id
    """ The Id of this Stroke.

    :type: Id
    """

    length_2d: typing.Any
    """ The 2D length of the Stroke."""

    medium_type: MediumType
    """ The MediumType used for this Stroke.

    :type: MediumType
    """

    texture_id: typing.Any
    """ The ID of the texture used to simulate th marks system for this Stroke."""

    tips: bool
    """ True if this Stroke uses a texture with tips, and false otherwise.

    :type: bool
    """

    def Stroke(self):
        """Creates a `Stroke` using the default constructor or copy constructor"""
        ...

    def Stroke(self, brother):
        """Creates a `Stroke` using the default constructor or copy constructor

        :param brother:
        """
        ...

    def compute_sampling(self, n):
        """Compute the sampling needed to get N vertices. If the
        specified number of vertices is less than the actual number of
        vertices, the actual sampling value is returned. (To remove Vertices,
        use the RemoveVertex() method of this class.)

                :param n: The number of stroke vertices we eventually want
        in our Stroke.
                :return: The sampling that must be used in the Resample(float)
        method.
        """
        ...

    def insert_vertex(self, vertex: StrokeVertex, next: StrokeVertexIterator):
        """Inserts the StrokeVertex given as argument into the Stroke before the
        point specified by next. The length and curvilinear abscissa are
        updated consequently.

                :param vertex: The StrokeVertex to insert in the Stroke.
                :type vertex: StrokeVertex
                :param next: A StrokeVertexIterator pointing to the StrokeVertex
        before which vertex must be inserted.
                :type next: StrokeVertexIterator
        """
        ...

    def remove_all_vertices(self):
        """Removes all vertices from the Stroke."""
        ...

    def remove_vertex(self, vertex: StrokeVertex):
        """Removes the StrokeVertex given as argument from the Stroke. The length
        and curvilinear abscissa are updated consequently.

                :param vertex: the StrokeVertex to remove from the Stroke.
                :type vertex: StrokeVertex
        """
        ...

    def resample(self, n):
        """Resamples the stroke so using one of two methods with the goal
        of creating a stroke with fewer points and the same shape.

                :param n: Resamples the stroke so that it eventually has N points. That means
        it is going to add N-vertices_size, where vertices_size is the
        number of points we already have. If vertices_size >= N, no
        resampling is done.
        """
        ...

    def resample(self, sampling):
        """Resamples the stroke so using one of two methods with the goal
        of creating a stroke with fewer points and the same shape.

                :param sampling: Resamples the stroke with a given sampling value. If the
        sampling is smaller than the actual sampling value, no resampling is done.
        """
        ...

    def stroke_vertices_begin(self, t=0.0):
        """Returns a StrokeVertexIterator pointing on the first StrokeVertex of
        the Stroke. One can specify a sampling value to re-sample the Stroke
        on the fly if needed.

                :param t: The resampling value with which we want our Stroke to be
        resampled. If 0 is specified, no resampling is done.
                :return: A StrokeVertexIterator pointing on the first StrokeVertex.
                :rtype: StrokeVertexIterator
        """
        ...

    def stroke_vertices_end(self) -> StrokeVertexIterator:
        """Returns a StrokeVertexIterator pointing after the last StrokeVertex
        of the Stroke.

                :return: A StrokeVertexIterator pointing after the last StrokeVertex.
                :rtype: StrokeVertexIterator
        """
        ...

    def stroke_vertices_size(self) -> StrokeVertexIterator:
        """Returns the number of StrokeVertex constituting the Stroke.

        :return: The number of stroke vertices.
        """
        ...

    def update_length(self):
        """Updates the 2D length of the Stroke."""
        ...

class StrokeAttribute:
    """Class to define a set of attributes associated with a `StrokeVertex`.
    The attribute set stores the color, alpha and thickness values for a Stroke
    Vertex.
    """

    alpha: typing.Any
    """ Alpha component of the stroke color."""

    color: typing.Union[typing.Sequence[float], mathutils.Color]
    """ RGB components of the stroke color.

    :type: typing.Union[typing.Sequence[float], mathutils.Color]
    """

    thickness: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ Right and left components of the stroke thickness.
The right (left) component is the thickness on the right (left) of the vertex
when following the stroke.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    visible: bool
    """ The visibility flag. True if the StrokeVertex is visible.

    :type: bool
    """

    def __init__(self):
        """Creates a `StrokeAttribute` object using either a default constructor,
        copy constructor, overloaded constructor, or and interpolation constructor
        to interpolate between two `StrokeAttribute` objects.

        """
        ...

    def __init__(self, brother: StrokeAttribute):
        """Creates a `StrokeAttribute` object using either a default constructor,
        copy constructor, overloaded constructor, or and interpolation constructor
        to interpolate between two `StrokeAttribute` objects.

                :param brother: A StrokeAttribute object to be used as a copy constructor.
                :type brother: StrokeAttribute
        """
        ...

    def __init__(self, red, green, blue, alpha, thickness_right, thickness_left):
        """Creates a `StrokeAttribute` object using either a default constructor,
        copy constructor, overloaded constructor, or and interpolation constructor
        to interpolate between two `StrokeAttribute` objects.

                :param red: Red component of a stroke color.
                :param green: Green component of a stroke color.
                :param blue: Blue component of a stroke color.
                :param alpha: Alpha component of a stroke color.
                :param thickness_right: Stroke thickness on the right.
                :param thickness_left: Stroke thickness on the left.
        """
        ...

    def __init__(self, attribute1: StrokeAttribute, attribute2: StrokeAttribute, t):
        """Creates a `StrokeAttribute` object using either a default constructor,
        copy constructor, overloaded constructor, or and interpolation constructor
        to interpolate between two `StrokeAttribute` objects.

                :param attribute1: The first StrokeAttribute object.
                :type attribute1: StrokeAttribute
                :param attribute2: The second StrokeAttribute object.
                :type attribute2: StrokeAttribute
                :param t: The interpolation parameter (0 <= t <= 1).
        """
        ...

    def get_attribute_real(self, name: str) -> str:
        """Returns an attribute of float type.

        :param name: The name of the attribute.
        :type name: str
        :return: The attribute value.
        """
        ...

    def get_attribute_vec2(self, name: str) -> str:
        """Returns an attribute of two-dimensional vector type.

        :param name: The name of the attribute.
        :type name: str
        :return: The attribute value.
        :rtype: mathutils.Vector
        """
        ...

    def get_attribute_vec3(self, name: str) -> str:
        """Returns an attribute of three-dimensional vector type.

        :param name: The name of the attribute.
        :type name: str
        :return: The attribute value.
        :rtype: mathutils.Vector
        """
        ...

    def has_attribute_real(self, name: str) -> str:
        """Checks whether the attribute name of float type is available.

        :param name: The name of the attribute.
        :type name: str
        :return: True if the attribute is available.
        :rtype: bool
        """
        ...

    def has_attribute_vec2(self, name: str) -> str:
        """Checks whether the attribute name of two-dimensional vector type
        is available.

                :param name: The name of the attribute.
                :type name: str
                :return: True if the attribute is available.
                :rtype: bool
        """
        ...

    def has_attribute_vec3(self, name: str) -> str:
        """Checks whether the attribute name of three-dimensional vector
        type is available.

                :param name: The name of the attribute.
                :type name: str
                :return: True if the attribute is available.
                :rtype: bool
        """
        ...

    def set_attribute_real(self, name: str, value):
        """Adds a user-defined attribute of float type. If there is no
        attribute of the given name, it is added. Otherwise, the new value
        replaces the old one.

                :param name: The name of the attribute.
                :type name: str
                :param value: The attribute value.
        """
        ...

    def set_attribute_vec2(
        self,
        name: str,
        value: typing.Union[typing.Sequence[float], mathutils.Vector, list],
    ):
        """Adds a user-defined attribute of two-dimensional vector type. If
        there is no attribute of the given name, it is added. Otherwise,
        the new value replaces the old one.

                :param name: The name of the attribute.
                :type name: str
                :param value: The attribute value.
                :type value: typing.Union[typing.Sequence[float], mathutils.Vector, list]
        """
        ...

    def set_attribute_vec3(
        self,
        name: str,
        value: typing.Union[typing.Sequence[float], mathutils.Vector, list],
    ):
        """Adds a user-defined attribute of three-dimensional vector type.
        If there is no attribute of the given name, it is added.
        Otherwise, the new value replaces the old one.

                :param name: The name of the attribute.
                :type name: str
                :param value: The attribute value.
                :type value: typing.Union[typing.Sequence[float], mathutils.Vector, list]
        """
        ...

class StrokeShader:
    """Base class for stroke shaders. Any stroke shader must inherit from
    this class and overload the shade() method. A StrokeShader is
    designed to modify stroke attributes such as thickness, color,
    geometry, texture, blending mode, and so on. The basic way for this
    operation is to iterate over the stroke vertices of the `Stroke`
    and to modify the `StrokeAttribute` of each vertex. Here is a
    code example of such an iteration:
    """

    name: str
    """ The name of the stroke shader.

    :type: str
    """

    def __init__(self):
        """Default constructor."""
        ...

    def shade(self, stroke: Stroke):
        """The shading method. Must be overloaded by inherited classes.

        :param stroke: A Stroke object.
        :type stroke: Stroke
        """
        ...

class StrokeVertex:
    """Class hierarchy: `Interface0D` > `CurvePoint` > `StrokeVertex`Class to define a stroke vertex."""

    attribute: StrokeAttribute
    """ StrokeAttribute for this StrokeVertex.

    :type: StrokeAttribute
    """

    curvilinear_abscissa: typing.Any
    """ Curvilinear abscissa of this StrokeVertex in the Stroke."""

    point: typing.Union[typing.Sequence[float], mathutils.Vector]
    """ 2D point coordinates.

    :type: typing.Union[typing.Sequence[float], mathutils.Vector]
    """

    stroke_length: typing.Any
    """ Stroke length (it is only a value retained by the StrokeVertex,
and it won't change the real stroke length)."""

    u: typing.Any
    """ Curvilinear abscissa of this StrokeVertex in the Stroke."""

    def __init__(self):
        """Builds a `StrokeVertex` using the default constructor,
        copy constructor, from 2 `StrokeVertex` and an interpolation parameter,
        from a CurvePoint, from a SVertex, or a `SVertex`   and a `StrokeAttribute` object.

        """
        ...

    def __init__(self, brother: StrokeVertex):
        """Builds a `StrokeVertex` using the default constructor,
        copy constructor, from 2 `StrokeVertex` and an interpolation parameter,
        from a CurvePoint, from a SVertex, or a `SVertex`   and a `StrokeAttribute` object.

                :param brother: A StrokeVertex object.
                :type brother: StrokeVertex
        """
        ...

    def __init__(self, first_vertex: StrokeVertex, second_vertex: StrokeVertex, t3d):
        """Builds a `StrokeVertex` using the default constructor,
        copy constructor, from 2 `StrokeVertex` and an interpolation parameter,
        from a CurvePoint, from a SVertex, or a `SVertex`   and a `StrokeAttribute` object.

                :param first_vertex: The first StrokeVertex.
                :type first_vertex: StrokeVertex
                :param second_vertex: The second StrokeVertex.
                :type second_vertex: StrokeVertex
                :param t3d: An interpolation parameter.
        """
        ...

    def __init__(self, point: CurvePoint):
        """Builds a `StrokeVertex` using the default constructor,
        copy constructor, from 2 `StrokeVertex` and an interpolation parameter,
        from a CurvePoint, from a SVertex, or a `SVertex`   and a `StrokeAttribute` object.

                :param point: A CurvePoint object.
                :type point: CurvePoint
        """
        ...

    def __init__(self, svertex: typing.Union[SVertex, SVertex]):
        """Builds a `StrokeVertex` using the default constructor,
        copy constructor, from 2 `StrokeVertex` and an interpolation parameter,
        from a CurvePoint, from a SVertex, or a `SVertex`   and a `StrokeAttribute` object.

                :param svertex: An SVertex object.An SVertex object.
                :type svertex: typing.Union[SVertex, SVertex]
        """
        ...

    def __init__(
        self, svertex: typing.Union[SVertex, SVertex], attribute: StrokeAttribute
    ):
        """Builds a `StrokeVertex` using the default constructor,
        copy constructor, from 2 `StrokeVertex` and an interpolation parameter,
        from a CurvePoint, from a SVertex, or a `SVertex`   and a `StrokeAttribute` object.

                :param svertex: An SVertex object.An SVertex object.
                :type svertex: typing.Union[SVertex, SVertex]
                :param attribute: A StrokeAttribute object.
                :type attribute: StrokeAttribute
        """
        ...

class StrokeVertexIterator:
    """Class hierarchy: `Iterator` > `StrokeVertexIterator`Class defining an iterator designed to iterate over the
    `StrokeVertex` of a `Stroke`. An instance of a
    StrokeVertexIterator can be obtained from a Stroke by calling
    iter(), stroke_vertices_begin() or stroke_vertices_begin(). It is iterating
    over the same vertices as an `Interface0DIterator`. The difference
    resides in the object access: an Interface0DIterator only allows
    access to an Interface0D while one might need to access the
    specialized StrokeVertex type. In this case, one should use a
    StrokeVertexIterator. To call functions of the UnaryFuntion0D type,
    a StrokeVertexIterator can be converted to an Interface0DIterator by
    by calling Interface0DIterator(it).
    """

    at_last: bool
    """ True if the iterator points to the last valid element.
For its counterpart (pointing to the first valid element), use it.is_begin.

    :type: bool
    """

    object: StrokeVertex
    """ The StrokeVertex object currently pointed to by this iterator.

    :type: StrokeVertex
    """

    t: typing.Any
    """ The curvilinear abscissa of the current point."""

    u: typing.Any
    """ The point parameter at the current point in the stroke (0 <= u <= 1)."""

    def __init__(self):
        """Creates a `StrokeVertexIterator` using either the
        default constructor or the copy constructor.

        """
        ...

    def __init__(self, brother: StrokeVertexIterator):
        """Creates a `StrokeVertexIterator` using either the
        default constructor or the copy constructor.

                :param brother: A StrokeVertexIterator object.
                :type brother: StrokeVertexIterator
        """
        ...

    def decremented(self) -> StrokeVertexIterator:
        """Returns a copy of a decremented StrokeVertexIterator.

        :return: A StrokeVertexIterator pointing the previous StrokeVertex.
        :rtype: StrokeVertexIterator
        """
        ...

    def incremented(self) -> StrokeVertexIterator:
        """Returns a copy of an incremented StrokeVertexIterator.

        :return: A StrokeVertexIterator pointing the next StrokeVertex.
        :rtype: StrokeVertexIterator
        """
        ...

    def reversed(self) -> StrokeVertexIterator:
        """Returns a StrokeVertexIterator that traverses stroke vertices in the
        reversed order.

                :return: A StrokeVertexIterator traversing stroke vertices backward.
                :rtype: StrokeVertexIterator
        """
        ...

class TVertex:
    """Class hierarchy: `Interface0D` > `ViewVertex` > `TVertex`Class to define a T vertex, i.e. an intersection between two edges.
    It points towards two SVertex and four ViewEdges. Among the
    ViewEdges, two are front and the other two are back. Basically a
    front edge hides part of a back edge. So, among the back edges, one
    is of invisibility N and the other of invisibility N+1.
    """

    back_svertex: SVertex
    """ The SVertex that is further away from the viewpoint.

    :type: SVertex
    """

    front_svertex: SVertex
    """ The SVertex that is closer to the viewpoint.

    :type: SVertex
    """

    id: Id
    """ The Id of this TVertex.

    :type: Id
    """

    def __init__(self):
        """Default constructor."""
        ...

    def get_mate(self, viewedge: ViewEdge) -> ViewEdge:
        """Returns the mate edge of the ViewEdge given as argument. If the
        ViewEdge is frontEdgeA, frontEdgeB is returned. If the ViewEdge is
        frontEdgeB, frontEdgeA is returned. Same for back edges.

                :param viewedge: A ViewEdge object.
                :type viewedge: ViewEdge
                :return: The mate edge of the given ViewEdge.
                :rtype: ViewEdge
        """
        ...

    def get_svertex(self, fedge: FEdge) -> FEdge:
        """Returns the SVertex (among the 2) belonging to the given FEdge.

        :param fedge: An FEdge object.
        :type fedge: FEdge
        :return: The SVertex belonging to the given FEdge.
        :rtype: SVertex
        """
        ...

class UnaryFunction0D:
    """Base class for Unary Functions (functors) working on
    `Interface0DIterator`. A unary function will be used by
    invoking __call__() on an Interface0DIterator. In Python, several
    different subclasses of UnaryFunction0D are used depending on the
    types of functors' return values. For example, you would inherit from
    a `UnaryFunction0DDouble` if you wish to define a function that
    returns a double value. Available UnaryFunction0D subclasses are:
    """

    name: str
    """ The name of the unary 0D function.

    :type: str
    """

class UnaryFunction0DDouble:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DDouble`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return a float value.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction0DEdgeNature:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DEdgeNature`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return a `Nature` object.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction0DFloat:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DFloat`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return a float value.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction0DId:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DId`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return an `Id` object.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction0DMaterial:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DMaterial`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return a `Material` object.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction0DUnsigned:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DUnsigned`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return an int value.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction0DVec2f:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DVec2f`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return a 2D vector.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction0DVec3f:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DVec3f`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return a 3D vector.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction0DVectorViewShape:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DVectorViewShape`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return a list of `ViewShape`
    objects.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction0DViewShape:
    """Class hierarchy: `UnaryFunction0D` > `UnaryFunction0DViewShape`Base class for unary functions (functors) that work on
    `Interface0DIterator` and return a `ViewShape` object.
    """

    def __init__(self):
        """Default constructor."""
        ...

class UnaryFunction1D:
    """Base class for Unary Functions (functors) working on
    `Interface1D`. A unary function will be used by invoking
    __call__() on an Interface1D. In Python, several different subclasses
    of UnaryFunction1D are used depending on the types of functors' return
    values. For example, you would inherit from a
    `UnaryFunction1DDouble` if you wish to define a function that
    returns a double value. Available UnaryFunction1D subclasses are:
    """

    name: str
    """ The name of the unary 1D function.

    :type: str
    """

class UnaryFunction1DDouble:
    """Class hierarchy: `UnaryFunction1D` > `UnaryFunction1DDouble`Base class for unary functions (functors) that work on
    `Interface1D` and return a float value.
    """

    integration_type: IntegrationType
    """ The integration method.

    :type: IntegrationType
    """

    def __init__(self):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

        """
        ...

    def __init__(self, integration_type: IntegrationType):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

                :param integration_type: An integration method.
                :type integration_type: IntegrationType
        """
        ...

class UnaryFunction1DEdgeNature:
    """Class hierarchy: `UnaryFunction1D` > `UnaryFunction1DEdgeNature`Base class for unary functions (functors) that work on
    `Interface1D` and return a `Nature` object.
    """

    integration_type: IntegrationType
    """ The integration method.

    :type: IntegrationType
    """

    def __init__(self):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

        """
        ...

    def __init__(self, integration_type: IntegrationType):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

                :param integration_type: An integration method.
                :type integration_type: IntegrationType
        """
        ...

class UnaryFunction1DFloat:
    """Class hierarchy: `UnaryFunction1D` > `UnaryFunction1DFloat`Base class for unary functions (functors) that work on
    `Interface1D` and return a float value.
    """

    integration_type: IntegrationType
    """ The integration method.

    :type: IntegrationType
    """

    def __init__(self):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

        """
        ...

    def __init__(self, integration_type: IntegrationType):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

                :param integration_type: An integration method.
                :type integration_type: IntegrationType
        """
        ...

class UnaryFunction1DUnsigned:
    """Class hierarchy: `UnaryFunction1D` > `UnaryFunction1DUnsigned`Base class for unary functions (functors) that work on
    `Interface1D` and return an int value.
    """

    integration_type: IntegrationType
    """ The integration method.

    :type: IntegrationType
    """

    def __init__(self):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

        """
        ...

    def __init__(self, integration_type: IntegrationType):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

                :param integration_type: An integration method.
                :type integration_type: IntegrationType
        """
        ...

class UnaryFunction1DVec2f:
    """Class hierarchy: `UnaryFunction1D` > `UnaryFunction1DVec2f`Base class for unary functions (functors) that work on
    `Interface1D` and return a 2D vector.
    """

    integration_type: IntegrationType
    """ The integration method.

    :type: IntegrationType
    """

    def __init__(self):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

        """
        ...

    def __init__(self, integration_type: IntegrationType):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

                :param integration_type: An integration method.
                :type integration_type: IntegrationType
        """
        ...

class UnaryFunction1DVec3f:
    """Class hierarchy: `UnaryFunction1D` > `UnaryFunction1DVec3f`Base class for unary functions (functors) that work on
    `Interface1D` and return a 3D vector.
    """

    integration_type: IntegrationType
    """ The integration method.

    :type: IntegrationType
    """

    def __init__(self):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

        """
        ...

    def __init__(self, integration_type: IntegrationType):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

                :param integration_type: An integration method.
                :type integration_type: IntegrationType
        """
        ...

class UnaryFunction1DVectorViewShape:
    """Class hierarchy: `UnaryFunction1D` > `UnaryFunction1DVectorViewShape`Base class for unary functions (functors) that work on
    `Interface1D` and return a list of `ViewShape`
    objects.
    """

    integration_type: IntegrationType
    """ The integration method.

    :type: IntegrationType
    """

    def __init__(self):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

        """
        ...

    def __init__(self, integration_type: IntegrationType):
        """Builds a unary 1D function using the default constructor
        or the integration method given as an argument.

                :param integration_type: An integration method.
                :type integration_type: IntegrationType
        """
        ...

class UnaryFunction1DVoid:
    """Class hierarchy: `UnaryFunction1D` > `UnaryFunction1DVoid`Base class for unary functions (functors) working on
    `Interface1D`.
    """

    integration_type: IntegrationType
    """ The integration method.

    :type: IntegrationType
    """

    def __init__(self):
        """Builds a unary 1D function using either a default constructor
        or the integration method given as an argument.

        """
        ...

    def __init__(self, integration_type: IntegrationType):
        """Builds a unary 1D function using either a default constructor
        or the integration method given as an argument.

                :param integration_type: An integration method.
                :type integration_type: IntegrationType
        """
        ...

class UnaryPredicate0D:
    """Base class for unary predicates that work on
    `Interface0DIterator`. A UnaryPredicate0D is a functor that
    evaluates a condition on an Interface0DIterator and returns true or
    false depending on whether this condition is satisfied or not. The
    UnaryPredicate0D is used by invoking its __call__() method. Any
    inherited class must overload the __call__() method.
    """

    name: str
    """ The name of the unary 0D predicate.

    :type: str
    """

    def __init__(self):
        """Default constructor."""
        ...

    def __call__(self, it: Interface0DIterator) -> Interface0DIterator:
        """Must be overload by inherited classes.

                :param it: The Interface0DIterator pointing onto the Interface0D at
        which we wish to evaluate the predicate.
                :type it: Interface0DIterator
                :return: True if the condition is satisfied, false otherwise.
                :rtype: bool
        """
        ...

class UnaryPredicate1D:
    """Base class for unary predicates that work on `Interface1D`. A
    UnaryPredicate1D is a functor that evaluates a condition on a
    Interface1D and returns true or false depending on whether this
    condition is satisfied or not. The UnaryPredicate1D is used by
    invoking its __call__() method. Any inherited class must overload the
    __call__() method.
    """

    name: str
    """ The name of the unary 1D predicate.

    :type: str
    """

    def __init__(self):
        """Default constructor."""
        ...

    def __call__(self, inter: Interface1D) -> Interface1D:
        """Must be overload by inherited classes.

        :param inter: The Interface1D on which we wish to evaluate the predicate.
        :type inter: Interface1D
        :return: True if the condition is satisfied, false otherwise.
        :rtype: bool
        """
        ...

class ViewEdge:
    """Class hierarchy: `Interface1D` > `ViewEdge`Class defining a ViewEdge. A ViewEdge in an edge of the image graph.
    it connects two `ViewVertex` objects. It is made by connecting
    a set of FEdges.
    """

    chaining_time_stamp: typing.Any
    """ The time stamp of this ViewEdge."""

    first_fedge: FEdge
    """ The first FEdge that constitutes this ViewEdge.

    :type: FEdge
    """

    first_viewvertex: ViewVertex
    """ The first ViewVertex.

    :type: ViewVertex
    """

    id: Id
    """ The Id of this ViewEdge.

    :type: Id
    """

    is_closed: bool
    """ True if this ViewEdge forms a closed loop.

    :type: bool
    """

    last_fedge: FEdge
    """ The last FEdge that constitutes this ViewEdge.

    :type: FEdge
    """

    last_viewvertex: ViewVertex
    """ The second ViewVertex.

    :type: ViewVertex
    """

    nature: Nature
    """ The nature of this ViewEdge.

    :type: Nature
    """

    occludee: ViewShape
    """ The shape that is occluded by the ViewShape to which this ViewEdge
belongs to. If no object is occluded, this property is set to None.

    :type: ViewShape
    """

    qi: typing.Any
    """ The quantitative invisibility."""

    viewshape: ViewShape
    """ The ViewShape to which this ViewEdge belongs to.

    :type: ViewShape
    """

    def __init__(self):
        """Builds a `ViewEdge` using the default constructor or the copy constructor."""
        ...

    def __init__(self, brother: ViewEdge):
        """Builds a `ViewEdge` using the default constructor or the copy constructor.

        :param brother: A ViewEdge object.
        :type brother: ViewEdge
        """
        ...

    def update_fedges(self):
        """Sets Viewedge to this for all embedded fedges."""
        ...

class ViewEdgeIterator:
    """Class hierarchy: `Iterator` > `ViewEdgeIterator`Base class for iterators over ViewEdges of the `ViewMap` Graph.
    Basically the increment() operator of this class should be able to
    take the decision of "where" (on which ViewEdge) to go when pointing
    on a given ViewEdge.
    """

    begin: ViewEdge
    """ The first ViewEdge used for the iteration.

    :type: ViewEdge
    """

    current_edge: ViewEdge
    """ The ViewEdge object currently pointed by this iterator.

    :type: ViewEdge
    """

    object: ViewEdge
    """ The ViewEdge object currently pointed by this iterator.

    :type: ViewEdge
    """

    orientation: bool
    """ The orientation of the pointed ViewEdge in the iteration.
If true, the iterator looks for the next ViewEdge among those ViewEdges
that surround the ending ViewVertex of the "begin" ViewEdge. If false,
the iterator searches over the ViewEdges surrounding the ending ViewVertex
of the "begin" ViewEdge.

    :type: bool
    """

    def __init__(self, begin=None, orientation: bool = True):
        """Builds a ViewEdgeIterator from a starting ViewEdge and its
        orientation or the copy constructor.

                :param begin: The ViewEdge from where to start the iteration.
                :param orientation: If true, we'll look for the next ViewEdge among
        the ViewEdges that surround the ending ViewVertex of begin. If
        false, we'll search over the ViewEdges surrounding the ending
        ViewVertex of begin.
                :type orientation: bool
        """
        ...

    def __init__(self, brother: ViewEdgeIterator):
        """Builds a ViewEdgeIterator from a starting ViewEdge and its
        orientation or the copy constructor.

                :param brother: A ViewEdgeIterator object.
                :type brother: ViewEdgeIterator
        """
        ...

    def change_orientation(self):
        """Changes the current orientation."""
        ...

class ViewMap:
    """Class defining the ViewMap."""

    scene_bbox: BBox
    """ The 3D bounding box of the scene.

    :type: BBox
    """

    def __init__(self):
        """Default constructor."""
        ...

    def get_closest_fedge(self, x, y):
        """Gets the FEdge nearest to the 2D point specified as arguments.

        :param x: X coordinate of a 2D point.
        :param y: Y coordinate of a 2D point.
        :return: The FEdge nearest to the specified 2D point.
        :rtype: FEdge
        """
        ...

    def get_closest_viewedge(self, x, y):
        """Gets the ViewEdge nearest to the 2D point specified as arguments.

        :param x: X coordinate of a 2D point.
        :param y: Y coordinate of a 2D point.
        :return: The ViewEdge nearest to the specified 2D point.
        :rtype: ViewEdge
        """
        ...

class ViewShape:
    """Class gathering the elements of the ViewMap (i.e., `ViewVertex`
    and `ViewEdge`) that are issued from the same input shape.
    """

    edges: typing.List[ViewEdge]
    """ The list of ViewEdge objects contained in this ViewShape.

    :type: typing.List[ViewEdge]
    """

    id: Id
    """ The Id of this ViewShape.

    :type: Id
    """

    library_path: typing.Union[str, typing.Any]
    """ The library path of the ViewShape.

    :type: typing.Union[str, typing.Any]
    """

    name: str
    """ The name of the ViewShape.

    :type: str
    """

    sshape: SShape
    """ The SShape on top of which this ViewShape is built.

    :type: SShape
    """

    vertices: typing.List[ViewVertex]
    """ The list of ViewVertex objects contained in this ViewShape.

    :type: typing.List[ViewVertex]
    """

    def __init__(self):
        """Builds a `ViewShape` using the default constructor,
        copy constructor, or from a `SShape`.

        """
        ...

    def __init__(self, brother: ViewShape):
        """Builds a `ViewShape` using the default constructor,
        copy constructor, or from a `SShape`.

                :param brother: A ViewShape object.
                :type brother: ViewShape
        """
        ...

    def __init__(self, sshape: SShape):
        """Builds a `ViewShape` using the default constructor,
        copy constructor, or from a `SShape`.

                :param sshape: An SShape object.
                :type sshape: SShape
        """
        ...

    def add_edge(self, edge: ViewEdge):
        """Adds a ViewEdge to the list of ViewEdge objects.

        :param edge: A ViewEdge object.
        :type edge: ViewEdge
        """
        ...

    def add_vertex(self, vertex: ViewVertex):
        """Adds a ViewVertex to the list of the ViewVertex objects.

        :param vertex: A ViewVertex object.
        :type vertex: ViewVertex
        """
        ...

class ViewVertex:
    """Class hierarchy: `Interface0D` > `ViewVertex`Class to define a view vertex. A view vertex is a feature vertex
    corresponding to a point of the image graph, where the characteristics
    of an edge (e.g., nature and visibility) might change. A
    `ViewVertex` can be of two kinds: A `TVertex` when it
    corresponds to the intersection between two ViewEdges or a
    `NonTVertex` when it corresponds to a vertex of the initial
    input mesh (it is the case for vertices such as corners for example).
    Thus, this class can be specialized into two classes, the
    `TVertex` class and the `NonTVertex` class.
    """

    nature: Nature
    """ The nature of this ViewVertex.

    :type: Nature
    """

    def edges_begin(self) -> Nature:
        """Returns an iterator over the ViewEdges that goes to or comes from
        this ViewVertex pointing to the first ViewEdge of the list. The
        orientedViewEdgeIterator allows to iterate in CCW order over these
        ViewEdges and to get the orientation for each ViewEdge
        (incoming/outgoing).

                :return: An orientedViewEdgeIterator pointing to the first ViewEdge.
                :rtype: orientedViewEdgeIterator
        """
        ...

    def edges_end(self) -> orientedViewEdgeIterator:
        """Returns an orientedViewEdgeIterator over the ViewEdges around this
        ViewVertex, pointing after the last ViewEdge.

                :return: An orientedViewEdgeIterator pointing after the last ViewEdge.
                :rtype: orientedViewEdgeIterator
        """
        ...

    def edges_iterator(self, edge: ViewEdge) -> ViewEdge:
        """Returns an orientedViewEdgeIterator pointing to the ViewEdge given
        as argument.

                :param edge: A ViewEdge object.
                :type edge: ViewEdge
                :return: An orientedViewEdgeIterator pointing to the given ViewEdge.
                :rtype: orientedViewEdgeIterator
        """
        ...

class orientedViewEdgeIterator:
    """Class hierarchy: `Iterator` > `orientedViewEdgeIterator`Class representing an iterator over oriented ViewEdges around a
    `ViewVertex`. This iterator allows a CCW iteration (in the image
    plane). An instance of an orientedViewEdgeIterator can only be
    obtained from a ViewVertex by calling edges_begin() or edges_end().
    """

    object: typing.Any
    """ The oriented ViewEdge (i.e., a tuple of the pointed ViewEdge and a boolean
value) currently pointed to by this iterator. If the boolean value is true,
the ViewEdge is incoming."""

    def __init__(self):
        """Creates an `orientedViewEdgeIterator` using either the
        default constructor or the copy constructor.

        """
        ...

    def __init__(self, iBrother: orientedViewEdgeIterator):
        """Creates an `orientedViewEdgeIterator` using either the
        default constructor or the copy constructor.

                :param iBrother: An orientedViewEdgeIterator object.
                :type iBrother: orientedViewEdgeIterator
        """
        ...
