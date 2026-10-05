"""Real disk-based CPU media nodes, using unchanged KVD-WORKER/2.0.0."""
from pathlib import Path

from ...contracts import (MediaRef, SpatialTransform, RenderResult, AudioTimeline,
    canonical_bytes, resolve_project)
from ...contracts.serialization import parse_json
from ...contracts.worker import OperationContext, ProjectLocator, StreamSelection
from ...errors import fail
from ...registration import build_registry
from ...media.probe import probe_media
from ...media.normalize import normalize_media, DEFAULT_RECIPE
from ...media.prepare import prepare_window
from ...media.project import create_project, apply_plan, source_profile
from ...planning.windows import plan_windows
from ...assembly.export import assemble_export, DEFAULT_POLICY, selected_windows
from ...assembly.selection import select_results


class NativeCancellation:
    def check(self):
        # Native interruption remains native. Import is only during execution;
        # portable CPU use does not require ComfyUI, torch or models.
        try:
            from comfy.model_management import throw_exception_if_processing_interrupted
        except ModuleNotFoundError as error:
            if error.name not in ('comfy', 'comfy.model_management'):
                raise
            return
        throw_exception_if_processing_interrupted()


def io_fields():
    return {
        'project_root': ('STRING', {'default': '', 'tooltip': 'Existing local project folder, explicitly selected by you.'}),
        'ffmpeg_path': ('STRING', {'default': '', 'tooltip': 'Absolute path to your existing FFmpeg executable.'}),
        'ffprobe_path': ('STRING', {'default': '', 'tooltip': 'Absolute path to your existing ffprobe executable.'}),
        'disk_quota_mb': ('INT', {'default': 4096, 'min': 1, 'max': 1048576, 'tooltip': 'Disk limit for this operation, including temporary artifacts.'}),
        'working_set_mb': ('INT', {'default': 256, 'min': 1, 'max': 65536, 'tooltip': 'Limit for active Python RGB buffers. Backend memory is reported separately.'}),
    }


def context_for(project_root, ffmpeg_path, ffprobe_path, disk_quota_mb=4096, working_set_mb=256, **extra):
    root = Path(project_root)
    if not project_root.strip() or not root.is_absolute() or not root.is_dir():
        fail('INVALID_LOCATOR', 'Select an existing absolute local project folder.')
    versions = {'ffmpeg_path': ffmpeg_path, 'ffprobe_path': ffprobe_path,
        'disk_quota_bytes': str(disk_quota_mb * 1024**2), 'working_set_bytes': str(working_set_mb * 1024**2)}
    versions.update({k: str(v) for k, v in extra.items() if v != ''})
    return OperationContext(root, NativeCancellation(), versions)


def dispatch(name, *args, **kwargs):
    return build_registry().require_operation(name)(*args, **kwargs)


def output(report, *values):
    summary = {'code': 'MEDIA_CPU_READY', 'gpu': 'not_performed', **report}
    text = canonical_bytes(summary).decode('utf-8')
    return {'ui': {'kvd_report': [summary]}, 'result': (*values, text)}


class DiskNode:
    CATEGORY = 'KVD/Media'
    FUNCTION = 'execute'

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float('nan')  # Revalidate content; Comfy's widget cache is not a file fingerprint.


class ProbeMediaNode(DiskNode):
    DESCRIPTION = 'Read actual decoded presentation timestamps and selected streams. Writes a bounded disk index; does not generate video.'
    RETURN_TYPES = ('KVD_PROBE', 'KVD_MEDIA', 'STRING')
    RETURN_NAMES = ('probe', 'source_media', 'media_report')

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {**io_fields(),
            'source_file': ('STRING', {'default': 'source.mp4', 'tooltip': 'Project-relative source path. Unicode and spaces are supported.'}),
            'video_stream': ('INT', {'default': 0, 'min': 0, 'tooltip': 'Absolute video stream index, not the video ordinal.'}),
            'audio_stream': ('INT', {'default': -1, 'min': -1, 'tooltip': '-1 excludes audio. Otherwise select its absolute stream index.'}),
            'endpoint_duration': ('STRING', {'default': '', 'tooltip': 'Leave blank for decoded EOF duration; ambiguous EOF requires an explicit final-frame duration, e.g. 1/24 seconds.'})}}

    def execute(self, source_file, video_stream, audio_stream, endpoint_duration, **io):
        ctx = context_for(**io, endpoint_duration=endpoint_duration)
        found = dispatch('ProbeMedia', ProjectLocator(source_file),
            StreamSelection(video_stream, None if audio_stream == -1 else audio_stream), context=ctx)
        return output(dict(found.timing), found, found.media)


