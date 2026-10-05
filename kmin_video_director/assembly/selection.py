"""Explicit portable selection of current successful window results; no I/O."""
from ..contracts import Project, RenderResult
from ..errors import fail


def select_results(project, results):
    data = project.to_dict()
    active = {}
    for result in results:
        if not isinstance(result, RenderResult):
            fail('INVALID_RECORD', 'Select validated RenderResult records.')
        window = data['windows'].get(result['window_id'])
        if window is None or result['generation_key'] != window['generation_key']:
            fail('STALE_DEPENDENCY', 'Select results for the current project window plan.')
        if result['status'] != 'succeeded':
            fail('PARTIAL_RESULT', 'Explicit selection accepts only successful render results.')
        if result['window_id'] in active:
            fail('DUPLICATE_ID', 'Select one result for each window.')
        existing = data['results'].get(result.id)
        if existing is not None and existing != result.to_dict():
            fail('STALE_DEPENDENCY', 'A result ID already identifies different content.')
        data['results'][result.id] = result.to_dict()
        active[result['window_id']] = result.id
        for media in result['artifacts']:
            existing = data['media'].get(media['id'])
            if existing is not None and existing != media:
                fail('STALE_DEPENDENCY', 'An artifact ID already identifies different content.')
            data['media'][media['id']] = media
    data['active_result_by_window'] = active
    if data != project.to_dict():
        data['revision'] += 1
    return Project.from_dict(data)
