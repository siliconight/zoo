@tool
extends VBoxContainer

## The Zoo Importer dock. Point it at a manifest, hit Import, and every member
## GLB is instanced into the open scene in a grid under one container node.

var _manifest_edit: LineEdit
var _spacing: SpinBox
var _status: Label
var _dialog: FileDialog


func _ready() -> void:
	add_theme_constant_override("separation", 6)
	custom_minimum_size = Vector2(240, 0)

	var title := Label.new()
	title.text = "Zoo Importer"
	add_child(title)

	var help := Label.new()
	help.text = "Load a .family.json / .habitat.json and drop its GLBs into the open scene."
	help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	help.modulate = Color(1, 1, 1, 0.7)
	add_child(help)

	var row := HBoxContainer.new()
	add_child(row)
	_manifest_edit = LineEdit.new()
	_manifest_edit.placeholder_text = "res://models/xxx.family.json"
	_manifest_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(_manifest_edit)
	var browse := Button.new()
	browse.text = "Browse"
	browse.pressed.connect(_on_browse)
	row.add_child(browse)

	var srow := HBoxContainer.new()
	add_child(srow)
	var slabel := Label.new()
	slabel.text = "Gap between assets (m)"
	slabel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	srow.add_child(slabel)
	_spacing = SpinBox.new()
	_spacing.min_value = 0.0
	_spacing.max_value = 10.0
	_spacing.step = 0.1
	_spacing.value = 0.5
	srow.add_child(_spacing)

	var go := Button.new()
	go.text = "Import into scene"
	go.pressed.connect(_on_import)
	add_child(go)

	_status = Label.new()
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_status)

	_dialog = FileDialog.new()
	_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	_dialog.access = FileDialog.ACCESS_RESOURCES
	_dialog.filters = PackedStringArray([
		"*.family.json ; Zoo family",
		"*.habitat.json ; Zoo habitat",
		"*.json ; JSON",
	])
	_dialog.file_selected.connect(func(p: String) -> void: _manifest_edit.text = p)
	add_child(_dialog)


func _on_browse() -> void:
	_dialog.popup_centered_ratio(0.6)


func _set_status(msg: String) -> void:
	if _status:
		_status.text = msg


func _on_import() -> void:
	var path := _manifest_edit.text.strip_edges()
	if path.is_empty():
		_set_status("Pick a manifest first.")
		return
	if not FileAccess.file_exists(path):
		_set_status("Not found: " + path)
		return

	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(data) != TYPE_DICTIONARY:
		_set_status("Not a valid Zoo manifest.")
		return

	# family manifests list "specimens", habitat manifests list "members"
	var items: Array = []
	var kind := ""
	var id := ""
	var zoo: Dictionary = data.get("zoo", {})
	if data.has("specimens"):
		items = data["specimens"]
		kind = "Family"
		id = str(zoo.get("family_id", "family"))
	elif data.has("members"):
		items = data["members"]
		kind = "Habitat"
		id = str(zoo.get("habitat_id", "habitat"))
	else:
		_set_status("No 'specimens' or 'members' in that manifest.")
		return

	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		_set_status("Open a scene first (Scene > New Scene > 3D Scene).")
		return

	var container := Node3D.new()
	container.name = "Zoo%s_%s" % [kind, id]
	scene_root.add_child(container)
	container.owner = scene_root

	var base_dir := path.get_base_dir()
	var gap: float = _spacing.value
	var missing := 0
	var instances := []

	for item in items:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var files: Dictionary = item.get("files", {})
		var glb_name := str(files.get("glb", ""))
		if glb_name.is_empty():
			continue
		var glb_path := base_dir.path_join(glb_name)
		if not ResourceLoader.exists(glb_path):
			missing += 1
			push_warning("Zoo Importer: GLB not found: " + glb_path)
			continue
		var packed: PackedScene = load(glb_path)
		if packed == null:
			missing += 1
			continue
		var inst: Node = packed.instantiate()
		inst.name = str(item.get("specimen_id", "zoo_asset"))
		container.add_child(inst)
		inst.owner = scene_root
		if inst is Node3D:
			instances.append(inst)

	_layout_row_pack(instances, gap)

	var msg := "%s '%s': imported %d asset(s)." % [kind, id, instances.size()]
	if missing > 0:
		msg += " %d GLB(s) not found next to the manifest — copy the .glb files into %s." % [missing, base_dir]
	_set_status(msg)


## --- layout -----------------------------------------------------------------

## Pack instances edge-to-edge in rows using each one's real footprint, so
## nothing overlaps regardless of size. Wraps to a new row past ~8 m wide.
func _layout_row_pack(instances: Array, gap: float) -> void:
	const MAX_ROW := 8.0
	var cursor_x := 0.0
	var row_z := 0.0
	var row_depth := 0.0
	for inst in instances:
		var box: AABB = _local_aabb(inst)
		var w: float = maxf(box.size.x, 0.05)
		var dpt: float = maxf(box.size.z, 0.05)
		if cursor_x > 0.0 and cursor_x + w > MAX_ROW:
			cursor_x = 0.0
			row_z += row_depth + gap
			row_depth = 0.0
		# left edge at cursor_x, front edge at row_z; leave Y (assets sit on 0)
		inst.position = Vector3(cursor_x - box.position.x, inst.position.y,
			row_z - box.position.z)
		cursor_x += w + gap
		row_depth = maxf(row_depth, dpt)


## Merged AABB of an instance's visible meshes, in the instance's own space.
## (-colonly collision imports as a StaticBody with no mesh, so it's ignored.)
func _local_aabb(inst: Node3D) -> AABB:
	var acc := AABB()
	var first := true
	var inv := inst.global_transform.affine_inverse()
	for mi in _mesh_instances(inst):
		if mi.mesh == null:
			continue
		var rel := inv * mi.global_transform
		var box: AABB = rel * mi.mesh.get_aabb()
		if first:
			acc = box
			first = false
		else:
			acc = acc.merge(box)
	return acc


func _mesh_instances(node: Node) -> Array:
	var out := []
	if node is MeshInstance3D:
		out.append(node)
	for c in node.get_children():
		out.append_array(_mesh_instances(c))
	return out
