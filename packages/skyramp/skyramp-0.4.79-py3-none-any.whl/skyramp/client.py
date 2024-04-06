"""
Defines a Skyramp client, which can be used to interact with a cluster.
"""
import os
import ctypes
import json
from typing import List, Union, Optional
import yaml

from skyramp.utils import _library, _call_function, add_unique_items
from skyramp.test_assert import _Assert
from skyramp.scenario import _Scenario
from skyramp.endpoint import _Endpoint
from skyramp.test_description import _TestDescription
from skyramp.test_request import _Request
from skyramp.utils import SKYRAMP_YAML_VERSION
from skyramp.response import _ResponseValue
from skyramp.mock_description import _MockDescription
from skyramp.traffic_config import _TrafficConfig
from skyramp.test_status import TestStatusV1, TestStatusV2, TestStatus
class TesterInfoType(ctypes.Structure):
    """ c type for tester info"""
    _fields_ = [
        ("tester_id", ctypes.c_char_p),
        ("error", ctypes.c_char_p),
    ]
class _ClientBase:
    """
    Client base class.
    """
    def __init__(self):
        self.project_path = None
        self.global_headers = {}

    def mocker_apply(self, namespace: str, address: str, endpoint) -> None:
        """
        Applies a mock configuration to K8s if `namespace` is provided,
        or to docker if `address` is provided.

        Args:
            namespace: The namespace where Mocker resides
            address: The address of Mocker
            endpoint: The Skyramp enpdoint object
        """
        yaml_string = yaml.dump(endpoint.mock_description)

        func = _library.applyMockDescriptionWrapper
        argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        _call_function(
            func,
            argtypes,
            ctypes.c_char_p,
            [
                namespace.encode(),
                address.encode(),
                yaml_string.encode(),
                "".encode(),
                "".encode(),
            ],
        )

    def mocker_apply_using_mock_file(
            self,
            namespace: str,
            address: str,
            mock_file: str,
            ) -> None:
        """
        Applies mock configuration to K8s if `namespace` is provided,
        or to docker if `address` is provided.

        Args:
            namespace: The k8s namespace where Mocker resides
            address: The docker address where Mocker resides
            mock_file: The file containing the mock configuration
        """
        if not self.project_path:
            raise Exception("project path not set")
        current_directory = os.getcwd()
        os.chdir(self.project_path)
        func = _library.applyMockDescriptionWrapper
        argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        _call_function(
            func,
            argtypes,
            ctypes.c_char_p,
            [
                namespace.encode(),
                address.encode(),
                "".encode(),
                mock_file.encode(),
                self.project_path.encode(),
            ],
        )
        os.chdir(current_directory)

    def mocker_apply_v1(
            self,
            namespace: str,
            address: str,
            response: Union[_ResponseValue, List[_ResponseValue]],
            traffic_config: _TrafficConfig=None,
            ) -> None:
        """
        Applies mock configuration to K8s if `namespace` is provided,
        or to docker if `address` is provided.

        Args:
            namespace: The k8s namespace where Mocker resides
            address: The docker address where Mocker resides
            response: The responses to apply to Mocker
            traffic_config: Traffic config
        """
        responses = response
        if isinstance(responses, _ResponseValue):
            responses = [responses]
        if isinstance(responses, list):
            mock_description = self.get_mock_description_v1(responses, traffic_config)
            yaml_string = yaml.dump(mock_description.to_json())

            func = _library.applyMockDescriptionWrapper
            argtypes = [
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
            ]

            _call_function(
                func,
                argtypes,
                ctypes.c_char_p,
                [
                    namespace.encode(),
                    address.encode(),
                    yaml_string.encode(),
                    "".encode(),
                    "".encode(),
                ],)

    def set_project_directory(self, path: str) -> None:
        """
        Sets the project directory for the client.

        Args:
            path: The path to the project directory
        """
        self.project_path = path
        func = _library.setProjectDirectoryWrapper
        argtypes = [ctypes.c_char_p]
        restype = ctypes.c_char_p

        return _call_function(func, argtypes, restype, [path.encode()])

    def tester_start_using_test_file(
            self,
            namespace: str,
            address:str,
            file_name: str,
            test_name: str,
            blocked=False,
            global_headers: map=None,
        ) ->  TestStatus:
        """
        Loads test from a test file.

        Args:
            namespace: The namespace where the worker resides
            address: The address of the worker
            file_name: The name of the file
            test_name: The name of the test
            blocked: Whether to wait for the test to finish
            global_headers: Global headers to be used for all requests
        """
        if not self.project_path:
            raise Exception("project path not set")
        current_directory = os.getcwd()
        os.chdir(self.project_path)
        # combine all the scenarios into one test_description
        func = _library.runTesterStartWrapperWithGlobalHeaders
        func.argtypes = [
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_bool,
                ctypes.c_char_p,
                ctypes.c_char_p,
            ]
        func.restype = TesterInfoType
        args = [
                namespace.encode(),
                address.encode(),
                "".encode(),
                file_name.encode(),
                test_name.encode(),
                json.dumps(global_headers).encode(),
                True,
                self.project_path.encode(),
                "".encode(),
            ]
        result = func(*args)
        if result.error:
            raise Exception(ctypes.c_char_p(result.error).value)
        os.chdir(current_directory)
        if blocked:
            return self._get_tester_status(
                namespace,
                address,
                ctypes.c_char_p(result.tester_id).value,
                True,
                )
        return None

    def _get_tester_status(
            self,
            namespace: str,
            address: str,
            tester_id: str,
            is_formatting_enabled: bool
        ) -> TestStatus:
        '''
        Get the status of the test
        '''
        tester_status_raw = _call_function(
            _library.runTesterStatusWrapper,
            [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool],
            ctypes.c_char_p,
            [namespace.encode(), address.encode(), tester_id, is_formatting_enabled],
            return_output=True,
        )

        tester_status = ""
        try:
            tester_status = json.loads(tester_status_raw)
        except ValueError as error:
            raise Exception(f"Could not parse tester status: {error}")
        if "error" in tester_status and tester_status["error"] != "":
            raise Exception(tester_status["error"])
        if  is_formatting_enabled:
            return TestStatusV2({"test_results": tester_status})
        return TestStatusV1({"test_results": tester_status})

    def load_endpoint(self, name: str) -> _Endpoint:
        """
        Loads an endpoint from a file.

        Args:
            name: The name of the endpoint
        """
        if not self.project_path:
            raise Exception("project path not set")
        func = _library.getEndpointFromProjectWrapper
        argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        restype = ctypes.c_char_p

        endpoint_data = _call_function(
            func,
            argtypes,
            restype,
            [
                name.encode(),
                self.project_path.encode(),
            ],
            True,
        )
        if not endpoint_data:
            raise Exception(f"endpoint {name} not found")
        try:
            endpoint = json.loads(endpoint_data)
        except json.JSONDecodeError:
            raise ValueError(f"Endpoint data for {name} is not valid JSON")
        return _Endpoint(json.dumps(endpoint))

    def override_assert_code(self,
                            scenario: _Scenario,
                            override_code: Optional[dict]=None ) -> None:
        """
        Overrides the expected value of assert steps in a given scenario.

        Args:
            scenario (_Scenario): The scenario object containing the steps.
            override_code (Optional[dict]): A dictionary from user 
                provided yaml file 

        Returns:
            None
        """
        if not override_code:
            return
        for step in scenario.steps_v1:
            if isinstance(step.step, _Assert):
                if step.step.assert_step_name in override_code:
                    new_code = override_code[step.step.assert_step_name]
                    step.step.assert_expected_value = new_code
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def tester_start_v1(
            self,
            scenario: Union[_Scenario, List[_Scenario]],
            global_headers: map=None,
            namespace: str="",
            address: str="",
            test_name: str="",
            blocked=False,
            global_vars: map=None,
            override_code_path: Optional[str] = None,
            endpoint_address: Optional[str] = None,
            pip_requirements: Optional[str] = None,
            at_once: Optional[int] = None,
            duration: Optional[str] = None,
            stop_on_failure: Optional[bool] = False,
            skip_verify: Optional[bool] = None,
            blobs: Optional[dict] = None,
            is_formatting_enabled: bool = False,
           ) ->  TestStatus:
        """
        Runs testers. If namespace is provided, connects with the worker instance running
        on the specified namespace in the registered Kubernetes cluster. If address is provided,
        connects to the worker directly using the network address.
        Args:
            scenario: Scenario object for the test to run
            global_headers: Global headers to be used for all requests
            namespace: The namespace where mocker resides
            address: The address to reach mocker
            test_name: The name of the test
            blocked: Whether to wait for the test to finish
            global_vars: Global variables to be used for all requests
            override_code_path: A path to a file with assert codes to use as overrides
            endpoint_address: The address to reach the endpoint
            pip_requirements: The pip requirements to use
            at_once: The number of threads for load test configuration, default is 1
            duration: The duration of the load test in seconds (e.g. 1s, 1m, 1h)
            stop_on_failure: Whether to stop the test on failure
        Returns:
            The status of the test
        """
        # pylint: disable=line-too-long
        if scenario is None:
            raise Exception("no scenario provided")
        # convert global_vars to dict if it is a string to support robot framework
        if global_vars is not None and isinstance(global_vars, dict) is False:
            global_vars = dict(json.loads((global_vars)))
        override_code_path = override_code_path or ""
        if isinstance(scenario, list):
            test_description = _TestDescription(
                version= SKYRAMP_YAML_VERSION,
                test= {
                    "testPattern": [],
                },
                scenarios=[],
                services=[],
                requests=[],
                endpoints=[],
            )
            for test_scenario in scenario:
                test_desc = self.get_test_description_v1(test_scenario)
                for service in test_desc.services:
                    if endpoint_address:
                        service["addr"] = endpoint_address
                        del service["alias"]
                add_unique_items(test_description.services, test_desc.services)
                add_unique_items(test_description.endpoints, test_desc.endpoints)
                add_unique_items(test_description.requests, test_desc.requests)

                add_unique_items(test_description.scenarios, test_desc.scenarios)
                # combine all the test patterns into one test_description
                test_pattern = test_desc.test["testPattern"]
                for pattern in test_pattern:
                    if at_once:
                        pattern["atOnce"] = at_once
                    if duration:
                        pattern["duration"] = duration
                    if stop_on_failure:
                        pattern["stopOnFailure"] = stop_on_failure
                add_unique_items(test_description.test["testPattern"], test_pattern)
        else:
            test_description = self.get_test_description_v1(scenario)
            for service in test_description.services:
                if endpoint_address:
                    service["addr"] = endpoint_address
                    del service["alias"]
            for pattern in test_description.test["testPattern"]:
                if at_once:
                    pattern["atOnce"] = at_once
                if duration:
                    pattern["duration"] = duration
                if stop_on_failure:
                    pattern["stopOnFailure"] = stop_on_failure

        test_description.test["name"] = test_name

        if global_vars is not None:
            test_description.test["globalVars"] = global_vars
        if pip_requirements is not None:
            test_description.test["pipRequirements"] = pip_requirements
        if skip_verify is not None:
            test_description.test["skipVerify"] = skip_verify
        # blob override
        if blobs is not None:
            test_description.test["override"] = {}
            test_description.test["override"]["blobs"] = blobs

        # combine all the scenarios into one test_description
        func = _library.runTesterStartWrapperWithGlobalHeaders
        func.argtypes = [
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_bool,
                ctypes.c_char_p,
                ctypes.c_char_p,
            ]
        func.restype = TesterInfoType
        args = [
                namespace.encode(),
                address.encode(),
                yaml.dump(test_description, default_style='"').encode(),
                "".encode(),
                test_name.encode(),
                json.dumps(global_headers).encode(),
                True,
                "".encode(),
                override_code_path.encode(),
            ]
        result = func(*args)
        if result.error:
            raise Exception(ctypes.c_char_p(result.error).value)
        if blocked:
            return self._get_tester_status(
                namespace,
                address,
                ctypes.c_char_p(result.tester_id).value,
                is_formatting_enabled,
                )
        return None

    def set_global_rest_headers(self, global_headers) -> None:
        """
        Sets the global REST headers for this client.
        
        Args:
            global_headers: The global headers to set
        """
        self.global_headers=global_headers

    def get_mock_description_v1(
            self,
            responses: List[_ResponseValue],
            traffic_config: _TrafficConfig) -> _MockDescription:
        """
        Helper for returning the mock description for the response

        Args:
            responses: The responses to mock
            traffic_config: Traffic config
        """
        mock = {
            "responses": [],
            "proxies": [],
        }
        response_dict = {}
        service_dict = {}
        endpoint_dict = {}
        if traffic_config is not None:
            mock.update(traffic_config.to_json())
        mock_res = mock["responses"]
        for response in responses:
            if isinstance(response, _ResponseValue):
                response_json = response.to_json()
                # if the response is a proxy live service, add it to the proxies list
                if response.proxy_live_service:
                    mock["proxies"].append({
                    "endpointName": response.endpoint_descriptor.endpoint.get("name"),
                    "methodName": response.method_name,
                })
                response_dict[response.name] = response_json
                if response.response_value is not None:
                    response_dict[response.name]["override"] = response.response_value
                if response.cookie_value is not None:
                    response_dict[response.name]["cookies"] = response.cookie_value
                res = {
                    "responseName": response.name,
                }
                if response.traffic_config is not None:
                    res.update(response.traffic_config.to_json())
                mock_res.append(res)

                for service in response.endpoint_descriptor.services:
                    service_dict[service.get("name")] = service
                endpoint = response.endpoint_descriptor.endpoint
                endpoint_dict[endpoint.get("name")] = endpoint

        # All of the endpoints and services are within the response object
        return _MockDescription(
            version=SKYRAMP_YAML_VERSION,
            mock=mock,
            services=list(service_dict.values()),
            responses=list(response_dict.values()),
            endpoints=list(endpoint_dict.values()),
            )

    # pylint: disable=too-many-branches
    def get_test_description_v1(self, scenario: _Scenario) -> _TestDescription:
        """
        Helper for returning the test description for the scenario

        Args:
            scenario: The scenario to test

        Returns:
            The test description
        """
        request_dict = {}
        service_dict = {}
        endpoint_dict = {}
        scenario_dict = {scenario.name: scenario.as_scenario_dict()}

        for step_v1 in scenario.steps_v1:
            if isinstance(step_v1.step, _Request):
                request_dict[step_v1.step.name] = step_v1.step.as_request_dict(self.global_headers)

                for service in step_v1.step.endpoint_descriptor.services:
                    service_dict[service.get("name")] = service
                endpoint = step_v1.step.endpoint_descriptor.endpoint
                if endpoint.get("name") not in endpoint_dict:
                    endpoint_dict[endpoint.get("name")] = endpoint

                # Add the method to the endpoint if it doesn't exist
                svc = service_dict[endpoint.get("serviceName")]
                method_exists = False
                method_name = getattr(step_v1.step, "method_name", None)
                if method_name is None:
                    method_name = getattr(step_v1.step, "method_type", None)
                if "methods" in endpoint:
                    for method in endpoint["methods"]:
                        if method["name"] == method_name:
                            method_exists = True
                            break
                if not method_exists:
                    if svc['protocol'] == "rest":
                        endpoint_dict[endpoint.get("name")]["methods"].append({
                            "name": method_name,
                            "type": method_name,
                        })
                    else:
                        endpoint_dict[endpoint.get("name")]["methods"].append({
                            "name": method_name,
                        })

            if isinstance(step_v1.step, _Scenario):
                child_test_desc = self.get_test_description_v1(step_v1.step)
                for request in child_test_desc.requests:
                    request_dict[request.get("name")] = request
                for service in child_test_desc.services:
                    service_dict[service.get("name")] = service
                for endpoint in child_test_desc.endpoints:
                    endpoint_dict[endpoint.get("name")] = endpoint
                for _scenario in child_test_desc.scenarios:
                    scenario_dict[_scenario.get("name")] = _scenario

        # All of the endpoints and services are within the requests_v1 object
        test_desc =_TestDescription(
            version=SKYRAMP_YAML_VERSION,
            test={
                "testPattern": [{"startAt": scenario.start_at, "scenarioName": scenario.name}],
            },
            scenarios=list(scenario_dict.values()),
            services=list(service_dict.values()),
            requests=list(request_dict.values()),
            endpoints=list(endpoint_dict.values()),
            )

        return test_desc

    def deploy_target(
        self,
        target_description_path: str,
        namespace: str,
        worker_image: str,
        local_image: bool,
    ) -> None:
        """
        Helps to deploy a target

        Args:
            target_description_path: The path of the target description
            namespace: The namespace where the target will be deployed
            worker_image: The image of the worker
            local_image: Whether the image is local
        """
        func = _library.deployTargetWrapper
        arg_types = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
        restype = ctypes.c_char_p

        _call_function(
            func,
            arg_types,
            restype,
            [
                target_description_path.encode(),
                namespace.encode(),
                worker_image.encode(),
                local_image,
            ],
        )

    def delete_target(self, target_description_path: str, namespace: str) -> None:
        """
        this function is used to delete a target

        Args:
            target_description_path: The path of the target description
            namespace: The namespace where the target will be deployed
        """
        func = _library.deleteTargetWrapper
        arg_types = [ctypes.c_char_p, ctypes.c_char_p]
        restype = ctypes.c_char_p

        _call_function(
            func,
            arg_types,
            restype,
            [
                target_description_path.encode(),
                namespace.encode(),
            ]
        )