class NormalizeMediaNode(DiskNode):
    DESCRIPTION = 'Normalize the whole source once to true CFR 24/1. Keep actual frame selection, display geometry and global PCM on disk.'
    RETURN_TYPES = ('KVD_NORMALIZED', 'KVD_MEDIA', 'KVD_AUDIO_TIMELINE', 'STRING')
    RETURN_NAMES = ('normalized', 'canonical_media', 'audio_timeline', 'media_report')

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {**io_fields(), 'source_media': ('KVD_MEDIA',),
            'audio_mode': (['preserve', 'mute'], {'default': 'preserve', 'tooltip': 'Preserve selected source audio or create a silent video.'}),
            'sample_rate': ('INT', {'default': 48000, 'min': 8000, 'max': 192000, 'tooltip': 'One global PCM timeline at this sample rate.'})}}

    def execute(self, source_media, audio_mode, sample_rate, **io):
        found = dispatch('NormalizeMedia', source_media,
            {**DEFAULT_RECIPE, 'audio_mode': audio_mode, 'sample_rate': sample_rate}, context=context_for(**io))
        return output(dict(found.normalization['report']), found, found.media, found.audio_timeline)


class MediaProjectNode:
    CATEGORY = 'KVD/Media'
    FUNCTION = 'execute'
    DESCRIPTION = 'Create one editable scene from normalized media. Default native policy is source-reviewed; it does not establish an installed H3 runtime.'
    RETURN_TYPES = ('KVD_PROJECT', 'KVD_RENDER_PROFILE', 'STRING')
    RETURN_NAMES = ('project', 'render_profile', 'media_report')

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'probe': ('KVD_PROBE',), 'normalized': ('KVD_NORMALIZED',),
            'prompt': ('STRING', {'default': '', 'multiline': True, 'tooltip': 'Visible authored scene prompt. Remains editable in the portable Project.'}),
            'seed': ('STRING', {'default': '0', 'tooltip': 'Decimal seed from 0 to 18446744073709551615.'})},
            'optional': {'render_profile': ('KVD_RENDER_PROFILE',)}}

    def execute(self, probe, normalized, prompt, seed, render_profile=None):
        profile = render_profile or source_profile()
        project = create_project(probe.media, normalized, profile, prompt=prompt, seed=seed)
        return output({'frame_count': project['frame_count'], 'profile_evidence': profile['evidence']}, project, profile)


class PlanWindowsNode:
    CATEGORY = 'KVD/Media'
    FUNCTION = 'execute'
    DESCRIPTION = 'Partition selected scenes into balanced legal native windows. Scene identities and ranges stay intact; padding is explicit.'
    RETURN_TYPES = ('KVD_PROJECT', 'KVD_WINDOW_PLAN', 'STRING')
    RETURN_NAMES = ('project', 'window_plan', 'media_report')

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'project': ('KVD_PROJECT',), 'render_profile': ('KVD_RENDER_PROFILE',)}}

    def execute(self, project, render_profile):
        ctx = OperationContext(Path(), NativeCancellation(), {})
        plan = dispatch('PlanWindows', resolve_project(project), render_profile, context=ctx)
        return output(dict(plan.coverage), apply_plan(project, plan), plan)


class SelectWindowNode:
    CATEGORY = 'KVD/Media'
    FUNCTION = 'execute'
    DESCRIPTION = 'Select one already planned window by timeline order. Returns disk media and the exact spatial transform; no decode or tensor allocation.'
    RETURN_TYPES = ('KVD_WINDOW', 'KVD_MEDIA', 'KVD_SPATIAL', 'STRING')
    RETURN_NAMES = ('window', 'canonical_media', 'spatial', 'media_report')

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'project': ('KVD_PROJECT',), 'window_index': ('INT', {'default': 0, 'min': 0})}}

    def execute(self, project, window_index):
        from ...contracts import GenerationWindow
        windows = sorted(project['windows'].values(), key=lambda w: w['useful_range']['start'])
        if not 0 <= window_index < len(windows):
            fail('PARTIAL_RESULT', 'Select an index within the current window plan.')
        window = GenerationWindow.from_dict(windows[window_index])
        media = MediaRef.from_dict(project['media'][project['canonical_media_id']])
        spatial = SpatialTransform.from_dict(project['spatial_transforms'][window['spatial_transform_id']])
        return output({'window_id': window.id, 'useful_range': window['useful_range'],
            'native_frames': window['inference_frame_count']}, window, media, spatial)


