"""Reviewed media + actual adapter operations; constructed AV only, never H3.

GraphBuilder is the hash-checked stdlib source fixture. Model availability is
explicitly synthetic. No native executor/loader/sampler/Canny call is made.
"""
from array import array
from dataclasses import replace
from fractions import Fraction
import json
import wave

import pytest

from kmin_video_director.contracts import (AudioTimeline, ControlSpec, GenerationWindow,
    MediaRef, Project, Settings, SpatialTransform, dumps, resolve_project)
from kmin_video_director.contracts.worker import DecodedAV, NativeLink, OperationContext, ProjectLocator, StreamSelection
from kmin_video_director.registration import build_registry
from kmin_video_director.errors import ContractError
from kmin_video_director.media.backend import check_media
from kmin_video_director.media.normalize import DEFAULT_RECIPE
from kmin_video_director.media.project import apply_plan, create_project
from kmin_video_director.media.probe import probe_media, verify_cfr
from kmin_video_director.media.timing import sample_boundary
from kmin_video_director.assembly.export import DEFAULT_POLICY
from kmin_video_director.assembly.selection import select_results
from kmin_video_director.adapters.native_h3.graph import generation_key
from kmin_video_director.adapters.native_h3.order import DecodeReceipt, check_predecessor
from tests.adapters.test_native_graph import native_builder, setup as graph_setup
from tests.adapters.test_finalization import setup as decoded_setup, backend
from tests.media.support import context, video, with_audio, raw_video, command, numbered_frame


def synthetic_audio(n, *, impulses=(), sample_rate=32000):
    # Exact pinned H3 40Hz latent grid and 800-sample stereo audio VAE hop.
    count = round(Fraction(n * 40, 24)) * 800
    pcm = array('h', [0]) * (count * 2)
    for index in impulses:
        pcm[index * 2] = pcm[index * 2 + 1] = 12000
    return {'sample_rate': sample_rate, 'channels': 2, 'pcm_s16le': pcm.tobytes()}


def prepared_project(root, *, frames, rate=32000, mode='preserve', sound=False):
    registry = build_registry()
    _, profile, models, _, _, graph_context, _, parent = graph_setup(root, off=True)
    ctx = context(root)
    source = video(root, count=frames, width=8, height=6, name='constructed source.nut')
    if sound:
        source = with_audio(root, source, samples=sample_boundary(frames, 48000), rate=48000,
                            impulses=(0, 4000, 12000), offset='0.08333333333333333')
    found = registry.require_operation('ProbeMedia')(ProjectLocator(source.name),
        StreamSelection(audio=1 if sound else None), context=ctx)
    normalized = registry.require_operation('NormalizeMedia')(found.media,
        {**DEFAULT_RECIPE, 'sample_rate': rate}, context=ctx)
    project = create_project(found.media, normalized, profile,
        prompt='Visible author text.\nВидимый авторский текст.', seed='18446744073709551615')
    data = project.to_dict()
    data['defaults']['audio_mode'] = mode
    data['audio_timeline']['mode'] = mode
    project = Project.from_dict(data)
    plan = registry.require_operation('PlanWindows')(resolve_project(project), profile, context=ctx)
    project = apply_plan(project, plan)
    ctx = OperationContext(root, ctx.cancellation,
        {**ctx.versions, **graph_context.versions, 'evidence': 'synthetic_decoded'})
    return project, profile, models, ctx, parent


