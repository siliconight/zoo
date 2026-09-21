extends SceneTree

## The engine half of `tools/instancing_probe.py`. Loads a GLB both ways
## Godot can load one and prints the node tree it got, with the instance
## count of anything that arrived as a MultiMesh.
##
## BOTH PATHS, because they are different code in principle and a result
## from one is not a result about the other: `GLTFDocument.append_from_file`
## is what a runtime importer calls, and `load()` on a .glb goes through the
## editor's ResourceImporterScene and its .import settings. Measured
## 2026-09-21 they agreed -- EXT_mesh_gpu_instancing is discarded by both,
## and the node keeps its mesh and loses its instance table.
##
##     godot --headless --path <project> --script instancing_probe.gd
##
## Put the GLB at res://probe.glb, or pass --glb=res://other.glb.
## Prints what it measured. It does not say what follows from it.

const DEFAULT_GLB := "res://probe.glb"


func _describe(n: Node) -> String:
	if n is MultiMeshInstance3D:
		var mm: MultiMesh = (n as MultiMeshInstance3D).multimesh
		if mm == null:
			return "MULTIMESH <null>"
		return "MULTIMESH instances=%d use_colors=%s use_custom=%s" % [
			mm.instance_count, mm.use_colors, mm.use_custom_data]
	if n is MeshInstance3D:
		var m: Mesh = (n as MeshInstance3D).mesh
		if m == null:
			return "MeshInstance3D <no mesh>"
		var verts := 0
		var tris := 0
		for s in m.get_surface_count():
			var arrays: Array = m.surface_get_arrays(s)
			verts += (arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
			var idx: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			tris += (idx.size() / 3) if idx != null else 0
		return "MeshInstance3D surfaces=%d verts=%d tris=%d" % [
			m.get_surface_count(), verts, tris]
	return n.get_class()


func _walk(n: Node, depth: int) -> void:
	print("    ", "  ".repeat(depth), n.name, "  ", _describe(n))
	for c in n.get_children():
		_walk(c, depth + 1)


func _glb_path() -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--glb="):
			return a.substr(6)
	return DEFAULT_GLB


func _init() -> void:
	var path := _glb_path()
	print("[instancing_probe] ", path)

	print("  via GLTFDocument.append_from_file (runtime path)")
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(path, state)
	if err != OK:
		print("    append_from_file failed, error ", err)
	else:
		var root: Node = doc.generate_scene(state)
		# The names the file claimed, so a dropped node is visible as an
		# absence rather than inferred from a count.
		print("    glTF nodes named in the file: ", state.get_nodes().size())
		_walk(root, 1)

	print("  via load() (editor ResourceImporterScene path)")
	var scn: PackedScene = load(path)
	if scn == null:
		print("    load() returned null -- is the file imported?")
	else:
		_walk(scn.instantiate(), 1)

	quit()
