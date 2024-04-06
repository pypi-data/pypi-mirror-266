"""
Contains helpers for interacting with Skyramp test assert.
"""
from typing import Callable, Optional
import inspect
class _Assert:
    def __init__(
            self,
            assert_value: str="",
            assert_expected_value: str="",
            assert_unexpected_value: str="",
            assert_function: Optional[Callable] = None,
            assert_step_name: Optional[str]="",
            description: Optional[str]="",
        ) -> None:
        self.assert_value = assert_value
        self.assert_expected_value = assert_expected_value
        self.assert_unexpected_value = assert_unexpected_value
        self.assert_function = assert_function
        self.assert_step_name = assert_step_name
        self.description = description

    def to_json(self):
        """
        Convert the object to dictionary
        """
        value = self.assert_value
        if not (self.assert_value.startswith("requests.") or \
                self.assert_value.startswith("vars.")):
            value = f"requests.{self.assert_value}"
        if self.assert_function:
            return {
                "assertsPython": inspect.getsource(self.assert_function)
            }
        assert_string = f'{value} == "{self.assert_expected_value}"'
        if self.assert_unexpected_value:
            assert_string = f'{value} != "{self.assert_unexpected_value}"'

        return {
            "asserts": assert_string,
            "description": self.description,
            "name": self.assert_step_name
        }
