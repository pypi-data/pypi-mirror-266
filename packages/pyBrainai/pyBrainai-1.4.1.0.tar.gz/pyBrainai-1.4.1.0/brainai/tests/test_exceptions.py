import pickle

import pytest

import brainai

EXCEPTION_TEST_CASES = [
    brainai.InvalidRequestError(
        "message",
        "param",
        code=400,
        http_body={"test": "test1"},
        http_status="fail",
        json_body={"text": "iono some text"},
        headers={"request-id": "asasd"},
    ),
    brainai.error.AuthenticationError(),
    brainai.error.PermissionError(),
    brainai.error.RateLimitError(),
    brainai.error.ServiceUnavailableError(),
    brainai.error.SignatureVerificationError("message", "sig_header?"),
    brainai.error.APIConnectionError("message!", should_retry=True),
    brainai.error.TryAgain(),
    brainai.error.Timeout(),
    brainai.error.APIError(
        message="message",
        code=400,
        http_body={"test": "test1"},
        http_status="fail",
        json_body={"text": "iono some text"},
        headers={"request-id": "asasd"},
    ),
    brainai.error.brainaiError(),
]


class TestExceptions:
    @pytest.mark.parametrize("error", EXCEPTION_TEST_CASES)
    def test_exceptions_are_pickleable(self, error) -> None:
        assert error.__repr__() == pickle.loads(pickle.dumps(error)).__repr__()
