import asyncio

from substance_painter_mcp.server import mcp


def test_all_tools_register_with_fastmcp():
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    assert len(tools) == 84
    assert {
        "create_layer_recipe",
        "run_batch",
        "execute_python",
        "get_effect_parameters",
        "set_effect_parameters",
        "preview_textures",
        "capture_ui",
        "snapshot_layer_tree",
        "insert_mask_effect",
        "inspect_baking",
        "save_project_copy",
        "export_smart_material",
        "export_smart_mask",
        "export_with_profile",
        "get_geometry_mask",
        "set_geometry_mask",
        "plan_layer_recipe",
        "diff_layer_snapshots",
        "insert_smart_material",
        "apply_smart_mask",
        "get_fill_projection",
        "set_fill_projection",
        "get_fill_sources",
        "set_fill_resource",
        "set_fill_projection_advanced",
        "start_bake",
        "get_bake_job",
        "cancel_bake",
        "plan_mesh_reload",
        "start_mesh_reload",
        "get_mesh_reload_job",
        "get_fill_parameters",
        "set_fill_parameters",
        "apply_fill_preset",
        "list_anchor_points",
        "set_fill_anchor_source",
        "inspect_baking_parameters",
        "configure_baking",
        "set_baking_mesh_inputs",
        "capture_baking_preset",
        "apply_baking_preset",
        "preflight_bake",
        "start_batch_bake",
        "set_baking_resource_input",
        "import_project_resource",
        "import_session_resource",
        "get_procedural_inputs",
        "set_procedural_input",
        "plan_project_creation",
        "create_project",
        "get_project_creation_job",
        "save_project",
        "open_project",
        "list_shelves",
        "import_shelf_resource",
        "start_shelf_refresh",
        "get_shelf_refresh_job",
    } <= names


def test_run_batch_chains_results_through_refs(monkeypatch):
    from substance_painter_mcp import server

    calls = []
    monkeypatch.setitem(server._TOOLS, "make", lambda name: {"uid": 41, "name": name, "effects": [{"uid": 9}]})
    monkeypatch.setitem(server._TOOLS, "use", lambda uid, other=None: calls.append((uid, other)) or {"ok": uid})
    result = server.run_batch([
        {"tool": "make", "args": {"name": "a"}},
        {"tool": "use", "args": {"uid": "$0.uid", "other": "$prev.effects.0.uid"}},
        {"tool": "use", "args": {"uid": "$1.ok"}},
    ])
    assert result["failed_steps"] == []
    assert calls == [(41, 9), (41, None)]


def test_run_batch_stops_on_first_error(monkeypatch):
    from substance_painter_mcp import server

    def boom():
        raise ValueError("nope")

    monkeypatch.setitem(server._TOOLS, "boom", boom)
    monkeypatch.setitem(server._TOOLS, "fine", lambda: {})
    result = server.run_batch([{"tool": "boom"}, {"tool": "fine"}])
    assert result["completed"] == 1 and result["failed_steps"] == [0]
    assert "ValueError: nope" in result["steps"][0]["error"]
    result = server.run_batch([{"tool": "boom"}, {"tool": "fine"}], stop_on_error=False)
    assert result["completed"] == 2 and result["steps"][1]["ok"]


def test_run_batch_rejects_nesting_and_unknown_tools():
    from substance_painter_mcp import server

    result = server.run_batch([{"tool": "run_batch", "args": {"steps": []}}, {"tool": "nope"}], stop_on_error=False)
    assert result["failed_steps"] == [0, 1]


def test_execute_python_stays_gated(monkeypatch):
    import pytest
    from substance_painter_mcp import server

    monkeypatch.delenv("SP_MCP_ALLOW_EXECUTE_PYTHON", raising=False)
    with pytest.raises(PermissionError):
        server.execute_python("result = 1")