def finalize_constructed(project, profile, models, ctx, parent, *, generated=False):
    registry = build_registry()
    results = []
    previous = None
    graphs = []
    for record in sorted(project['windows'].values(), key=lambda w: w['ordinal']):
        window = GenerationWindow.from_dict(record)
        spatial = SpatialTransform.from_dict(project['spatial_transforms'][window['spatial_transform_id']])
        canonical = MediaRef.from_dict(project['media'][project['canonical_media_id']])
        prepared = registry.require_operation('PrepareWindow')(window, canonical, spatial, context=ctx)
        spec = ControlSpec.from_dict(project['controls'][window['control_spec_id']])
        control = registry.require_operation('BuildControl')(prepared, spec, context=ctx)
        assert control.media is None  # Real explicit-off handler, no fake native contour.
        prompt = registry.require_operation('CompileWindowPrompt')(window,
            Settings.from_dict(window['resolved_settings']), (), context=ctx)
        data = window.to_dict()
        data['generation_key'] = generation_key(window, profile, control, prompt, spec)
        window = GenerationWindow.from_dict(data)
        pd = project.to_dict()
        pd['windows'][window.id] = window.to_dict()
        project = Project.from_dict(pd)
        check_predecessor(previous, project_id=project.id, plan_revision=window['plan_revision'],
            ordinal=window['ordinal'], useful_start=window['useful_range']['start'])
        predecessor = None
        graph_parent = dict(parent)
        if previous is not None:
            predecessor = NativeLink('previous-finalizer', 1)
            graph_parent['previous-finalizer'] = {'class_type': 'KVD_FinalizeWindow', 'inputs': {}}
        local = replace(ctx, versions={**ctx.versions, 'source_graph': json.dumps(graph_parent),
            'control_spec_json': dumps(spec), 'canvas_width': str(spatial['canvas_width']),
            'canvas_height': str(spatial['canvas_height'])})
        expanded = registry.require_operation('ExpandNativeRender')(window, profile, models,
            control, prompt, predecessor, context=local)
        graphs.append(expanded.graph)
        manifest = json.loads(expanded.graph[expanded.order_token.node_id]['inputs']['manifest'])
        token = DecodeReceipt(manifest, 'synthetic_decoded')
        n = window['inference_frame_count']
        useful = window['useful_range']
        count = useful['end'] - useful['start']
        # Independent synthetic render numbers differ from the actual source.
        frames = tuple(numbered_frame(1000 + useful['start'] + i,
            spatial['canvas_width'], spatial['canvas_height']) for i in range(n))
        audio = synthetic_audio(n, impulses=(0, 3200)) if generated else None
        decoded = DecodedAV(frames, audio, n, spatial['canvas_width'], spatial['canvas_height'])
        finalized = registry.require_operation('FinalizeWindow')(decoded, window, resolve_project(project),
            spatial, 1, 'constructed-' + window.id, token, context=local)
        result = finalized.result
        assert result['validation']['gpu'] == 'not_performed'
        assert result['validation']['evidence_kind'] == 'cpu_media'
        assert result['coverage']['useful_frames'] == count
        video_ref = MediaRef.from_dict(next(a for a in result['artifacts'] if a['role'] == 'render_video'))
        actual = probe_media(ProjectLocator(video_ref['locator']['path']), StreamSelection(), context=ctx).media
        assert actual['probe'] == video_ref['probe']
        assert verify_cfr(actual, count, ctx)['pts_digest'] == result['coverage']['pts_digest']
        results.append(result)
        previous = finalized.order_token
        project = select_results(project, tuple(results))
        del decoded, frames, audio
    return project, tuple(results), graphs


def test_actual_media_adapter_export_retains_source_global_pcm_and_exact_probe(tmp_path, native_builder):
    project, profile, models, ctx, parent = prepared_project(tmp_path, frames=24, sound=True)
    original = project['audio_timeline']
    project, results, graphs = finalize_constructed(project, profile, models, ctx, parent)
    out = build_registry().require_operation('AssembleExport')(project, results,
        AudioTimeline.from_dict(original), DEFAULT_POLICY, context=ctx)
    assert project['audio_timeline'] == original
    assert results[0]['audio']['source_offset'] == {'num': 1, 'den': 12}
    assert results[0]['audio']['expected_samples'] == sample_boundary(24, 32000)
    pcm = MediaRef.from_dict(project['normalization']['report']['pcm_media'])
    with wave.open(str(check_media(pcm, ctx)), 'rb') as src:
        expected = src.readframes(src.getnframes())
    exported = check_media(MediaRef.from_dict(out.result['artifacts'][0]), ctx)
    actual = command([ctx.versions['ffmpeg_path'], '-v', 'error', '-i', str(exported),
        '-map', '0:a:0', '-f', 's16le', 'pipe:1'])
    assert actual == expected
    assert out.report['audio']['final_encode_count'] == 1
    assert raw_video(exported) != raw_video(tmp_path / 'constructed source.nut')
    assert all('audio_guide' not in n['inputs'] for g in graphs for n in g.values())


