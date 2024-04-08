import typing

GenericType = typing.TypeVar("GenericType")

def compute_shader_support_get() -> bool:
    """Are compute shaders supported.

    :return: True when supported, False when not supported.
    :rtype: bool
    """

    ...

def extensions_get():
    """Get supported extensions in the current context.

    :return: Extensions.
    """

    ...

def hdr_support_get() -> bool:
    """Return whether GPU backend supports High Dynamic range for viewport.

    :return: HDR support available.
    :rtype: bool
    """

    ...

def max_batch_indices_get():
    """Get maximum number of vertex array indices.

    :return: Number of indices.
    """

    ...

def max_batch_vertices_get():
    """Get maximum number of vertex array vertices.

    :return: Number of vertices.
    """

    ...

def max_images_get():
    """Get maximum supported number of image units.

    :return: Number of image units.
    """

    ...

def max_texture_layers_get():
    """Get maximum number of layers in texture.

    :return: Number of layers.
    """

    ...

def max_texture_size_get():
    """Get estimated maximum texture size to be able to handle.

    :return: Texture size.
    """

    ...

def max_textures_frag_get():
    """Get maximum supported texture image units used for
    accessing texture maps from the fragment shader.

        :return: Texture image units.
    """

    ...

def max_textures_geom_get():
    """Get maximum supported texture image units used for
    accessing texture maps from the geometry shader.

        :return: Texture image units.
    """

    ...

def max_textures_get():
    """Get maximum supported texture image units used for
    accessing texture maps from the vertex shader and the
    fragment processor.

        :return: Texture image units.
    """

    ...

def max_textures_vert_get():
    """Get maximum supported texture image units used for
    accessing texture maps from the vertex shader.

        :return: Texture image units.
    """

    ...

def max_uniforms_frag_get():
    """Get maximum number of values held in uniform variable
    storage for a fragment shader.

        :return: Number of values.
    """

    ...

def max_uniforms_vert_get():
    """Get maximum number of values held in uniform variable
    storage for a vertex shader.

        :return: Number of values.
    """

    ...

def max_varying_floats_get():
    """Get maximum number of varying variables used by
    vertex and fragment shaders.

        :return: Number of variables.
    """

    ...

def max_vertex_attribs_get():
    """Get maximum number of vertex attributes accessible to
    a vertex shader.

        :return: Number of attributes.
    """

    ...

def max_work_group_count_get(index):
    """Get maximum number of work groups that may be dispatched to a compute shader.

    :param index: Index of the dimension.
    :return: Maximum number of work groups for the queried dimension.
    """

    ...

def max_work_group_size_get(index):
    """Get maximum size of a work group that may be dispatched to a compute shader.

    :param index: Index of the dimension.
    :return: Maximum size of a work group for the queried dimension.
    """

    ...

def shader_image_load_store_support_get() -> bool:
    """Is image load/store supported.

    :return: True when supported, False when not supported.
    :rtype: bool
    """

    ...
