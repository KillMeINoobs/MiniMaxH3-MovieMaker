"""Authored text stays byte-exact; no enhancer or generation is executed."""
import pytest
from kmin_video_director.contracts import ContractError, GenerationWindow, Settings, digest_bytes, digest_json
from kmin_video_director.contracts.worker import CancellationFlag, OperationContext
from kmin_video_director.adapters.native_h3.prompt import compile_window_prompt
from tests.contracts.example_data import window


def inputs(tmp_path,text='A cinematic scene.\nРусский текст. <d>[Russian] Привет.</d>  '):
    data = window()
    data['resolved_settings']['prompt'] = text
    data['compiled_prompt'] = text
    data['resolved_settings_digest'] = digest_json(data['resolved_settings'])
    return (GenerationWindow.from_dict(data), Settings.from_dict(data['resolved_settings']),
            OperationContext(tmp_path,CancellationFlag(),{}))


def test_visible_text_digest_and_timing_are_exact(tmp_path):
    win,settings,ctx = inputs(tmp_path)
    out = compile_window_prompt(win,settings,(),context=ctx)
    assert out.text == settings['prompt']
    assert out.digest == digest_bytes(out.text.encode('utf-8'))
    assert out.reference_manifest == ()
    assert out.timing['inference_duration'] == {'num':8,'den':1}
    assert out.timing['output_useful_range'] == {'start':0,'end':180}
    assert out.timing['padding'] == win['padding']
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('text', ['', ' \n ', 'A <Picture 1> walks.', '<Video 2>', '<Audio 1>'])
def test_empty_or_unbound_reference_text_is_rejected(tmp_path,text):
    win,settings,ctx = inputs(tmp_path,text)
    with pytest.raises(ContractError,match='PROMPT_INVALID|REFERENCE_UNBOUND'):
        compile_window_prompt(win,settings,(),context=ctx)


def test_bindings_and_cancel_do_not_silently_fall_back(tmp_path):
    win,settings,ctx = inputs(tmp_path)
    with pytest.raises(ContractError,match='UNSUPPORTED_CAPABILITY'):
        compile_window_prompt(win,settings,({'binding_id':'b'},),context=ctx)
    ctx.cancellation.cancel()
    with pytest.raises(ContractError,match='CANCELLED'):
        compile_window_prompt(win,settings,(),context=ctx)


def test_an_unfrozen_settings_change_is_rejected(tmp_path):
    win,settings,ctx = inputs(tmp_path)
    changed = settings.to_dict()
    changed['seed'] = '4'
    with pytest.raises(ContractError,match='STALE_DEPENDENCY'):
        compile_window_prompt(win,Settings.from_dict(changed),(),context=ctx)


def test_an_authored_window_prompt_is_visible_and_independent_of_scene_text(tmp_path):
    win,settings,ctx = inputs(tmp_path)
    data = win.to_dict()
    data['compiled_prompt'] = 'Local window action.\nVisible author edit.'
    out = compile_window_prompt(GenerationWindow.from_dict(data),settings,(),context=ctx)
    assert out.text == data['compiled_prompt']
    assert out.digest == digest_bytes(data['compiled_prompt'].encode('utf-8'))