def test_generated_native_32k_two_windows_fit_global_q_without_origin_reset(tmp_path, native_builder):
    project, profile, models, ctx, parent = prepared_project(tmp_path, frames=346, mode='generate')
    project, results, graphs = finalize_constructed(project, profile, models, ctx, parent, generated=True)
    assert [r['audio']['expected_samples'] for r in results] == [230667, 230666]
    assert [r['audio']['sample_phase_fit'] for r in results] == [0, -1]
    assert all(r['audio']['native_sample_rate'] == 32000 for r in results)
    for result in results:
        audio = MediaRef.from_dict(next(a for a in result['artifacts'] if a['role'] == 'audio_pcm'))
        with wave.open(str(check_media(audio, ctx)), 'rb') as src:
            assert src.getnframes() == result['audio']['expected_samples']
    out = build_registry().require_operation('AssembleExport')(project, results,
        AudioTimeline.from_dict(project['audio_timeline']), DEFAULT_POLICY, context=ctx)
    exported = check_media(MediaRef.from_dict(out.result['artifacts'][0]), ctx)
    pcm = array('h')
    pcm.frombytes(command([ctx.versions['ffmpeg_path'], '-v', 'error', '-i', str(exported),
        '-map', '0:a:0', '-f', 's16le', 'pipe:1']))
    assert len(pcm) == sample_boundary(346, 32000)
    assert pcm[0] and pcm[sample_boundary(173, 32000)]
    assert out.report['audio']['sample_phase_corrections'] == []
    assert out.report['audio']['final_encode_count'] == 1
    gate = next(n for n in graphs[1].values() if n['class_type'] == 'KVD_WindowGate')
    assert gate['inputs']['order_token'] == ['previous-finalizer', 1]


def test_native_32k_generated_pcm_resamples_to_project_48k_once(tmp_path, native_builder):
    project, profile, models, ctx, parent = prepared_project(tmp_path, frames=6, rate=48000, mode='generate')
    project, results, _ = finalize_constructed(project, profile, models, ctx, parent, generated=True)
    audio = next(a for a in results[0]['artifacts'] if a['role'] == 'audio_pcm')
    with wave.open(str(tmp_path / audio['locator']['path']), 'rb') as src:
        assert (src.getframerate(), src.getnchannels(), src.getnframes()) == (48000, 1, 12000)
        samples = array('h'); samples.frombytes(src.readframes(src.getnframes()))
    assert abs(max(range(4600, 5000), key=lambda i: abs(samples[i])) - 4800) <= 1
    assert results[0]['audio']['native_sample_count'] == 165600
    assert results[0]['audio']['native_quantization_correction'] == 267


def test_native_audio_grid_shortfall_is_padded_once_and_reported(tmp_path, native_builder):
    project, profile, models, ctx, parent = prepared_project(tmp_path, frames=158, mode='generate')
    project, results, _ = finalize_constructed(project, profile, models, ctx, parent, generated=True)
    report = results[0]['audio']
    assert report['native_sample_count'] == 210400
    assert report['expected_samples'] == report['measured_samples'] == 210667
    assert report['native_quantization_correction'] == -267
    assert report['native_useful_pad_samples'] == 267
    assert report['sample_phase_fit'] == 0


def test_generated_pcm_content_changes_durable_result_identity_and_preserves_prior_bytes(tmp_path, backend):
    from kmin_video_director.adapters.native_h3.finalize import finalize_window
    decoded, window, snapshot, spatial, token, ctx = decoded_setup(tmp_path, backend, audio_mode='generate')
    first = finalize_window(replace(decoded, audio=synthetic_audio(decoded.frame_count)),
        window, snapshot, spatial, 1, 'same-audio-attempt', token, context=ctx).result
    first_media = MediaRef.from_dict(next(a for a in first['artifacts'] if a['role'] == 'audio_pcm'))
    first_bytes = check_media(first_media, ctx).read_bytes()
    second = finalize_window(replace(decoded, audio=synthetic_audio(decoded.frame_count, impulses=(3200,))),
        window, snapshot, spatial, 1, 'same-audio-attempt', token, context=ctx).result
    second_media = next(a for a in second['artifacts'] if a['role'] == 'audio_pcm')
    assert first['generation_key'] == second['generation_key'] == window['generation_key']
    assert first.id != second.id and first_media['locator'] != second_media['locator']
    assert first_media['fingerprint']['digest'] != second_media['fingerprint']['digest']
    assert check_media(first_media, ctx).read_bytes() == first_bytes


