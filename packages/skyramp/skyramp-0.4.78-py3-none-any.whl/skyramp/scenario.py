"""
Contains helpers for interacting with Skyramp testing scenarios.
"""

import ctypes
from typing import Callable, Optional
import inspect
import json
import os
import yaml

from typing_extensions import Self
from skyramp.utils import _library, _call_function
from skyramp.endpoint import _Endpoint
from skyramp.test_request import _Request
from skyramp.test_assert import _Assert


class _Step:
    def __init__(
        self,
        step,
        max_retries: int = 0,
        interval: str = "",
        until: str = "",
        blob_override: Optional[dict] = None,
        vars_override: Optional[dict] = None,
        description: Optional[str] = None,
        step_name: Optional[str] = None,
        break_: bool = False,
        ignore: bool = False,
        if_: Optional[str] = None,
        export: Optional[dict] = None,
        until_func: Optional[Callable] = None,
        wait: str = "",
    ) -> None:
        self.step = step
        self.max_retries = max_retries
        self.interval = interval
        self.until = until
        self.response_value = None
        self.cookie_value = None
        self.response_code = 0
        self.vars_override = vars_override
        self.blob_override = blob_override
        self.description = description
        self.step_name = step_name
        self.break_ = break_
        self.ignore = ignore
        self.if_ = if_
        self.export = export
        self.until_func = until_func
        self.wait = wait

    def override_vars(self, vars_: Optional[dict]):
        """
        Overrides the vars for this step
        """
        self.vars_override = vars_

    def override_blob(self, blob_override: Optional[dict]):
        """
        Overrides the blob for this step
        """
        self.blob_override = blob_override

    def set_value(self, response_value: json):
        """
        Sets the response value for this step
        """
        self.response_value = response_value

    def set_cookie_value(self, cookie_value: json):
        """
        Sets the cookie value for this step
        """
        self.cookie_value = cookie_value

    def get_request(self):
        """
        Gets the request value for this step
        """
        if self.step is not None and isinstance(self.step, _Request):
            if not self.step.name.startswith("requests."):
                return f"requests.{self.step.name}"
            return f"{self.step.name}"
        raise Exception("Step is not a request")

    def get_scenario(self):
        """
        Gets the scenario for this step
        """
        if self.step is not None and isinstance(self.step, _Scenario):
            if not self.step.name.startswith("scenarios."):
                return f"scenarios.{self.step.name}"
            return f"{self.step.name}"
        raise Exception("Step is not a scenario")

    def get_scenario_value(self, json_path: str):
        """
        Gets the response value for this step
        """
        scenario = self.get_scenario()
        return f"{scenario}.{json_path}"

    def get_response_code(self):
        """
        Gets the response code for this step
        """
        request = self.get_request()
        return f"{request}.code"

    def get_response_value(self, json_path: str = "") -> str:
        """
        Gets the response value for this step based on the provided JSON path.
        If the JSON path is empty, it returns the entire response.

        Example JSON path: "body.data"
        """
        request = self.get_request()
        if json_path == "":
            return f"{request}.res"
        return f"{request}.res.{json_path}"

    def get_response_cookies_value(self, json_path: str):
        """
        Gets the response value for this step
        """
        request = self.get_request()
        return f"{request}.cookies.{json_path}"

    # pylint: disable=too-many-branches
    def to_json(self):
        """
        Convert the object to dictionary
        """
        step_dict = self.step.to_json()

        if self.description:
            step_dict["description"] = self.description
        if self.step_name:
            step_dict["name"] = self.step_name
        if self.max_retries or self.interval or self.until or self.until_func:
            step_dict["repeat"] = {}
        if self.max_retries:
            step_dict["repeat"]["maxRetries"] = self.max_retries
        if self.interval:
            step_dict["repeat"]["interval"] = self.interval
        if self.until:
            step_dict["repeat"]["until"] = self.until
        if self.until_func:
            step_dict["repeat"]["untilPython"] = inspect.getsource(self.until_func)
        if self.vars_override:
            step_dict["override"] = self.vars_override
        if self.blob_override:
            step_dict["blobOverride"] = self.blob_override
        if self.break_:
            step_dict["break"] = self.break_
        if self.ignore:
            step_dict["ignore"] = self.ignore
        if self.if_:
            step_dict["if"] = self.if_
        if self.export:
            step_dict["export"] = self.export
        if self.wait:
            step_dict["wait"] = self.wait

        return step_dict


