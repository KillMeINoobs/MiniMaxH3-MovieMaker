"""Exact authored text and timing metadata, without hidden rewriting."""
from fractions import Fraction
import re

from ...contracts import digest_bytes, require_runtime_capabilities
from ...contracts.worker import CompiledPrompt
from ...errors import fail

VERSION = 'kvd-authored-prompt/1.0.0'


def compile_window_prompt(window, settings, bindings, *, context):
    context.cancellation.check()
    require_runtime_capabilities(settings=settings,window=window)
    if bindings or window['reference_manifest']:
        fail('UNSUPPORTED_CAPABILITY','The first authored path requires empty appearance/reference bindings.')
    if settings.to_dict() != window['resolved_settings']:
        fail('STALE_DEPENDENCY','Compile the exact settings frozen in this window.')
    text = window['compiled_prompt']
    if not text.strip():
        fail('PROMPT_INVALID','Author a visible nonempty window prompt.')
    if re.search(r'<\s*(?:picture|image|video|audio)\s+\d+\s*>',text,re.IGNORECASE):
        fail('REFERENCE_UNBOUND','The no-reference prompt cannot name disconnected media tags.')
    duration = Fraction(window['inference_frame_count'],24)
    timing = {'version':VERSION,'fps':{'num':24,'den':1},
        'inference_duration':{'num':duration.numerator,'den':duration.denominator},
        'useful_range':window['useful_range'],'output_useful_range':window['output_useful_range'],
        'padding':window['padding'],'context':window['context'], 'text_policy':'authored_exact'}
    return CompiledPrompt(text,digest_bytes(text.encode('utf-8')),(),timing)
