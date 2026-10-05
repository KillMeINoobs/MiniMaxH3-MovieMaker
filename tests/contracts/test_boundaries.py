import importlib
from copy import deepcopy
import pytest
from .example_data import project, window, future_records


def test_stable_identifiers_and_malformed_envelopes():
    c = importlib.import_module("kmin_video_director.contracts")
    assert c.stable_id("window", "proj", "seg", 1, [0, 180]) == c.stable_id("window", "proj", "seg", 1, [0, 180])
    assert c.make_id("project") != c.make_id("project")
    for text in ('{"kind":1}', '{"kind":"kmin.project","schema_version":"2.0.0","required_features":[{}]}'):
        with pytest.raises(c.ContractError):
            c.loads(text)


def test_subframe_clamp_and_absolute_audio_boundaries():
    c = importlib.import_module("kmin_video_director.contracts")
    p = project()
    p["frame_count"] = 1
    p["segments"][0]["useful_range"]["end"] = 1
    p["segments"][0]["source_range"]["end"] = 1
    p["normalization"].update(duration={"num":1,"den":120}, rounded_frame_count=0, frame_count=1,
                              duration_error={"num":1,"den":30}, duration_clamp={"applied":True,
                                "reason":"minimum_one_frame","before_frame_count":0,"after_frame_count":1})
    p["audio_timeline"].update(sample_rate=32000, sample_count=1333)
    c.Project.from_dict(p)
    p["audio_timeline"]["sample_count"] = 1334
    with pytest.raises(c.ContractError, match="AUDIO_SYNC_MISMATCH"):
        c.Project.from_dict(p)


def test_shared_nested_window_and_cut_validation():
    c = importlib.import_module("kmin_video_director.contracts")
    p = project()
    p["windows"] = {"win-1": window()}
    c.Project.from_dict(p)
    p["windows"]["win-1"]["resolved_settings"]["seed"] = "12"
    with pytest.raises(c.ContractError, match="STALE_DEPENDENCY"):
        c.Project.from_dict(p)
    p = project()
    s2 = deepcopy(p["segments"][0])
    s2.update(id="seg-2", boundary_before="cut")
    s2["useful_range"]["start"] = s2["source_range"]["start"] = 180
    p["segments"][0]["useful_range"]["end"] = p["segments"][0]["source_range"]["end"] = 180
    p["segments"].append(s2)
    with pytest.raises(c.ContractError, match="CONTINUATION_INCOMPATIBLE"):
        c.Project.from_dict(p)


def test_accepted_recipe_and_reference_closure():
    c = importlib.import_module("kmin_video_director.contracts")
    p = project()
    recipe = future_records()["prompt_recipe"]
    recipe.update(status="accepted", accepted={"text":recipe["final_text"],"revision":1,"digest":recipe["text_digest"]})
    p["prompt_recipes"] = {recipe["id"]:recipe}
    p["segments"][0]["overrides"].update(prompt_recipe_id=recipe["id"], prompt=recipe["final_text"])
    c.Project.from_dict(p)
    p["segments"][0]["overrides"]["prompt"] = "edited without clearing recipe"
    with pytest.raises(c.ContractError, match="STALE_DEPENDENCY"):
        c.Project.from_dict(p)
