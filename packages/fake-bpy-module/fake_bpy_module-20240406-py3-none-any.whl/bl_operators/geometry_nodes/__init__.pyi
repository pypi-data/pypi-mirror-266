import typing
import bpy_types

GenericType = typing.TypeVar("GenericType")

class BakeNodeItemAddOperator(bpy_types.Operator):
    """ """

    active_index_name: typing.Any
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    default_socket_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    items_name: typing.Any
    """ """

    node_type: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_node(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class BakeNodeItemMoveOperator(bpy_types.Operator):
    """ """

    active_index_name: typing.Any
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    items_name: typing.Any
    """ """

    node_type: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_node(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class BakeNodeItemRemoveOperator(bpy_types.Operator):
    """ """

    active_index_name: typing.Any
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    items_name: typing.Any
    """ """

    node_type: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_node(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class NodeOperator:
    """ """

    def get_node(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

class IndexSwitchItemAddOperator(bpy_types.Operator):
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class IndexSwitchItemRemoveOperator(bpy_types.Operator):
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class MoveModifierToNodes(bpy_types.Operator):
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class NewGeometryNodeGroupTool(bpy_types.Operator):
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class NewGeometryNodeTreeAssign(bpy_types.Operator):
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class NewGeometryNodesModifier(bpy_types.Operator):
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class RepeatZoneItemAddOperator(bpy_types.Operator):
    """ """

    active_index_name: typing.Any
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    default_socket_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    input_node_type: typing.Any
    """ """

    items_name: typing.Any
    """ """

    output_node_type: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_node(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class RepeatZoneItemMoveOperator(bpy_types.Operator):
    """ """

    active_index_name: typing.Any
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    input_node_type: typing.Any
    """ """

    items_name: typing.Any
    """ """

    output_node_type: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_node(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class RepeatZoneItemRemoveOperator(bpy_types.Operator):
    """ """

    active_index_name: typing.Any
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    input_node_type: typing.Any
    """ """

    items_name: typing.Any
    """ """

    output_node_type: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_node(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class ZoneOperator:
    """ """

    def get_node(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

class SimulationZoneItemAddOperator(bpy_types.Operator):
    """ """

    active_index_name: typing.Any
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    default_socket_type: typing.Any
    """ """

    id_data: typing.Any
    """ """

    input_node_type: typing.Any
    """ """

    items_name: typing.Any
    """ """

    output_node_type: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_node(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SimulationZoneItemMoveOperator(bpy_types.Operator):
    """ """

    active_index_name: typing.Any
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    input_node_type: typing.Any
    """ """

    items_name: typing.Any
    """ """

    output_node_type: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_node(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SimulationZoneItemRemoveOperator(bpy_types.Operator):
    """ """

    active_index_name: typing.Any
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    input_node_type: typing.Any
    """ """

    items_name: typing.Any
    """ """

    output_node_type: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_node(self, context):
        """

        :param context:
        """
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

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class SocketItemAddOperator:
    """ """

    active_index_name: typing.Any
    """ """

    default_socket_type: typing.Any
    """ """

    items_name: typing.Any
    """ """

    def execute(self, context):
        """

        :param context:
        """
        ...

class SocketItemRemoveOperator:
    """ """

    active_index_name: typing.Any
    """ """

    items_name: typing.Any
    """ """

    def execute(self, context):
        """

        :param context:
        """
        ...

class SocketMoveItemOperator:
    """ """

    active_index_name: typing.Any
    """ """

    items_name: typing.Any
    """ """

    def execute(self, context):
        """

        :param context:
        """
        ...

class BakeNodeOperator(NodeOperator):
    """ """

    active_index_name: typing.Any
    """ """

    items_name: typing.Any
    """ """

    node_type: typing.Any
    """ """

    def get_node(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

class RepeatZoneOperator(ZoneOperator):
    """ """

    active_index_name: typing.Any
    """ """

    input_node_type: typing.Any
    """ """

    items_name: typing.Any
    """ """

    output_node_type: typing.Any
    """ """

    def get_node(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

class SimulationZoneOperator(ZoneOperator):
    """ """

    active_index_name: typing.Any
    """ """

    input_node_type: typing.Any
    """ """

    items_name: typing.Any
    """ """

    output_node_type: typing.Any
    """ """

    def get_node(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

def add_empty_geometry_node_group(name):
    """ """

    ...

def edit_geometry_nodes_modifier_poll(context):
    """ """

    ...

def geometry_modifier_poll(context):
    """ """

    ...

def geometry_node_group_empty_modifier_new(name):
    """ """

    ...

def geometry_node_group_empty_new(name):
    """ """

    ...

def geometry_node_group_empty_tool_new(context):
    """ """

    ...

def get_context_modifier(context):
    """ """

    ...

def get_enabled_socket_with_name(sockets, name):
    """ """

    ...

def get_socket_with_identifier(sockets, identifier):
    """ """

    ...

def modifier_attribute_name_get(modifier, identifier):
    """ """

    ...

def modifier_input_use_attribute(modifier, identifier):
    """ """

    ...

def socket_idname_to_attribute_type(idname):
    """ """

    ...
