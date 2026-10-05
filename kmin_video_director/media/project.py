"""Construct a real portable media project and install an explicitly requested plan."""
from ..contracts import Project, Settings, RenderProfile, ControlSpec, stable_id, digest_json
from ..errors import fail
from .backend import media_binding


def source_profile():
    # Checked source policy, deliberately no installed model or GPU claim.
    return RenderProfile.from_dict({'id': 'native-h3-source-policy', 'version': 'kvd-native-source/1.0.0',
        'evidence': 'source_only', 'receipts': [], 'fps': {'num': 24, 'den': 1},
        'lattice': {'offset': 5, 'step': 17}, 'shape_min': 5, 'policy_inference_min': 124,
        'policy_inference_max': 345, 'policy_duration_max': {'num': 15, 'den': 1}, 'grid': 32,
        'base_family': 'ref2va', 'components': {}, 'node_signatures': {},
        'core_revision': 'b87fe48b0491425f682f7ffdaed56d0387cb6c5d',
        'runtime': {}, 'sampling': {}, 'control_branch': {}, 'memory_policy': 'one_window'})


def create_project(source, normalized, profile, *, prompt='', seed='0'):
    binding = media_binding(source)
    if (source['fingerprint']['digest'] != normalized.normalization['report'].get('source_digest')
        or binding != normalized.normalization['report'].get('source_binding')):
        fail('STALE_DEPENDENCY', 'Normalized media must originate from the same selected source streams and probe.')
    identifier = stable_id('project', binding, normalized.normalization['report']['recipe'])
    scene_id = stable_id('scene', identifier)
    settings = Settings.from_dict({'prompt': prompt, 'prompt_recipe_id': None, 'seed': seed,
        'control_spec_id': 'control-off', 'audio_mode': normalized.audio_timeline['mode'],
        'reference_binding_ids': [], 'continuity_policy': 'none', 'spatial_policy': 'preserve_display_pad',
        'render_profile_id': profile.id})
    control = ControlSpec.from_dict({'kind': 'kmin.control_spec', 'schema_version': '2.0.0', 'id': 'control-off',
        'type': 'off', 'enabled': False, 'backend': {'id': 'explicit-off', 'version': '1.0.0', 'parameters': {},
            'model_digest': None, 'temporal_policy': 'none'}, 'strength': 0,
        'schedule': {'start_percent': 0, 'end_percent': 1}, 'conditioning_role': 'structural_control_video',
        'compatibility': {'profile_ids': [profile.id], 'evidence': 'source_only'}, 'preprocess_version': 'off/1'})
    f = normalized.normalization['frame_count']
    r = {'start': 0, 'end': f}
    media = {source.id: source.to_dict(), normalized.media.id: normalized.media.to_dict()}
    pcm = normalized.normalization['report'].get('pcm_media')
    if pcm:
        media[pcm['id']] = pcm
    return Project.from_dict({'kind': 'kmin.project', 'schema_version': '2.0.0', 'id': identifier,
        'revision': 1, 'fps': {'num': 24, 'den': 1}, 'frame_count': f,
        'source_media_id': source.id, 'canonical_media_id': normalized.media.id,
        'normalization': dict(normalized.normalization), 'media': media, 'defaults': settings.to_dict(),
        'controls': {control.id: control.to_dict()}, 'render_profiles': {profile.id: profile.to_dict()},
        'segments': [{'kind': 'kmin.segment', 'schema_version': '2.0.0', 'id': scene_id, 'revision': 1,
            'project_id': identifier, 'useful_range': r, 'source_range': r, 'source_media_id': normalized.media.id,
            'boundary_before': 'first', 'continuity_group_id': stable_id('shot', identifier), 'overrides': {},
            'analysis_ids': [], 'prompt_draft_ids': [], 'selected': True, 'passthrough': False}],
        'audio_timeline': normalized.audio_timeline.to_dict(), 'results': {}, 'active_result_by_window': {},
        'mode_drafts': {}, 'detection_proposals': {}, 'scene_analyses': {}, 'prompt_recipes': {}, 'subjects': {},
        'reference_bindings': {}, 'continuation_states': {}, 'windows': {}, 'spatial_transforms': {},
        'extensions': {'kvd.media': {'version': '1.0.0', 'profile_evidence': 'source_only', 'gpu': 'not_performed'}}})


def apply_plan(project, plan):
    data = project.to_dict()
    if any(w['project_id'] != project.id for w in plan.windows):
        fail('DANGLING_REFERENCE', 'The plan belongs to a different project.')
    data['windows'] = {w.id: w.to_dict() for w in plan.windows}
    data['spatial_transforms'] = dict(plan.coverage['spatial_transforms'])
    data['active_result_by_window'] = {w: r for w, r in data['active_result_by_window'].items()
        if w in data['windows'] and data['results'][r]['generation_key'] == data['windows'][w]['generation_key']}
    if data != project.to_dict():
        data['revision'] += 1
    return Project.from_dict(data)
