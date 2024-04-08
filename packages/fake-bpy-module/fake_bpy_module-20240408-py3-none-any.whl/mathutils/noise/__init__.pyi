import typing
import mathutils

GenericType = typing.TypeVar("GenericType")

def cell(position: typing.Union[typing.Sequence[float], mathutils.Vector]):
    """Returns cell noise value at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :return: The cell noise value.
    """

    ...

def cell_vector(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
) -> mathutils.Vector:
    """Returns cell noise vector at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :return: The cell noise vector.
    :rtype: mathutils.Vector
    """

    ...

def fractal(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    H,
    lacunarity,
    octaves,
    noise_basis: str = "PERLIN_ORIGINAL",
):
    """Returns the fractal Brownian motion (fBm) noise value from the noise basis at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param H: The fractal increment factor.
    :param lacunarity: The gap between successive frequencies.
    :param octaves: The number of different noise frequencies used.
    :param noise_basis: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_basis: str
    :return: The fractal Brownian motion noise value.
    """

    ...

def hetero_terrain(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    H,
    lacunarity,
    octaves,
    offset,
    noise_basis: str = "PERLIN_ORIGINAL",
):
    """Returns the heterogeneous terrain value from the noise basis at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param H: The fractal dimension of the roughest areas.
    :param lacunarity: The gap between successive frequencies.
    :param octaves: The number of different noise frequencies used.
    :param offset: The height of the terrain above 'sea level'.
    :param noise_basis: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_basis: str
    :return: The heterogeneous terrain value.
    """

    ...

def hybrid_multi_fractal(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    H,
    lacunarity,
    octaves,
    offset,
    gain,
    noise_basis: str = "PERLIN_ORIGINAL",
):
    """Returns hybrid multifractal value from the noise basis at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param H: The fractal dimension of the roughest areas.
    :param lacunarity: The gap between successive frequencies.
    :param octaves: The number of different noise frequencies used.
    :param offset: The height of the terrain above 'sea level'.
    :param gain: Scaling applied to the values.
    :param noise_basis: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_basis: str
    :return: The hybrid multifractal value.
    """

    ...

def multi_fractal(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    H,
    lacunarity,
    octaves,
    noise_basis: str = "PERLIN_ORIGINAL",
):
    """Returns multifractal noise value from the noise basis at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param H: The fractal increment factor.
    :param lacunarity: The gap between successive frequencies.
    :param octaves: The number of different noise frequencies used.
    :param noise_basis: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_basis: str
    :return: The multifractal noise value.
    """

    ...

def noise(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    noise_basis: str = "PERLIN_ORIGINAL",
):
    """Returns noise value from the noise basis at the position specified.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param noise_basis: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_basis: str
    :return: The noise value.
    """

    ...

def noise_vector(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    noise_basis: str = "PERLIN_ORIGINAL",
) -> mathutils.Vector:
    """Returns the noise vector from the noise basis at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param noise_basis: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_basis: str
    :return: The noise vector.
    :rtype: mathutils.Vector
    """

    ...

def random():
    """Returns a random number in the range [0, 1).

    :return: The random number.
    """

    ...

def random_unit_vector(size=3) -> mathutils.Vector:
    """Returns a unit vector with random entries.

    :param size: The size of the vector to be produced, in the range [2, 4].
    :return: The random unit vector.
    :rtype: mathutils.Vector
    """

    ...

def random_vector(size=3) -> mathutils.Vector:
    """Returns a vector with random entries in the range (-1, 1).

    :param size: The size of the vector to be produced.
    :return: The random vector.
    :rtype: mathutils.Vector
    """

    ...

def ridged_multi_fractal(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    H,
    lacunarity,
    octaves,
    offset,
    gain,
    noise_basis: str = "PERLIN_ORIGINAL",
):
    """Returns ridged multifractal value from the noise basis at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param H: The fractal dimension of the roughest areas.
    :param lacunarity: The gap between successive frequencies.
    :param octaves: The number of different noise frequencies used.
    :param offset: The height of the terrain above 'sea level'.
    :param gain: Scaling applied to the values.
    :param noise_basis: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_basis: str
    :return: The ridged multifractal value.
    """

    ...

def seed_set(seed):
    """Sets the random seed used for random_unit_vector, and random.

        :param seed: Seed used for the random generator.
    When seed is zero, the current time will be used instead.
    """

    ...

def turbulence(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    octaves,
    hard: bool,
    noise_basis: str = "PERLIN_ORIGINAL",
    amplitude_scale=0.5,
    frequency_scale=2.0,
):
    """Returns the turbulence value from the noise basis at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param octaves: The number of different noise frequencies used.
    :param hard: Specifies whether returned turbulence is hard (sharp transitions) or soft (smooth transitions).
    :type hard: bool
    :param noise_basis: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_basis: str
    :param amplitude_scale: The amplitude scaling factor.
    :param frequency_scale: The frequency scaling factor
    :return: The turbulence value.
    """

    ...

def turbulence_vector(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    octaves,
    hard: bool,
    noise_basis: str = "PERLIN_ORIGINAL",
    amplitude_scale=0.5,
    frequency_scale=2.0,
) -> mathutils.Vector:
    """Returns the turbulence vector from the noise basis at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param octaves: The number of different noise frequencies used.
    :param hard: Specifies whether returned turbulence is hard (sharp transitions) or soft (smooth transitions).
    :type hard: bool
    :param noise_basis: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_basis: str
    :param amplitude_scale: The amplitude scaling factor.
    :param frequency_scale: The frequency scaling factor
    :return: The turbulence vector.
    :rtype: mathutils.Vector
    """

    ...

def variable_lacunarity(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    distortion,
    noise_type1: str = "PERLIN_ORIGINAL",
    noise_type2: str = "PERLIN_ORIGINAL",
):
    """Returns variable lacunarity noise value, a distorted variety of noise, from noise type 1 distorted by noise type 2 at the specified position.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param distortion: The amount of distortion.
    :param noise_type1: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_type1: str
    :param noise_type2: Enumerator in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE'].
    :type noise_type2: str
    :return: The variable lacunarity noise value.
    """

    ...

def voronoi(
    position: typing.Union[typing.Sequence[float], mathutils.Vector],
    distance_metric: str = "DISTANCE",
    exponent=2.5,
):
    """Returns a list of distances to the four closest features and their locations.

    :param position: The position to evaluate the selected noise function.
    :type position: typing.Union[typing.Sequence[float], mathutils.Vector]
    :param distance_metric: Enumerator in ['DISTANCE', 'DISTANCE_SQUARED', 'MANHATTAN', 'CHEBYCHEV', 'MINKOVSKY', 'MINKOVSKY_HALF', 'MINKOVSKY_FOUR'].
    :type distance_metric: str
    :param exponent: The exponent for Minkowski distance metric.
    :return: A list of distances to the four closest features and their locations.
    """

    ...
