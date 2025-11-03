from kairos.presentation.controller import PresentationController


def test_execute_intent_next_previous():
    pc = PresentationController()  # uses stub client
    assert pc.execute_intent(("next_slide", {})).get("ok") is True
    assert pc.execute_intent(("previous_slide", {})).get("ok") is True


def test_execute_intent_set_slide_param():
    pc = PresentationController()
    res = pc.execute_intent(("set_slide", {"slide_number": 7}))
    assert res.get("ok") is True


def test_execute_intent_unknown():
    pc = PresentationController()
    res = pc.execute_intent(("unknown", {}))
    assert res.get("ok") is False
    assert "Unsupported intent" in res.get("error", "")

