"""Recipe JSON types and documented values, without any media/backend I/O."""
from copy import deepcopy

import pytest

from kmin_video_director.errors import ContractError
from kmin_video_director.media.normalize import DEFAULT_RECIPE, validate_recipe


@pytest.mark.parametrize('recipe', [
    None, 7, True, [], 'private-recipe-value',
    {**DEFAULT_RECIPE, 'fps': {'num': 24, 'den': True}},
    {**DEFAULT_RECIPE, 'fps': {'num': 24.0, 'den': 1}},
    {**DEFAULT_RECIPE, 'fps': {'num': 24, 'den': 1.0}},
    {**DEFAULT_RECIPE, 'fps': None},
    {**DEFAULT_RECIPE, 'fps': {'num': 24}},
    {**DEFAULT_RECIPE, 'fps': {'num': 24, 'den': 1, 'extra': 'private-recipe-value'}},
    {**DEFAULT_RECIPE, 'sample_rate': True},
    {**DEFAULT_RECIPE, 'sample_rate': 0},
    {**DEFAULT_RECIPE, 'audio_mode': 'private-recipe-value'},
    {k: v for k, v in DEFAULT_RECIPE.items() if k != 'fps'},
    {**DEFAULT_RECIPE, 'extra': 'private-recipe-value'},
])
def test_malformed_or_unsupported_recipe_is_a_typed_redacted_failure(recipe):
    with pytest.raises(ContractError) as raised:
        validate_recipe(recipe)
    assert raised.value.code in ('INVALID_JSON', 'INVALID_RECORD', 'UNSUPPORTED_CAPABILITY')
    assert 'private-recipe-value' not in str(raised.value)


@pytest.mark.parametrize('mode', ['preserve', 'mute'])
@pytest.mark.parametrize('rate', [8000, 48000, 192000])
def test_documented_recipe_values_remain_accepted_without_mutation(mode, rate):
    recipe = deepcopy(DEFAULT_RECIPE)
    recipe.update(audio_mode=mode, sample_rate=rate)
    original = deepcopy(recipe)
    validate_recipe(recipe)
    assert recipe == original
