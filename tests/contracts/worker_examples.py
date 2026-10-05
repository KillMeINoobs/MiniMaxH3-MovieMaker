"""Synthetic call-shape examples for all nine downstream protocols.

No handler is invoked, file is probed, graph is expanded or tensor is created.
Planned results and unmaterialized native values cannot establish execution.
"""
from pathlib import Path

from kmin_video_director.contracts import (
    AudioTimeline, ControlSpec, GenerationWindow, MediaRef, Project, RenderProfile,
    RenderResult, SpatialTransform, digest_bytes, resolve_project,
)
from kmin_video_director.contracts import worker as w
from .example_data import media, project, result, spatial, window


def operation_inputs(asset_root: Path):
    p = Project.from_dict(project())
    snapshot = resolve_project(p)
    planned_window = GenerationWindow.from_dict(window())
    transform = SpatialTransform.from_dict(spatial())
    profile = RenderProfile.from_dict(p["render_profiles"]["profile-source-only"])
    canonical = MediaRef.from_dict(p["media"]["media-cfr"])
    control = ControlSpec.from_dict(p["controls"]["ctrl-canny"])
    context = w.OperationContext(asset_root, w.CancellationFlag(), {"fixture": "synthetic/1"})
    prepared_media = media("prepared-window-synthetic", "prepared_video")
    prepared_media["probe"]["video"].update(end_pts=192, height=384)
    prepared = w.PreparedArtifact(planned_window.id, MediaRef.from_dict(prepared_media), transform, 192)
    map_media = media("map-synthetic", "control_map")
    map_media["probe"]["video"].update(end_pts=192, height=384)
    control_artifact = w.ControlArtifact(planned_window.id, control.id,
        MediaRef.from_dict(map_media), transform.id, 192)
    text = planned_window["compiled_prompt"]
    prompt = w.CompiledPrompt(text, digest_bytes(text.encode("utf-8")), (),
        {"useful_range": planned_window["useful_range"], "evidence": "synthetic_metadata"})
    models = w.NativeModelLinks(*(w.NativeLink("synthetic-" + n, 0)
                                 for n in ("model", "clip", "video-vae", "audio-vae")))
    # Opaque objects show a runtime-only boundary. They contain no pixels/audio.
    decoded = w.DecodedAV(object(), None, 192, 640, 384)
    common = {"context": context}
    return {
        "ProbeMedia": {**common, "locator": w.ProjectLocator("media/Сцена 1/clip.bin"),
            "selection": w.StreamSelection(video=0, audio=None)},
        "NormalizeMedia": {**common, "media": MediaRef.from_dict(p["media"]["media-source"]),
            "recipe": {"version": "synthetic-recipe/1", "fps": {"num": 24, "den": 1}}},
        "PlanWindows": {**common, "snapshot": snapshot, "profile": profile},
        "PrepareWindow": {**common, "window": planned_window, "canonical_media": canonical,
            "spatial": transform},
        "BuildControl": {**common, "prepared": prepared, "control": control},
        "CompileWindowPrompt": {**common, "window": planned_window,
            "settings": snapshot.settings["seg-1"], "bindings": ()},
        "ExpandNativeRender": {**common, "window": planned_window, "profile": profile,
            "models": models, "control": control_artifact, "prompt": prompt, "order_token": None},
        "FinalizeWindow": {**common, "decoded": decoded, "window": planned_window,
            "snapshot": snapshot, "spatial": transform, "attempt": 1,
            "request_id": "synthetic-request-1", "order_token": object()},
        "AssembleExport": {**common, "project": p, "results": (RenderResult.from_dict(result()),),
            "audio": AudioTimeline.from_dict(p["audio_timeline"]),
            "export_policy": {"version": "synthetic-policy/1", "evidence": "synthetic_metadata"}},
    }
