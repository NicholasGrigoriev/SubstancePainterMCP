"""FastMCP server for Adobe Substance 3D Painter."""

from __future__ import annotations

import os
import base64
import re
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP, Image

from .client import PainterRemote
from .operations import PainterOperations


mcp = FastMCP(
    "Substance Painter",
    instructions=(
        "Control the locally running Adobe Substance 3D Painter instance. "
        "Use UIDs from list_layers for edits because layer names may be duplicated."
    ),
)
operations = PainterOperations(PainterRemote())
_TOOLS: dict[str, Callable[..., Any]] = {}


def tool() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register an MCP tool and remember it for run_batch."""
    register = mcp.tool()

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        _TOOLS[fn.__name__] = fn
        return register(fn)

    return decorator


@tool()
def painter_status() -> dict[str, Any]:
    """Check the connection and report Painter, Python API, and project status."""
    return operations.status()


@tool()
def get_project_info() -> dict[str, Any]:
    """Return the current project path and texture-set names."""
    return operations.project_info()


@tool()
def plan_project_creation(
    mesh_file_path: str,
    output_path: str,
    mesh_map_file_paths: list[str] | None = None,
    template_file_path: str | None = None,
    settings: dict[str, Any] | None = None,
    overwrite: bool = False,
    replace_current: bool = False,
    backup_current_path: str | None = None,
    backup_mode: str = "Incremental",
    overwrite_backup: bool = False,
) -> dict[str, Any]:
    """Validate a new project, typed import settings, context switch, and backup."""
    return operations.plan_project_creation(
        mesh_file_path,
        output_path,
        mesh_map_file_paths,
        template_file_path,
        settings,
        overwrite,
        replace_current,
        backup_current_path,
        backup_mode,
        overwrite_backup,
    )


@tool()
def create_project(
    mesh_file_path: str,
    output_path: str,
    mesh_map_file_paths: list[str] | None = None,
    template_file_path: str | None = None,
    settings: dict[str, Any] | None = None,
    overwrite: bool = False,
    replace_current: bool = False,
    backup_current_path: str | None = None,
    backup_mode: str = "Incremental",
    overwrite_backup: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    """Back up an optional current project, create a typed project, and verify its file."""
    return operations.create_project(
        mesh_file_path,
        output_path,
        mesh_map_file_paths,
        template_file_path,
        settings,
        overwrite,
        replace_current,
        backup_current_path,
        backup_mode,
        overwrite_backup,
        confirm,
    )


@tool()
def get_project_creation_job(job_id: str | None = None) -> dict[str, Any]:
    """Read terminal state and file verification for an asynchronous project creation."""
    return operations.get_project_creation_job(job_id)


@tool()
def save_project(mode: str = "Incremental", confirm: bool = False) -> dict[str, Any]:
    """Overwrite and verify the current saved project after explicit confirmation."""
    return operations.save_project(mode, confirm)


@tool()
def open_project(
    project_path: str,
    confirm: bool = False,
    backup_current_path: str | None = None,
    backup_mode: str = "Incremental",
    overwrite_backup: bool = False,
) -> dict[str, Any]:
    """Open an approved .spp, requiring a backup when the current project is dirty."""
    return operations.open_project(
        project_path, confirm, backup_current_path, backup_mode, overwrite_backup
    )


@tool()
def get_capabilities() -> dict[str, Any]:
    """Report runtime-supported channels, blend modes, and version-sensitive features."""
    return operations.capabilities()


@tool()
def audit_project() -> dict[str, Any]:
    """Audit texture sets, channels, layer hygiene, and outdated resources."""
    return operations.audit_project()


@tool()
def inspect_baking(texture_set: str | None = None) -> dict[str, Any]:
    """Inspect enabled bakers, UV tiles, and mesh-map assignments without starting a bake."""
    return operations.inspect_baking(texture_set)


@tool()
def inspect_baking_parameters(
    texture_set: str, baker: str | None = None
) -> dict[str, Any]:
    """Inspect editable common parameters and one baker's typed property metadata."""
    return operations.inspect_baking_parameters(texture_set, baker)


