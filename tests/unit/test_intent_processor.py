from kairos.nlp.intent import IntentProcessor


def test_basic_intents():
    ip = IntentProcessor()

    assert ip.recognize_intent("next slide")[0] == "next_slide"
    assert ip.recognize_intent("previous slide")[0] == "previous_slide"
    assert ip.recognize_intent("start presentation")[0] == "start_presentation"
    assert ip.recognize_intent("stop presentation")[0] == "stop_presentation"
    assert ip.recognize_intent("list presentations")[0] == "list_presentations"
    assert ip.recognize_intent("what is the current slide")[0] == "current_slide"


def test_set_slide_parsing():
    ip = IntentProcessor()
    name, params = ip.recognize_intent("go to slide 12")
    assert name == "set_slide"
    assert params["slide_number"] == 12

