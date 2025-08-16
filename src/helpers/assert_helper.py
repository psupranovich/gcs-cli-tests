from assertpy import assert_that

from src.helpers.data_helper import GCPCommandResponse


class AssertHelper:
    @staticmethod
    def assert_error_response(
        response: GCPCommandResponse, expected_message: str, code: int = 1
    ) -> None:
        """
        Assert that a response contains an expected error message.
        """
        assert_that(response.status_code).is_equal_to(code)
        assert_that(response.output).contains(expected_message)