@tool()
def configure_baking(
    texture_set: str,
    enabled: bool | None = None,
    enabled_bakers: list[str] | None = None,
    enabled_uv_tiles: list[int] | None = None,
    curvature_method: str | None = None,
    common_values: dict[str, Any] | None = None,
    baker_values: dict[str, dict[str, Any]] | None = None,
    confirm: bool = False,
) -> dict[str, Any]:
    """Transactionally configure Texture Set, UV tile, common, and per-baker settings."""
    return operations.configure_baking(
        texture_set,
        enabled,
        enabled_bakers,
        enabled_uv_tiles,
        curvature_method,
        common_values,
        baker_values,
        confirm,
    )


@tool()
def set_baking_mesh_inputs(
    texture_set: str,
    high_poly_files: list[str] | None = None,
    cage_file: str | None = None,
    low_as_high: bool | None = None,
    cage_mode: str | None = None,
    confirm: bool = False,
) -> dict[str, Any]:
    """Assign sandboxed high-poly/cage meshes and related common baker settings."""
    return operations.set_baking_mesh_inputs(
        texture_set,
        high_poly_files,
        cage_file,
        low_as_high,
        cage_mode,
        confirm,
    )


@tool()
def set_baking_resource_input(
    texture_set: str,
    parameter: str,
    resource_url: str | None = None,
    baker: str | None = None,
    clear: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    """Set or clear a Resource-typed common/per-baker input transactionally."""
    return operations.set_baking_resource_input(
        texture_set, parameter, resource_url, baker, clear, confirm
    )


@tool()
def capture_baking_preset(
    texture_set: str, bakers: list[str] | None = None
) -> dict[str, Any]:
    """Capture a portable JSON baking preset without filesystem-backed properties."""
    return operations.capture_baking_preset(texture_set, bakers)


@tool()
def apply_baking_preset(
    texture_set: str,
    preset: dict[str, Any],
    confirm: bool = False,
) -> dict[str, Any]:
    """Apply a captured baking preset transactionally after explicit confirmation."""
    return operations.apply_baking_preset(texture_set, preset, confirm)


@tool()
def preflight_bake(texture_sets: list[str] | None = None) -> dict[str, Any]:
    """Validate selected Texture Sets, mesh inputs, UV tiles, and expected mesh maps."""
    return operations.preflight_bake(texture_sets)


@tool()
def start_batch_bake(
    texture_sets: list[str],
    confirm: bool = False,
    backup_path: str | None = None,
    backup_mode: str = "Incremental",
    overwrite_backup: bool = False,
) -> dict[str, Any]:
    """Preflight and start a cancellable multi-Texture-Set bake with result manifests."""
    return operations.start_batch_bake(
        texture_sets, confirm, backup_path, backup_mode, overwrite_backup
    )


@tool()
def start_bake(
    texture_set: str,
    confirm: bool = False,
    backup_path: str | None = None,
    backup_mode: str = "Incremental",
    overwrite_backup: bool = False,
) -> dict[str, Any]:
    """Start an asynchronous mesh-map bake after explicit confirmation."""
    return operations.start_bake(
        texture_set, confirm, backup_path, backup_mode, overwrite_backup
    )


@tool()
def get_bake_job(job_id: str | None = None) -> dict[str, Any]:
    """Return progress and terminal status for the latest or selected bake job."""
    return operations.get_bake_job(job_id)


@tool()
def cancel_bake(job_id: str) -> dict[str, Any]:
    """Request cooperative cancellation of a running bake job."""
    return operations.cancel_bake(job_id)


@tool()
def plan_mesh_reload(
    mesh_file_path: str,
    backup_path: str | None = None,
    backup_mode: str = "Incremental",
    overwrite_backup: bool = False,
    preserve_strokes: bool = True,
    import_cameras: bool = True,
    auto_unwrap_settings: dict[str, Any] | None = None,
    mesh_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a mesh reload and preview texture-set and backup impact."""
    return operations.plan_mesh_reload(
        mesh_file_path,
        backup_path,
        backup_mode,
        overwrite_backup,
        preserve_strokes,
        import_cameras,
        auto_unwrap_settings,
        mesh_settings,
    )


@tool()
def start_mesh_reload(
    mesh_file_path: str,
    confirm: bool = False,
    backup_path: str | None = None,
    backup_mode: str = "Incremental",
    overwrite_backup: bool = False,
    preserve_strokes: bool = True,
    import_cameras: bool = True,
    auto_unwrap_settings: dict[str, Any] | None = None,
    mesh_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Back up and asynchronously reload a mesh after explicit confirmation."""
    return operations.start_mesh_reload(
        mesh_file_path,
        confirm,
        backup_path,
        backup_mode,
        overwrite_backup,
        preserve_strokes,
        import_cameras,
        auto_unwrap_settings,
        mesh_settings,
    )


@tool()
def get_mesh_reload_job(job_id: str | None = None) -> dict[str, Any]:
    """Return status and texture-set changes for the latest mesh reload job."""
    return operations.get_mesh_reload_job(job_id)


@tool()
def list_layers(texture_set: str | None = None, recursive: bool = True) -> dict[str, Any]:
    """List layers with stable UIDs, types, visibility, and optional group children."""
    return operations.list_layers(texture_set=texture_set, recursive=recursive)


@tool()
def find_layers(
    query: str = "",
    node_type: str | None = None,
    visible: bool | None = None,
    texture_set: str | None = None,
) -> dict[str, Any]:
    """Search layers by partial name, exact node type, and visibility."""
    return operations.find_layers(query, node_type, visible, texture_set)


@tool()
def snapshot_layer_tree(texture_set: str | None = None) -> dict[str, Any]:
    """Capture a detailed layer/effect snapshot with a deterministic SHA-256 digest."""
    return operations.snapshot_layer_tree(texture_set)


@tool()
def diff_layer_snapshots(
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    """Compare two layer snapshots by UID and report added, removed, and changed nodes."""
    return operations.diff_layer_snapshots(before, after)


@tool()
def get_geometry_mask(uid: int) -> dict[str, Any]:
    """Inspect a layer's Mesh/UVTile geometry mask and available elements."""
    return operations.get_geometry_mask(uid)


@tool()
def set_geometry_mask(
    uid: int,
    mask_type: str,
    elements: list[str | int],
    inclusion_list: bool = True,
) -> dict[str, Any]:
    """Set a geometry mask using mesh names or standard UDIM numbers."""
    return operations.set_geometry_mask(uid, mask_type, elements, inclusion_list)


@tool()
def create_fill_layer(
    name: str,
    texture_set: str | None = None,
    base_color: list[float] | None = None,
) -> dict[str, Any]:
    """Create a top-level Fill Layer, optionally setting sRGB base color [r,g,b]."""
    return operations.create_fill_layer(name, texture_set, base_color)


@tool()
def create_group(name: str, texture_set: str | None = None) -> dict[str, Any]:
    """Create a top-level layer group."""
    return operations.create_group(name, texture_set)


@tool()
def create_paint_layer(name: str, texture_set: str | None = None) -> dict[str, Any]:
    """Create a top-level Paint Layer."""
    return operations.create_paint_layer(name, texture_set)


@tool()
def plan_layer_recipe(
    recipe: list[dict[str, Any]],
    texture_set: str | None = None,
    backup_path: str | None = None,
    backup_mode: str = "Incremental",
    overwrite_backup: bool = False,
) -> dict[str, Any]:
    """Validate a recipe, resolve channels, and preview backup/mutation scope without editing."""
    return operations.plan_layer_recipe(
        recipe, texture_set, backup_path, backup_mode, overwrite_backup
    )


@tool()
def create_layer_recipe(
    recipe: list[dict[str, Any]],
    texture_set: str | None = None,
    backup_path: str | None = None,
    backup_mode: str = "Incremental",
    overwrite_backup: bool = False,
) -> dict[str, Any]:
    """Create a nested recipe atomically, optionally saving an approved .spp backup first."""
    return operations.create_layer_recipe(
        recipe, texture_set, backup_path, backup_mode, overwrite_backup
    )


@tool()
def insert_smart_material(
    resource_url: str,
    texture_set: str | None = None,
    parent_uid: int | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """Insert a Smart Material resource at stack top or inside a group."""
    return operations.insert_smart_material(resource_url, texture_set, parent_uid, name)


@tool()
def apply_smart_mask(uid: int, resource_url: str) -> dict[str, Any]:
    """Apply a Smart Mask resource to a layer using transactional mask insertion."""
    return operations.apply_smart_mask(uid, resource_url)


@tool()
def set_fill_base_color(uid: int, color: list[float]) -> dict[str, Any]:
    """Set a Fill Layer's base color using its UID and sRGB [r,g,b] values."""
    return operations.set_fill_base_color(uid, color)


@tool()
def get_fill_projection(uid: int) -> dict[str, Any]:
    """Inspect a Fill layer's projection mode and common UV transformation."""
    return operations.get_fill_projection(uid)


@tool()
def get_fill_sources(uid: int) -> dict[str, Any]:
    """Inspect a Fill layer's material or per-channel color/resource sources."""
    return operations.get_fill_sources(uid)


@tool()
def get_procedural_inputs(uid: int, channel: str | None = None) -> dict[str, Any]:
    """Inspect image inputs on Fill, Fill Effect, Generator, or Filter sources."""
    return operations.get_procedural_inputs(uid, channel)


@tool()
def set_procedural_input(
    uid: int,
    input_name: str,
    resource_url: str | None = None,
    channel: str | None = None,
    reset: bool = False,
) -> dict[str, Any]:
    """Connect a resource to a procedural image input or reset it to its default."""
    return operations.set_procedural_input(uid, input_name, resource_url, channel, reset)


@tool()
def get_fill_parameters(uid: int, channel: str | None = None) -> dict[str, Any]:
    """Inspect procedural parameters and presets of a Fill layer, mask Fill, Generator, or Filter.

    Generator/Filter effects (e.g. dirt, edge wear) and mono mask fills take no channel.
    """
    return operations.get_fill_parameters(uid, channel)


@tool()
def set_fill_parameters(
    uid: int,
    values: dict[str, Any],
    channel: str | None = None,
) -> dict[str, Any]:
    """Transactionally update procedural parameters on a Fill layer, mask Fill, Generator, or Filter."""
    return operations.set_fill_parameters(uid, values, channel)


@tool()
def apply_fill_preset(
    uid: int, preset: str, channel: str | None = None
) -> dict[str, Any]:
    """Apply a named preset exposed by a Fill, Generator, or Filter procedural source."""
    return operations.apply_fill_preset(uid, preset, channel)


@tool()
def list_anchor_points(texture_set: str | None = None) -> dict[str, Any]:
    """List Anchor Point effects with owner and Texture Set context."""
    return operations.list_anchor_points(texture_set)


@tool()
def set_fill_anchor_source(
    uid: int,
    anchor_uid: int,
    channel: str | None = None,
    material_mode: bool = False,
) -> dict[str, Any]:
    """Connect an Anchor Point to one Fill channel or the complete material source."""
    return operations.set_fill_anchor_source(uid, anchor_uid, channel, material_mode)


@tool()
def set_fill_resource(
    uid: int,
    resource_url: str,
    channel: str | None = None,
    material_mode: bool = False,
) -> dict[str, Any]:
    """Assign a Painter resource to one Fill channel or to the whole material."""
    return operations.set_fill_resource(uid, resource_url, channel, material_mode)


@tool()
def set_fill_projection(
    uid: int,
    mode: str,
    scale: list[float] | None = None,
    rotation: float | None = None,
    offset: list[float] | None = None,
) -> dict[str, Any]:
    """Set Fill, UV, or Triplanar projection with transactional transform updates."""
    return operations.set_fill_projection(uid, mode, scale, rotation, offset)


@tool()
def set_fill_projection_advanced(
    uid: int,
    mode: str,
    settings: dict[str, Any],
) -> dict[str, Any]:
    """Configure UV, triplanar, planar, spherical, or cylindrical projection details."""
    return operations.set_fill_projection_advanced(uid, mode, settings)


@tool()
def set_fill_channels(
    uid: int,
    values: dict[str, float | list[float]],
) -> dict[str, Any]:
    """Set and enable multiple uniform Fill channels, such as Roughness or Metallic."""
    return operations.set_fill_channels(uid, values)


@tool()
def set_active_channels(uid: int, channels: list[str]) -> dict[str, Any]:
    """Replace a Fill or Paint layer's active channel set by UID."""
    return operations.set_active_channels(uid, channels)


@tool()
def set_layer_mask(uid: int, enabled: bool, background: str = "Black") -> dict[str, Any]:
    """Add/update or remove a layer mask; backgrounds are reported by get_capabilities."""
    return operations.set_layer_mask(uid, enabled, background)


@tool()
def insert_mask_effect(
    uid: int,
    effect_type: str,
    resource_url: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """Insert a mask effect: fill, paint, generator, filter, levels, anchor, smart_mask,
    color_selection (ID-map masking), or compare_mask.

    Tune levels/color_selection/compare_mask with set_effect_parameters, and generator or
    filter parameters with set_fill_parameters. Blend mode and opacity of any mask effect
    are set with set_layer_properties (omit channel).
    """
    return operations.insert_mask_effect(uid, effect_type, resource_url, name)


@tool()
def rename_layer(uid: int, name: str) -> dict[str, Any]:
    """Rename a layer or group by UID."""
    return operations.rename_layer(uid, name)


@tool()
def set_layer_properties(
    uid: int,
    visible: bool | None = None,
    opacity: float | None = None,
    blending_mode: str | None = None,
    channel: str | None = None,
) -> dict[str, Any]:
    """Set visibility, opacity, or blend mode of a layer or effect.

    channel defaults to BaseColor for content-stack nodes; omit it for mask-stack effects,
    which are mono-channel (e.g. Multiply/Subtract two mask effects together).
    """
    return operations.set_layer_properties(uid, visible, opacity, blending_mode, channel)


@tool()
def select_layers(uids: list[int]) -> dict[str, Any]:
    """Select one or more layers in Painter by UID."""
    return operations.select_layers(uids)


@tool()
def list_export_presets() -> dict[str, Any]:
    """List built-in and shelf export presets without exporting files."""
    return operations.list_export_presets()


@tool()
def inspect_export_preset(
    preset: str,
    texture_set: str | None = None,
) -> dict[str, Any]:
    """Resolve an export preset and preview its map names without writing files."""
    return operations.inspect_export_preset(preset, texture_set)


@tool()
def list_export_profiles() -> dict[str, Any]:
    """List curated engine export profiles and whether their Painter presets are available."""
    return operations.list_export_profiles()


@tool()
def plan_texture_export(
    output_directory: str,
    preset: str,
    texture_sets: list[str] | None = None,
    size_log2: int | None = None,
    file_format: str | None = None,
    bit_depth: str | None = None,
) -> dict[str, Any]:
    """Validate an export and list exact output files without writing them."""
    return operations.plan_texture_export(
        output_directory, preset, texture_sets, size_log2, file_format, bit_depth
    )


@tool()
def export_textures(
    output_directory: str,
    preset: str,
    texture_sets: list[str] | None = None,
    size_log2: int | None = None,
    file_format: str | None = None,
    bit_depth: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Export textures inside SP_MCP_EXPORT_ROOTS and verify every output file."""
    return operations.export_textures(
        output_directory,
        preset,
        texture_sets,
        size_log2,
        file_format,
        bit_depth,
        overwrite,
    )


@tool()
def plan_profile_export(
    output_directory: str,
    profile: str,
    texture_sets: list[str] | None = None,
    size_log2: int | None = None,
) -> dict[str, Any]:
    """Preview an engine-profile texture export without writing files."""
    return operations.plan_profile_export(output_directory, profile, texture_sets, size_log2)


@tool()
def export_with_profile(
    output_directory: str,
    profile: str,
    texture_sets: list[str] | None = None,
    size_log2: int | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Run a curated export profile inside SP_MCP_EXPORT_ROOTS and verify outputs."""
    return operations.export_with_profile(
        output_directory, profile, texture_sets, size_log2, overwrite
    )


@tool()
def import_project_resource(
    file_path: str,
    usage: str,
    name: str | None = None,
    group: str | None = None,
    confirm: bool = False,
) -> dict[str, Any]:
    """Import and verify a sandboxed resource inside the open Painter project."""
    return operations.import_project_resource(file_path, usage, name, group, confirm)


@tool()
def list_shelves() -> dict[str, Any]:
    """List Painter shelves with paths, write capability, and crawling state."""
    return operations.list_shelves()


@tool()
def import_shelf_resource(
    file_path: str,
    usage: str,
    shelf_name: str | None = None,
    name: str | None = None,
    group: str | None = None,
    confirm: bool = False,
) -> dict[str, Any]:
    """Import and verify a safe resource in an editable shelf or the user shelf."""
    return operations.import_shelf_resource(
        file_path, usage, shelf_name, name, group, confirm
    )


@tool()
def start_shelf_refresh(shelf_name: str, confirm: bool = False) -> dict[str, Any]:
    """Start event-observed discovery for one Painter shelf after confirmation."""
    return operations.start_shelf_refresh(shelf_name, confirm)


@tool()
def get_shelf_refresh_job(job_id: str | None = None) -> dict[str, Any]:
    """Read persistent state for the latest or selected shelf refresh job."""
    return operations.get_shelf_refresh_job(job_id)


@tool()
def import_session_resource(
    file_path: str,
    usage: str,
    name: str | None = None,
    group: str | None = None,
    confirm: bool = False,
) -> dict[str, Any]:
    """Import and verify a sandboxed resource for the current Painter session."""
    return operations.import_session_resource(file_path, usage, name, group, confirm)


@tool()
def list_project_resources() -> dict[str, Any]:
    """List resources referenced by the open project."""
    return operations.list_project_resources()


@tool()
def search_resources(
    query: str,
    limit: int = 50,
    resource_type: str | None = None,
    usage: str | None = None,
) -> dict[str, Any]:
    """Search Painter resources and return identifiers, type, category, and usages."""
    return operations.search_resources(query, limit, resource_type, usage)


@tool()
def find_outdated_resources() -> dict[str, Any]:
    """Plan project-resource replacements without modifying the project."""
    return operations.find_outdated_resources()


@tool()
def replace_outdated_resources(confirm: bool = False) -> dict[str, Any]:
    """Atomically replace all outdated resources after explicit confirm=true."""
    return operations.replace_outdated_resources(confirm)


@tool()
def save_project_copy(
    output_path: str,
    mode: str = "Incremental",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Save a verified .spp copy inside SP_MCP_PROJECT_ROOTS without relocating the project."""
    return operations.save_project_copy(output_path, mode, overwrite)


@tool()
def export_smart_material(
    uid: int,
    name: str,
    output_directory: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Export a group as a verified Smart Material inside SP_MCP_EXPORT_ROOTS."""
    return operations.export_smart_material(uid, name, output_directory, overwrite)


@tool()
def export_smart_mask(
    uid: int,
    name: str,
    output_directory: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Export a layer mask as a verified Smart Mask inside SP_MCP_EXPORT_ROOTS."""
    return operations.export_smart_mask(uid, name, output_directory, overwrite)


@tool()
def delete_layer(uid: int) -> dict[str, Any]:
    """Delete a layer or group by UID. This modifies the open project."""
    return operations.delete_layer(uid)


def _require_raw_python() -> None:
    if os.getenv("SP_MCP_ALLOW_EXECUTE_PYTHON") != "1":
        raise PermissionError(
            "Raw Python execution is disabled. Set SP_MCP_ALLOW_EXECUTE_PYTHON=1 "
            "in the MCP server environment to opt in."
        )


@tool()
def execute_python(code: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run Painter Python in one call (needs SP_MCP_ALLOW_EXECUTE_PYTHON=1).

    The namespace preloads substance_painter plus its modules by short name (layerstack,
    textureset, resource, colormanagement, project, export, baking, source, levels, ui,
    display, application, properties) and `params` (the JSON object you pass). Assign a
    JSON-serialisable value to `result` to return it. print() output comes back as
    `stdout`; exceptions come back as `ok: false` with the full traceback instead of
    aborting. Wrap many layer-stack edits in
    `with layerstack.ScopedModification("name"):` to make them one undo step.
    """
    _require_raw_python()
    return operations.run_python(code, params)


_REF = re.compile(r"^\$(prev|\d+)((?:\.[A-Za-z0-9_]+)*)$")


def _resolve_refs(value: Any, results: list[Any]) -> Any:
    if isinstance(value, str):
        match = _REF.match(value)
        if not match:
            return value
        index = len(results) - 1 if match.group(1) == "prev" else int(match.group(1))
        if not 0 <= index < len(results):
            raise ValueError(f"{value}: step {index} has no result yet")
        current = results[index]
        for key in filter(None, match.group(2).split(".")):
            if isinstance(current, list):
                current = current[int(key)]
            elif isinstance(current, dict):
                current = current[key]
            else:
                raise ValueError(f"{value}: cannot index {type(current).__name__} with {key!r}")
        return current
    if isinstance(value, list):
        return [_resolve_refs(item, results) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_refs(item, results) for key, item in value.items()}
    return value


@tool()
def run_batch(steps: list[dict[str, Any]], stop_on_error: bool = True) -> dict[str, Any]:
    """Run many tool calls in one request, in order.

    Each step is {"tool": "<tool name>", "args": {...}}. Any string argument of the form
    "$N.key.key" (N = 0-based step index) or "$prev.key" is replaced by that step's result,
    e.g. {"tool": "set_fill_channels", "args": {"uid": "$0.uid", ...}} after a
    create_fill_layer step. List items are indexed with numbers ("$2.effects.0.uid").
    Returns per-step results; with stop_on_error the batch halts at the first failure.
    Nested run_batch is not allowed; preview/capture tools return no images here.
    """
    if not steps:
        raise ValueError("steps must contain at least one step")
    results: list[Any] = []
    report: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        name = step.get("tool") if isinstance(step, dict) else None
        entry: dict[str, Any] = {"step": index, "tool": name}
        try:
            if name == "run_batch" or name not in _TOOLS:
                raise ValueError(f"Unknown or non-batchable tool: {name!r}")
            args = _resolve_refs(step.get("args") or {}, results)
            outcome = _TOOLS[name](**args)
            if isinstance(outcome, list):
                outcome = [item for item in outcome if not isinstance(item, Image)]
            entry.update(ok=True, result=outcome)
            results.append(outcome)
        except Exception as exc:
            entry.update(ok=False, error=f"{type(exc).__name__}: {exc}")
            results.append(None)
            report.append(entry)
            if stop_on_error:
                break
            continue
        report.append(entry)
    failed = [entry["step"] for entry in report if not entry["ok"]]
    return {
        "completed": len(report),
        "total": len(steps),
        "failed_steps": failed,
        "steps": report,
    }


@tool()
def get_effect_parameters(uid: int) -> dict[str, Any]:
    """Read a Levels, Compare Mask, or Color Selection effect's parameters by UID."""
    return operations.get_effect_parameters(uid)


@tool()
def set_effect_parameters(
    uid: int,
    values: dict[str, Any] | None = None,
    affected_channel: str | None = None,
) -> dict[str, Any]:
    """Edit a Levels, Compare Mask, or Color Selection effect; only named fields change.

    Levels: input_min, input_max, gamma, output_min, output_max (numbers in a mask or
    mono channel, RGB arrays on colour channels), clamp; affected_channel picks the
    channel for a content-stack Levels. Color Selection (ID-map masking): id_mask
    (resource:// of the baked ID map), colors (list of sRGB arrays), tolerance, hardness,
    output_value, background_color. Compare Mask: operation, left_operand,
    right_operand, constant, tolerance, hardness, channel. Enum fields take member names;
    call get_effect_parameters first to see current values.
    """
    return operations.set_effect_parameters(uid, values, affected_channel)


@tool()
def preview_textures(
    texture_set: str | None = None,
    channels: list[str] | None = None,
    size: int = 512,
) -> list[Any]:
    """See the current result: exports low-res channel images and returns them inline.

    channels: BaseColor (default), Roughness, Metallic, Normal, Height, Emissive,
    Opacity, AO. texture_set defaults to the active one. Nothing is written to export
    folders; previews go to a private cache that is cleared on each call.
    """
    result = operations.preview_textures(texture_set, channels, size)
    images = [Image(path=path) for path in result["files"]]
    return [{k: v for k, v in result.items()}, *images]


@tool()
def capture_ui(max_width: int = 1600) -> list[Any]:
    """Screenshot Painter's UI: layer stack, properties panel, status-bar errors.

    The 3D/2D viewports render black (Vulkan); use preview_textures to see texture results.
    """
    result = operations.capture_ui(max_width)
    data = base64.b64decode(result.pop("png_base64"))
    return [result, Image(data=data, format="png")]


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
