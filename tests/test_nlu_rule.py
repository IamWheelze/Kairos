import pytest
from backend.kairos_core.nlu.rule_based import RuleBasedNLU


@pytest.mark.asyncio
async def test_rule_nlu_basic():
    nlu = RuleBasedNLU()
    r = await nlu.detect_intent('next slide')
    assert r.intent == 'NextSlide'
    r2 = await nlu.detect_intent('previous please')
    assert r2.intent == 'PreviousSlide'
    r3 = await nlu.detect_intent('clear screen')
    assert r3.intent == 'ClearScreen'
    r4 = await nlu.detect_intent('show amazing grace')
    assert r4.intent == 'GoToSong'
    assert 'song_title' in r4.params

