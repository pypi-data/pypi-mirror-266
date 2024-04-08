import typing
import bpy_types

GenericType = typing.TypeVar("GenericType")

class SceneButtonsPanel:
    """ """

    bl_context: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

class SCENE_PT_audio(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_custom_props(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_order: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_keyframing_settings(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_parent_id: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_keyframing_settings(self, context, layout, ks, ksp):
        """

        :param context:
        :param layout:
        :param ks:
        :param ksp:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_keying_set_paths(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_parent_id: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_keyframing_settings(self, context, layout, ks, ksp):
        """

        :param context:
        :param layout:
        :param ks:
        :param ksp:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_keying_sets(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_keyframing_settings(self, context, layout, ks, ksp):
        """

        :param context:
        :param layout:
        :param ks:
        :param ksp:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_physics(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_header(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_rigid_body_cache(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_parent_id: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_rigid_body_field_weights(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_parent_id: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_rigid_body_world(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_header(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_rigid_body_world_settings(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_parent_id: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_scene(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_simulation(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_PT_unit(bpy_types._GenericUI):
    """ """

    bl_context: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SCENE_UL_keying_set_paths(bpy_types._GenericUI):
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw_item(
        self,
        _context,
        layout,
        _data,
        item,
        icon,
        _active_data,
        _active_propname,
        _index,
    ):
        """

        :param _context:
        :param layout:
        :param _data:
        :param item:
        :param icon:
        :param _active_data:
        :param _active_propname:
        :param _index:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_resolve(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SceneKeyingSetsPanel:
    """ """

    def draw_keyframing_settings(self, context, layout, ks, ksp):
        """

        :param context:
        :param layout:
        :param ks:
        :param ksp:
        """
        ...

class RigidBodySubPanel(SceneButtonsPanel):
    """ """

    bl_context: typing.Any
    """ """

    bl_parent_id: typing.Any
    """ """

    bl_region_type: typing.Any
    """ """

    bl_space_type: typing.Any
    """ """

    def poll(self, context):
        """

        :param context:
        """
        ...