def test_finalize_sound_mode_must_match_the_explicit_global_decision(tmp_path, backend):
    decoded, window, snapshot, spatial, token, ctx = decoded_setup(tmp_path, backend, audio_mode='generate')
    data = snapshot.project.to_dict()
    data['audio_timeline']['mode'] = 'preserve'
    with pytest.raises(ContractError, match='AUDIO_SYNC_MISMATCH'):
        build_registry().require_operation('FinalizeWindow')(replace(decoded, audio=synthetic_audio(decoded.frame_count)),
            window, resolve_project(Project.from_dict(data)), spatial, 1, 'mode-mismatch', token, context=ctx)
    assert not list(tmp_path.rglob('*.nut'))


def test_finalized_collection_uses_reviewed_selection_and_includes_artifacts(tmp_path, backend):
    from kmin_video_director.adapters.native_h3 import finalize
    decoded, window, snapshot, spatial, token, ctx = decoded_setup(tmp_path, backend)
    result = finalize.finalize_window(decoded, window, snapshot, spatial, 1, 'collect', token, context=ctx).result
    collected, text = finalize.collect_result(snapshot.project, result)
    records = json.loads(text)
    assert records == [result.to_dict()]
    assert collected['active_result_by_window'][window.id] == result.id
    assert collected['results'][result.id] == result.to_dict()
    assert all(collected['media'][a['id']] == a for a in result['artifacts'])
    assert select_results(collected, tuple(type(result).from_dict(r) for r in records)) == collected


def test_new_attempt_collection_keeps_identical_content_artifacts_distinct(tmp_path, backend):
    from kmin_video_director.adapters.native_h3 import finalize
    decoded, window, snapshot, spatial, token, ctx = decoded_setup(tmp_path, backend)
    first = finalize.finalize_window(decoded, window, snapshot, spatial, 1, 'retry', token, context=ctx).result
    collected, _ = finalize.collect_result(snapshot.project, first)
    second = finalize.finalize_window(decoded, window, resolve_project(collected), spatial,
        2, 'retry', token, context=ctx).result
    updated, text = finalize.collect_result(collected, second)
    assert first['generation_key'] == second['generation_key']
    assert first['artifacts'][0]['fingerprint']['digest'] == second['artifacts'][0]['fingerprint']['digest']
    assert first['artifacts'][0]['id'] != second['artifacts'][0]['id']
    assert updated['results'][first.id] == first.to_dict()
    assert updated['active_result_by_window'][window.id] == second.id
    assert json.loads(text) == [second.to_dict()]


@pytest.mark.parametrize('fault', ['missing', 'rate', 'boolean_rate', 'channels', 'short', 'long', 'odd_bytes'])
def test_generated_audio_incompatible_inputs_fail_before_publishing(tmp_path, backend, fault):
    decoded, window, snapshot, spatial, token, ctx = decoded_setup(tmp_path, backend, audio_mode='generate')
    audio = synthetic_audio(decoded.frame_count)
    if fault == 'missing': audio = None
    elif fault == 'rate': audio['sample_rate'] = 48000
    elif fault == 'boolean_rate': audio['sample_rate'] = True
    elif fault == 'channels': audio['channels'] = 1
    elif fault == 'short': audio['pcm_s16le'] = audio['pcm_s16le'][:-4]
    elif fault == 'long': audio['pcm_s16le'] += b'\0' * 4
    elif fault == 'odd_bytes': audio['pcm_s16le'] += b'\0'
    decoded = replace(decoded, audio=audio)
    with pytest.raises(ContractError, match='AUDIO_SYNC_MISMATCH'):
        build_registry().require_operation('FinalizeWindow')(decoded, window, snapshot, spatial,
            1, 'bad-audio', token, context=ctx)
    assert not list(tmp_path.rglob('*.partial')) and not list(tmp_path.rglob('*.nut'))


def test_incomplete_first_window_collection_cannot_export_remaining_source(tmp_path, native_builder):
    project, profile, models, ctx, parent = prepared_project(tmp_path, frames=346)
    # Keep the full plan, explicitly select just a separately constructed first result.
    record = min(project['windows'].values(), key=lambda w: w['ordinal'])
    partial = project.to_dict()
    partial['windows'] = {record['id']: record}
    partial, results, _ = finalize_constructed(Project.from_dict(partial), profile, models, ctx, parent)
    full_data = project.to_dict()
    full_data['windows'][record['id']] = partial['windows'][record['id']]
    full = select_results(Project.from_dict(full_data), results)
    with pytest.raises(ContractError, match='PARTIAL_RESULT'):
        build_registry().require_operation('AssembleExport')(full, results,
            AudioTimeline.from_dict(full['audio_timeline']), DEFAULT_POLICY, context=ctx)