class _Scenario:
    """
    Represents a testing scenario.
    """

    def __init__(
        self,
        name: str,
        start_at: int = 1,
        vars_: Optional[dict] = None,
        headers: Optional[dict] = None,
        ignore: bool = False,
    ) -> None:
        self.name = name

        self.steps = []
        self.steps_v1 = []

        self.global_headers = {}

        self.services = []
        self.endpoints = []
        self.requests = []
        self.scenarios = []
        self.start_at = start_at
        self.vars = vars_
        self.headers = headers

        self.ignore = ignore

    def add_request(
        self,
        endpoint: _Endpoint,
        method_name: str,
        request_object=None,
        dynamic: bool = False,
    ) -> str:
        """
        Adds a request to this scenario.

        Args:
            endpoint: The endpoint object associated with the request
            method_name: The name of the method that this request will be hitting
            request_object: Map containing request information
            dynamic: Whether or not the request_object is a dynamic script

        Returns:
            The name of the request that was added
        """
        self._build_metadata_for_endpoint(endpoint)

        for request in self.requests:
            if request["methodName"] != method_name:
                continue

            if dynamic:
                request["javascriptPath"] = request_object
                request.pop("blob", None)
            elif request_object is not None:
                request["blob"] = request_object["requestValue"]["blob"]
            self.steps += [{"requestName": request["name"]}]
            return request["name"]

    def add_request_from_file(
        self, endpoint: _Endpoint, method_name: str, request_file: str
    ) -> str:
        """
        Adds the request in the specified file to the corresponding endpoint and method.

        Args:
            endpoint: The endpoint object associated with the request
            method_name: The name of the method that this request will be hitting
            request_file: The path to the file containing the request information
        """
        _, file_ext = os.path.splitext(request_file)

        try:
            with open(request_file) as file:
                file_contents = file.read()
        except:
            raise Exception(f"failed to open file: {request_file}")
        # pylint: disable=duplicate-code
        dynamic = False

        if file_ext == ".json":
            data = json.loads(file_contents)
        elif file_ext in [".yaml", ".yml"]:
            data = yaml.safe_load(file_contents)
        elif file_ext == ".js":
            dynamic = True
            data = request_file
        else:
            raise Exception(
                f"unsupported file format: {file_ext}. Only JSON, YAML, and JS are supported"
            )

        return self.add_request(endpoint, method_name, data, dynamic)

    def add_assert_equal(self, value_name: str, expected_value: str):
        """
        Adds an assert equal given the value expression and expected value

        Args:
            value_name: The name of the value to assert
            expected_value: The expected value
        """
        assertion = f'requests.{value_name} == "{expected_value}"'
        self.steps.append({"asserts": assertion})

    def add_assert_v1(
        self,
        assert_value: str = "",
        assert_expected_value: str = "",
        assert_unexpected_value: str = "",
        assert_step: _Assert = None,
        max_retries: int = 0,
        interval: str = "",
        until: str = "",
        assert_step_name: str = "",
        description: str = "",
        ignore: bool = False,
        break_: bool = False,
        if_: str = "",
    ):
        """
        Adds an assert given the value expression and expected value

        Args:
            assert_value: The name of the value to assert
            assert_expected_value: The expected value
            assert_unexpected_value: The unexpected value
            assert_step: The assert step
            max_retries: The maximum number of retries
            interval: The interval between retries
            until: The condition to stop retrying
            assert_step_name: Assert step name used by the code
                              generation to support assert override
            description: The description of the assert step
            ignore: If set, a failure will not break out of the scenario
            break_: If set, will break out of the test after the assert (for debugging)
            if_: If condition for executing this assert
        """
        if assert_step is not None:
            self.steps_v1.append(
                _Step(
                    assert_step,
                    max_retries,
                    interval,
                    until,
                    ignore=ignore,
                    break_=break_,
                    if_=if_,
                )
            )
        else:
            assert_step = _Assert(
                assert_value=assert_value,
                assert_expected_value=assert_expected_value,
                assert_unexpected_value=assert_unexpected_value,
                assert_step_name=assert_step_name,
                description=description,
            )
            self.steps_v1.append(
                _Step(
                    assert_step,
                    max_retries,
                    interval,
                    until,
                    ignore=ignore,
                    break_=break_,
                    if_=if_,
                )
            )

    def _build_metadata_for_endpoint(self, endpoint: _Endpoint):
        if endpoint.endpoint in self.endpoints:
            return

        self.services += endpoint.services

        self.endpoints.append(endpoint.endpoint)

        mock_description_yaml = yaml.dump(endpoint.mock_description)

        func = _library.buildRequestsWrapper
        argtypes = [ctypes.c_char_p]
        restype = ctypes.c_char_p

        requests = _call_function(
            func,
            argtypes,
            restype,
            [mock_description_yaml.encode()],
            return_output=True,
        )

        parsed_requests = json.loads(requests)
        self.requests.append(parsed_requests[0])

    def set_global_headers(self, headers):
        """
        Sets the global headers for this scenario
        """
        self.global_headers = headers

    # pylint: disable=too-many-locals
    def add_request_v1(
        self,
        request: _Request,
        max_retries: int = 0,
        interval: str = "",
        until: str = "",
        vars_override: Optional[dict] = None,
        blob_override: Optional[dict] = None,
        description: str = "",
        step_name: str = "",
        ignore: bool = False,
        break_: bool = False,
        if_: str = "",
        export: Optional[dict] = None,
        until_func: Optional[str] = None,
        wait: str = "",
    ) -> _Step:
        """
        Adds a request to this scenario.

        Args:
            request: request information
            max_retries: The maximum number of retries
            interval: The interval between retries
            until: The condition to stop retrying
            ignore: If set, a failure will not break out of the scenario
            break_: If set, will break out of the test after the request (for debugging)
            if_: If condition for executing this request
            until_func: The repeat function to use for this step
        Returns:
            The name of the step that was added
        """
        step = _Step(
            request,
            max_retries,
            interval,
            until,
            vars_override=vars_override,
            blob_override=blob_override,
            description=description,
            step_name=step_name,
            ignore=ignore,
            break_=break_,
            if_=if_,
            export=export,
            until_func=until_func,
            wait=wait,
        )

        self.steps_v1.append(step)
        return step

    # pylint: disable=too-many-locals
    def add_scenario_v1(
        self,
        scenario:  Self,
        max_retries: int = 0,
        interval: str = "",
        until: str = "",
        vars_override: Optional[dict]=None,
        description: Optional[str]="",
        step_name: str='',
        break_: bool=False,
        ignore: bool = False,
        if_: str = "",
        export: Optional[dict]=None,
        wait: str="",
    ) -> _Step:
        """
        Adds a scenario to this scenario.

        Args:
            scenario: scenario information
        Returns:
            The name of the step that was added
        """
        # pylint: disable=line-too-long
        step = _Step(
            step=scenario,
            max_retries=max_retries,
            interval=interval,
            until=until,
            vars_override=vars_override,
            description=description,
            step_name=step_name,
            break_=break_,
            ignore=ignore,
            if_=if_,
            export=export,
            wait=wait,)
        self.steps_v1.append(step)
        return step

    # pylint: disable=too-many-branches, too-many-statements
    def as_scenario_dict(self):
        """
        Convert the object to a JSON string.
        """
        # pylint: disable=too-many-branches
        steps = []
        for step_v1 in self.steps_v1:
            step = {}
            if isinstance(step_v1.step, _Assert):
                step = step_v1.step.to_json()
            if isinstance(step_v1.step, _Request):
                step = step_v1.step.to_json()
                if step_v1.max_retries or step_v1.interval or step_v1.until or step_v1.until_func:
                    step["repeat"] = {}
                if step_v1.max_retries:
                    step["repeat"]["maxRetries"] = step_v1.max_retries
                if step_v1.interval:
                    step["repeat"]["interval"] = step_v1.interval
                if step_v1.until:
                    step["repeat"]["until"] = step_v1.until
                if step_v1.until_func:
                    step["repeat"]["untilPython"] = inspect.getsource(step_v1.until_func)
                if step_v1.vars_override is not None:
                    step["override"] = step_v1.vars_override
                if step_v1.blob_override is not None:
                    step["blobOverride"] = step_v1.blob_override
            if isinstance(step_v1.step, _Scenario):
                step["scenarioName"] = step_v1.step.name
                step["description"] = step_v1.description
                if step_v1.vars_override is not None:
                    step["override"] = step_v1.vars_override
                if step_v1.max_retries or step_v1.interval or step_v1.until or step_v1.until_func:
                    step["repeat"] = {}
                if step_v1.max_retries:
                    step["repeat"]["maxRetries"] = step_v1.max_retries
                if step_v1.interval:
                    step["repeat"]["interval"] = step_v1.interval
                if step_v1.until:
                    step["repeat"]["until"] = step_v1.until
                if step_v1.until_func:
                    step["repeat"]["untilPython"] = inspect.getsource(step_v1.until_func)
            if step_v1.step_name is not None and step_v1.step_name != "":
                step["name"] = step_v1.step_name
            if step_v1.description is not None and step_v1.description != "":
                step["description"] = step_v1.description
            if step_v1.response_value is not None:
                step["override"] = step_v1.response_value
            if step_v1.cookie_value is not None:
                step["cookies"] = step_v1.cookie_value
            if step_v1.if_ is not None and step_v1.if_ != "":
                step["if"] = step_v1.if_
            if step_v1.export is not None:
                step["export"] = step_v1.export
            if step_v1.wait:
                step["wait"] = step_v1.wait
            steps.append(step)

        scenario_dict = {
            "name": self.name,
            "steps": steps,
            "ignore": self.ignore,
        }

        if self.vars is not None:
            scenario_dict["vars"] = self.vars
        if self.headers is not None:
            scenario_dict["headers"] = self.headers

        return scenario_dict
