"""Profile-derived balanced technical partitions; editorial records are untouched."""
from ..contracts import GenerationWindow, digest_json, stable_id, require_runtime_capabilities
from ..contracts.worker import OperationContext, WindowPlan
from ..contracts import ResolvedProject, RenderProfile
from ..errors import fail
from ..media.geometry import spatial_transform
from ..media.timing import fraction

PLANNER_VERSION = 'kvd-balanced-windows/1.0.0'


def plan_windows(snapshot: ResolvedProject, profile: RenderProfile, *, context: OperationContext) -> WindowPlan:
    context.cancellation.check()
    p = snapshot.project
    cap = min(profile['policy_inference_max'], int(fraction(profile['policy_duration_max']) * 24))
    offset, step = profile['lattice']['offset'], profile['lattice']['step']
    cap -= (cap - offset) % step
    floor = max(profile['shape_min'], profile['policy_inference_min'])
    source = p['media'][p['source_media_id']]
    from ..contracts import MediaRef
    spatial = spatial_transform(MediaRef.from_dict(source), grid=profile['grid'])
    windows = []
    for scene in p['segments']:
        context.cancellation.check()
        if not scene['selected']:
            continue
        if scene['passthrough']:
            fail('UNSUPPORTED_CAPABILITY', 'M1 media assembly requires successful selected renders.')
        settings = snapshot.settings[scene['id']].to_dict()
        require_runtime_capabilities(settings=settings)
        if settings['render_profile_id'] != profile.id or settings['spatial_policy'] != 'preserve_display_pad':
            fail('UNSUPPORTED_CAPABILITY', 'Select the scene profile and preserve-display spatial policy explicitly.')
        start, end = scene['useful_range']['start'], scene['useful_range']['end']
        length = end - start
        pieces = (length + cap - 1) // cap
        base, remainder = divmod(length, pieces)
        for local in range(pieces):
            useful = base + (local < remainder)
            needed = max(floor, useful)
            n = needed + (offset - needed) % step
            if n > cap:
                fail('FRAME_COUNT_MISMATCH', 'The checked profile cannot fit this window.')
            r = {'start': start, 'end': start + useful}
            spans = [{'role': 'useful', 'inference_range': {'start': 0, 'end': useful},
                'media_id': p['canonical_media_id'], 'source_range': r}]
            if n > useful:
                spans.append({'role': 'padding', 'inference_range': {'start': useful, 'end': n},
                              'repeat_frame': useful - 1})
            plan = {'version': PLANNER_VERSION, 'profile': profile.to_dict(), 'range': r,
                    'spatial': spatial.to_dict(), 'spans': spans, 'scene_revision': scene['revision']}
            key = digest_json({'plan': plan, 'source': p['media'][p['canonical_media_id']]['fingerprint']['digest'],
                              'settings': settings})
            identifier = stable_id('window', p.id, scene['id'], local, r)
            plan_digest = digest_json(plan)
            old = p['windows'].get(identifier)
            revision = (old['plan_revision'] if old and old['plan_digest'] == plan_digest and old['generation_key'] == key
                        else old['plan_revision'] + 1 if old else 1)
            windows.append(GenerationWindow.from_dict({'kind': 'kmin.generation_window', 'schema_version': '2.0.0',
                'id': identifier, 'project_id': p.id, 'segment_id': scene['id'], 'plan_revision': revision, 'ordinal': len(windows),
                'useful_range': r, 'inference_frame_count': n, 'output_useful_range': {'start': 0, 'end': useful},
                'input_spans': spans, 'context': {'mode': 'none', 'before': 0, 'after': 0,
                    'dependency_result_ids': [], 'continuation_state_id': None},
                'padding': {'before': 0, 'after': n - useful, 'method': 'repeat_boundary'},
                'spatial_transform_id': spatial.id, 'control_spec_id': settings['control_spec_id'],
                'render_profile_id': profile.id, 'resolved_settings': settings,
                'resolved_settings_digest': digest_json(settings), 'plan_digest': plan_digest,
                'generation_key': key, 'compiled_prompt': settings['prompt'], 'prompt_recipe_id': None,
                'reference_manifest': []}))
            start += useful
    if not windows:
        fail('PARTIAL_RESULT', 'Select at least one editorial scene.')
    return WindowPlan(tuple(windows), {'version': PLANNER_VERSION, 'gpu': 'not_performed',
        'ranges': [w['useful_range'] for w in windows], 'spatial_transforms': {spatial.id: spatial.to_dict()},
        'useful_frames': sum(w['useful_range']['end'] - w['useful_range']['start'] for w in windows),
        'native_frames': sum(w['inference_frame_count'] for w in windows)})