class PrepareWindowNode(DiskNode):
    DESCRIPTION = 'Prepare one bounded native disk artifact from canonical CFR frames, including spatial pad and last-frame repeat. No whole-film IMAGE tensor.'
    RETURN_TYPES = ('KVD_PREPARED', 'KVD_MEDIA', 'STRING')
    RETURN_NAMES = ('prepared', 'prepared_media', 'media_report')

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {**io_fields(), 'window': ('KVD_WINDOW',),
            'canonical_media': ('KVD_MEDIA',), 'spatial': ('KVD_SPATIAL',)}}

    def execute(self, window, canonical_media, spatial, **io):
        prepared = dispatch('PrepareWindow', window, canonical_media, spatial, context=context_for(**io))
        return output({'window_id': prepared.window_id, 'native_frames': prepared.frame_count,
            'canvas_dimensions': [spatial['canvas_width'], spatial['canvas_height']]}, prepared, prepared.media)


class SelectResultsNode:
    CATEGORY = 'KVD/Assembly'
    FUNCTION = 'execute'
    DESCRIPTION = 'Explicitly select validated successful current RenderResult records. Empty or missing selections remain incomplete; no source substitution.'
    RETURN_TYPES = ('KVD_PROJECT', 'STRING')
    RETURN_NAMES = ('project', 'media_report')

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'project': ('KVD_PROJECT',), 'results_json': ('STRING', {'default': '[]', 'multiline': True,
            'tooltip': 'JSON array of successful RenderResult records for the current windows. Explicit selection replaces the active result map.'})}}

    def execute(self, project, results_json):
        records = parse_json(results_json)
        if not isinstance(records, list):
            fail('INVALID_RECORD', 'Results JSON must be an array of RenderResult records.')
        results = tuple(RenderResult.from_dict(r) for r in records)
        selected = select_results(project, results)
        return output({'selected_result_ids': [r.id for r in results]}, selected)


class AssembleExportNode(DiskNode):
    CATEGORY = 'KVD/Assembly'
    DESCRIPTION = 'Verify explicitly selected successful useful outputs, assemble once, and check actual decoded export timing, samples and dimensions.'
    RETURN_TYPES = ('KVD_RENDER_RESULT', 'KVD_MEDIA', 'STRING')
    RETURN_NAMES = ('export_result', 'export_media', 'media_report')
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {**io_fields(), 'project': ('KVD_PROJECT',),
            'selection': (['full', 'selected'], {'default': 'full', 'tooltip': 'Full requires all scenes. Selected concatenates only selected scene ranges.'}),
            'codec': (['ffv1-nut', 'h264-aac'], {'default': 'ffv1-nut', 'tooltip': 'Lossless FFV1/PCM or one final H.264/AAC encode.'}),
            'odd_dimensions': (['reject', 'pad_even'], {'default': 'reject', 'tooltip': 'H.264 requires even dimensions. Explicit padding adds at most one right/bottom pixel.'})},
            'optional': {'audio_timeline': ('KVD_AUDIO_TIMELINE',)}}

    def execute(self, project, selection, codec, odd_dimensions, audio_timeline=None, **io):
        windows = selected_windows(project, selection)
        ids = [project['active_result_by_window'].get(w['id']) for w in windows]
        results = tuple(RenderResult.from_dict(project['results'][i]) for i in ids if i is not None)
        found = dispatch('AssembleExport', project, results,
            audio_timeline or AudioTimeline.from_dict(project['audio_timeline']),
            {**DEFAULT_POLICY, 'selection': selection, 'codec': codec, 'odd_dimensions': odd_dimensions}, context=context_for(**io))
        return output(dict(found.report), found.result, MediaRef.from_dict(found.result['artifacts'][0]))


NODE_CLASS_MAPPINGS = {'KVD_ProbeMedia': ProbeMediaNode, 'KVD_NormalizeMedia': NormalizeMediaNode,
    'KVD_MediaProject': MediaProjectNode, 'KVD_PlanWindows': PlanWindowsNode, 'KVD_SelectWindow': SelectWindowNode,
    'KVD_PrepareWindow': PrepareWindowNode, 'KVD_SelectResults': SelectResultsNode, 'KVD_AssembleExport': AssembleExportNode}
NODE_DISPLAY_NAME_MAPPINGS = {'KVD_ProbeMedia': 'KVD Probe Media', 'KVD_NormalizeMedia': 'KVD Normalize · CFR24',
    'KVD_MediaProject': 'KVD Media Project', 'KVD_PlanWindows': 'KVD Plan Windows', 'KVD_SelectWindow': 'KVD Select Window',
    'KVD_PrepareWindow': 'KVD Prepare Window', 'KVD_SelectResults': 'KVD Select Results', 'KVD_AssembleExport': 'KVD Assemble & Export'}
OPERATIONS = {'ProbeMedia': probe_media, 'NormalizeMedia': normalize_media, 'PlanWindows': plan_windows,
    'PrepareWindow': prepare_window, 'AssembleExport': assemble_export}
