@tool
extends EditorPlugin

## Zoo Importer — reads the .family.json / .habitat.json manifests that the
## Zoo (Blender) tool emits and instances the referenced GLBs into the open
## scene. Collision (-colonly) and attachment (ATT_*) nodes come in through
## Godot's native glTF import, so this plugin only has to place the pieces.

const DockScene := preload("res://addons/zoo_importer/zoo_dock.gd")

var _dock: Control


func _enter_tree() -> void:
	_dock = DockScene.new()
	_dock.name = "Zoo"
	add_control_to_dock(DOCK_SLOT_RIGHT_BL, _dock)


func _exit_tree() -> void:
	if _dock:
		remove_control_from_docks(_dock)
		_dock.free()
		_dock = null
