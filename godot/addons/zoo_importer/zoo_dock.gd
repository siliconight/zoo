@tool
extends VBoxContainer

## The Zoo Importer dock. Point it at a manifest, hit Import, and every member
## GLB is instanced into the open scene in a grid under one container node.

var _manifest_edit: LineEdit
var _spacing: SpinBox
var _status: Label
var _dialog: FileDialog
var _snap_attach: CheckBox
var _snap_free: CheckBox


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

	# --- snap section: anchor a prop onto a socket (Lego-style) -------------
	var sep := HSeparator.new()
	add_child(sep)
	var snap_title := Label.new()
	snap_title.text = "Snap (anchor prop -> socket)"
	add_child(snap_title)
	var snap_help := Label.new()
	snap_help.text = ("Select the prop, then Ctrl-click the host (a table, a "
		+ "character...). Zoo finds the socket and snaps the prop onto it.")
	snap_help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	snap_help.modulate = Color(1, 1, 1, 0.7)
	add_child(snap_help)
	_snap_attach = CheckBox.new()
	_snap_attach.text = "Attach (parent to host, moves with it)"
	_snap_attach.button_pressed = true
	add_child(_snap_attach)
	_snap_free = CheckBox.new()
	_snap_free.text = "Free placement (keep X/Z, drop to surface)"
	_snap_free.button_pressed = false
	add_child(_snap_free)
	var snap_btn := Button.new()
	snap_btn.text = "Snap prop -> socket"
	snap_btn.pressed.connect(_on_snap)
	add_child(snap_btn)
	var unsnap_btn := Button.new()
	unsnap_btn.text = "Unsnap (detach selected prop)"
	unsnap_btn.pressed.connect(_on_unsnap)
	add_child(unsnap_btn)

	_status = Label.new()
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_status)

	_dialog = FileDialog.new()
	_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	_dialog.access = FileDialog.ACCESS_RESOURCES
	_dialog.filters = PackedStringArray([
		"*.family.json ; Zoo family",
		"*.habitat.json ; Zoo habitat",
		"*.exhibit.json ; Zoo exhibit",
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

	# exhibit manifests carry a "scheme" and pre-computed positions
	if data.has("scheme") and data.has("members"):
		_import_exhibit(data, path)
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

	# human-readable container name from the theme (habitat) or prompt (family)
	var label := str(data.get("theme", "")) if kind == "Habitat" else str(data.get("prompt", ""))
	var container := Node3D.new()
	scene_root.add_child(container)
	container.owner = scene_root
	container.name = "Zoo " + (label.capitalize() if not label.is_empty() else id)

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
		var specimen_id := str(item.get("specimen_id", "zoo_asset"))
		var species_str := ""
		if item.has("species"):
			species_str = str(item["species"])              # habitat member
		elif typeof(data.get("species", null)) == TYPE_STRING:
			species_str = str(data["species"])              # family (one species)
		var inst: Node = packed.instantiate()
		container.add_child(inst)
		inst.owner = scene_root
		# readable name ("filing_cabinet" -> "Filing Cabinet"); Godot auto-numbers
		# duplicates. Keep the hash in metadata for traceability.
		inst.name = species_str.capitalize() if not species_str.is_empty() else specimen_id
		inst.set_meta("zoo_specimen_id", specimen_id)
		if inst is Node3D:
			instances.append(inst)

	_layout_row_pack(instances, gap)

	var msg := "%s '%s': imported %d asset(s)." % [kind, id, instances.size()]
	if missing > 0:
		msg += " %d GLB(s) not found next to the manifest — copy the .glb files into %s." % [missing, base_dir]
	_set_status(msg)


## --- snap (Lego anchoring) --------------------------------------------------

## Snap a prop onto a host's socket. Select the prop, then Ctrl-click the host
## (its root — the table, the character). Zoo finds the first ATT_* socket
## inside the host, snaps the prop's anchor onto it, and (by default) parents
## the prop under the host root so it moves with the host. Sockets stay put.
func _on_snap() -> void:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		_set_status("Open a scene first.")
		return
	var sel := EditorInterface.get_selection().get_selected_nodes()
	var nodes3d: Array = []
	for n in sel:
		if n is Node3D:
			nodes3d.append(n)
	if nodes3d.size() < 2:
		_set_status("Select the prop, then Ctrl-click the host (2 nodes).")
		return
	var prop: Node3D = nodes3d[0]
	var host: Node3D = nodes3d[nodes3d.size() - 1]
	if prop == host:
		_set_status("Pick two different nodes (prop + host).")
		return

	# resolve the socket: the host if it's already an ATT_*, else find one in it
	var socket: Node3D = host
	if not str(host.name).begins_with("ATT_"):
		socket = _find_socket(host)
	if socket == null:
		_set_status("No ATT_* socket found on '%s'." % host.name)
		return
	if socket.is_ancestor_of(prop):
		_set_status("'%s' is already inside that host." % prop.name)
		return

	# align the prop's anchor (its origin by default) onto the socket
	if _snap_free.button_pressed:
		# free placement on a surface: keep the prop where it is in X/Z, just
		# drop it to the socket's surface height. Put it anywhere on the table.
		var t := prop.global_transform
		t.origin.y = socket.global_transform.origin.y
		prop.global_transform = t
	else:
		var anchor_local := Transform3D.IDENTITY
		if prop.has_meta("zoo_anchor"):
			anchor_local = prop.get_meta("zoo_anchor")
		prop.global_transform = socket.global_transform * anchor_local.affine_inverse()

	# attach: parent under the host's top-level node so it moves with the host
	# (parenting under the scene-owned root, not the internal socket, so it saves)
	if _snap_attach.button_pressed:
		var host_root := _top_under(socket, scene_root)
		if host_root != null and host_root != prop and not prop.is_ancestor_of(host_root):
			prop.reparent(host_root, true)
			prop.owner = scene_root
			_reown(prop, scene_root)
	var tail := " (attached)" if _snap_attach.button_pressed else ""
	_set_status("Snapped '%s' -> '%s'%s." % [prop.name, socket.name, tail])


## Detach a prop that was attached with Snap: reparent it back to the scene
## root, keeping its world position, so it's free-standing again.
func _on_unsnap() -> void:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		_set_status("Open a scene first.")
		return
	var sel := EditorInterface.get_selection().get_selected_nodes()
	var prop: Node3D = null
	for n in sel:
		if n is Node3D:
			prop = n
			break
	if prop == null:
		_set_status("Select the prop to detach.")
		return
	if prop.get_parent() == scene_root:
		_set_status("'%s' is already free (not attached)." % prop.name)
		return
	prop.reparent(scene_root, true)
	prop.owner = scene_root
	_reown(prop, scene_root)
	_set_status("Detached '%s' — now free-standing." % prop.name)



func _find_socket(node: Node) -> Node3D:
	for c in node.get_children():
		if c is Node3D and str(c.name).begins_with("ATT_"):
			return c
	for c in node.get_children():
		var deep := _find_socket(c)
		if deep != null:
			return deep
	return null


## The top-level node under scene_root that contains `node` (the GLB root).
func _top_under(node: Node, scene_root: Node) -> Node:
	var n := node
	while n.get_parent() != null and n.get_parent() != scene_root:
		n = n.get_parent()
	return n


func _reown(node: Node, root: Node) -> void:
	for c in node.get_children():
		c.owner = root
		_reown(c, root)




## Place an exhibit manifest (zoo/museum): members go at their pre-computed
## positions; props add pedestals, labels, and scale-reference markers.
func _import_exhibit(data: Dictionary, path: String) -> void:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		_set_status("Open a scene first (Scene > New Scene > 3D Scene).")
		return

	var scheme := str(data.get("scheme", "zoo"))
	var ex_name := str(data.get("exhibit", "exhibit"))
	var container := Node3D.new()
	scene_root.add_child(container)
	container.owner = scene_root
	container.name = "Zoo Exhibit %s (%s)" % [ex_name.capitalize(), scheme]

	var base_dir := path.get_base_dir()
	var placed := 0
	var missing := 0

	for m in data.get("members", []):
		if typeof(m) != TYPE_DICTIONARY:
			continue
		var glb_name := str(m.get("glb", ""))
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
		container.add_child(inst)
		inst.owner = scene_root
		if inst is Node3D:
			inst.position = _to_vec3(m.get("pos", [0, 0, 0]))
			inst.rotation.y = float(m.get("rot_y", 0.0))
		var nm := str(m.get("name", "asset"))
		inst.name = nm.capitalize()
		inst.set_meta("zoo_specimen_id", nm)
		placed += 1

	for p in data.get("props", []):
		if typeof(p) != TYPE_DICTIONARY:
			continue
		_spawn_prop(p, container, scene_root)

	var msg := "Exhibit '%s' (%s): placed %d asset(s)." % [ex_name, scheme, placed]
	if missing > 0:
		msg += " %d GLB(s) not found — copy the .glb files into %s." % [missing, base_dir]
	_set_status(msg)


func _to_vec3(a) -> Vector3:
	if typeof(a) == TYPE_ARRAY and a.size() >= 3:
		return Vector3(float(a[0]), float(a[1]), float(a[2]))
	return Vector3.ZERO


func _spawn_prop(p: Dictionary, container: Node3D, owner_root: Node) -> void:
	var kind := str(p.get("type", ""))
	var pos := _to_vec3(p.get("pos", [0, 0, 0]))
	if kind == "label":
		var lab := Label3D.new()
		lab.text = str(p.get("text", ""))
		lab.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		lab.pixel_size = 0.002
		lab.modulate = Color(1, 1, 1)
		container.add_child(lab)
		lab.owner = owner_root
		lab.position = pos
		lab.name = "Label"
		return
	# pedestal / marker are boxes sitting on Y=0 (pos is the floor point)
	var size := _to_vec3(p.get("size", [0.4, 0.4, 0.4]))
	var mi := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = size
	mi.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = (Color(0.7, 0.7, 0.72) if kind == "pedestal"
		else Color(0.35, 0.6, 0.9))
	mi.material_override = mat
	container.add_child(mi)
	mi.owner = owner_root
	mi.position = pos + Vector3(0, size.y * 0.5, 0)
	mi.name = ("Pedestal" if kind == "pedestal" else "ScaleMarker")
	if kind == "marker" and p.has("label"):
		var lab2 := Label3D.new()
		lab2.text = str(p.get("label", ""))
		lab2.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		lab2.pixel_size = 0.003
		container.add_child(lab2)
		lab2.owner = owner_root
		lab2.position = pos + Vector3(0, size.y + 0.1, 0)
		lab2.name = "MarkerLabel"


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
		var rel: Transform3D = inv * mi.global_transform
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
