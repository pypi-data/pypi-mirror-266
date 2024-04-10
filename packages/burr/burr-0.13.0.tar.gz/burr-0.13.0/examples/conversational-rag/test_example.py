import pytest
from burr.core import state
from burr.testing import pytest_generate_tests  # noqa: F401
# TODO: import action you're testing, i.e. import ai_converse.
from application import ai_converse, bootstrap_vector_db, conversational_rag_driver


@pytest.fixture()
def vector_store():
    input_text = [
        "harrison worked at kensho",
        "stefan worked at Stitch Fix",
        "stefan likes tacos",
        "elijah worked at TwoSigma",
        "elijah likes mango",
        "stefan used to work at IBM",
        "elijah likes to go biking",
        "stefan likes to bake sourdough",
    ]
    vector_store = bootstrap_vector_db(conversational_rag_driver, input_text)
    return vector_store



@pytest.mark.file_name("ai_converse.json")
def test_ai_converse(input_state, expected_state, vector_store):
    """Function for testing the action"""
    input_state = state.State(input_state)
    expected_state = state.State(expected_state)
    _, output_state = ai_converse(input_state, vector_store)  # exercise the action
    # TODO: choose appropriate way to evaluate the output
    # e.g. exact match, fuzzy match, LLM grade, etc.
    # this is exact match here on all values in state
    assert output_state == expected_state
    # e.g.
    # assert 'some value' in output_state["response"]["content"]
    # assert llm_evaluator(..., ...) == "Y"
