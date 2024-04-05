"""
TestStatus module
"""
from typing import List
import json


class TesterStatusType:
    """
    TesterStatusType object
    """
    Idle = "idle"
    Initializing = "initializing"
    Waiting = "waiting"
    Running = "running"
    Failed = "failed"
    Skipped = "skipped"
    Stopping = "stopping"
    Stopped = "stopped"
    Finished = "finished"

class TestResultType:
    """
    TestResultType object
    """
    NoneType = ""
    Command = "command"
    Request = "request"
    Scenario = "scenario"
    Load = "load"
    Repeat = "repeat"
    Assert = "assert"
    With = "with"

class TestTimeseriesStat:
    """
    TestTimeseriesStat object
    """
    timestamp: str = ""
    error_rate: str = ""
    rps: str = ""
    avg_latency: str = ""

    def __init__(self, options: dict):
        if "timestamp" in options:
            self.timestamp = options["timestamp"]
        if "errorRate" in options:
            self.error_rate = options["errorRate"]
        if "RPS" in options:
            self.rps = options["RPS"]
        if "avgLatency" in options:
            self.avg_latency = options["avgLatency"]

    def __repr__(self):
        _data = {
            "timestamp": self.timestamp,
            "error_rate": self.error_rate,
            "rps": self.rps,
            "avg_latency": self.avg_latency
        }
        filtered_data = {k: v for k, v in _data.items() if v is not None and v != ""}
        return f"TestTimeseriesStat({json.dumps(filtered_data, indent=2)})"


class TestStat:
    """
    TestStat object
    """
    description: str = ""
    count: int = 0
    executed: int = 0
    fail: int = 0
    avg_latency: str = ""
    max_latency: str = ""
    min_latency: str = ""
    l99th_latency: str = ""
    l95th_latency: str = ""
    l90th_latency: str = ""

    def __init__(self, options: dict):
        if "Description" in options:
            self.description = options["Description"]
        if "Count" in options:
            self.count = options["Count"]
        if "Executed" in options:
            self.executed = options["Executed"]
        if "Fail" in options:
            self.fail = options["Fail"]
        if "AvgLatency" in options:
            self.avg_latency = options["AvgLatency"]
        if "MaxLatency" in options:
            self.max_latency = options["MaxLatency"]
        if "MinLatency" in options:
            self.min_latency = options["MinLatency"]
        if "L99thLatency" in options:
            self.l99th_latency = options["L99thLatency"]
        if "L95thLatency" in options:
            self.l95th_latency = options["L95thLatency"]
        if "L90thLatency" in options:
            self.l90th_latency = options["L90thLatency"]

    def __repr__(self):
        _data = {
            "description": self.description,
            "count": self.count,
            "executed": self.executed,
            "fail": self.fail,
            "avg_latency": self.avg_latency,
            "max_latency": self.max_latency,
            "min_latency": self.min_latency,
            "l99th_latency": self.l99th_latency,
            "l95th_latency": self.l95th_latency,
            "l90th_latency": self.l90th_latency
        }
        filtered_data = {k: v for k, v in _data.items() if v is not None and v != ""}
        return f"TestStat({json.dumps(filtered_data, indent=2)})"

class RequestLog:
    """
    RequestLog object
    """
    path: str = ""
    method: str = ""
    headers: dict = {}
    cookies: dict = {}
    payload: str = ""

    def __init__(self, options: dict):
        if "Path" in options:
            self.path = options["Path"]
        if "Method" in options:
            self.method = options["Method"]
        if "Headers" in options:
            self.headers = options["Headers"]
        if "Cookies" in options:
            self.cookies = options["Cookies"]
        if "Payload" in options:
            self.payload = options["Payload"]

    def __repr__(self):
        _data = {
            "path": self.path,
            "method": self.method,
            "headers": self.headers,
            "cookies": self.cookies,
            "payload": self.payload
        }
        filtered_data = {k: v for k, v in _data.items() if v is not None and v != ""}
        return f"RequestLog({json.dumps(filtered_data, indent=2)})"
class TesterState:
    """
    TesterState object
    """
    vars: dict = {}
    scenario_vars: dict = {}
    exports: dict = {}
    blob_overrides: dict = {}

    def __init__(self, options: dict):
        if "vars" in options:
            self.vars = options["vars"]
        if "scenarioVars" in options:
            self.scenario_vars = options["scenarioVars"]
        if "exports" in options:
            self.exports = options["exports"]
        if "blobOverrides" in options:
            self.blob_overrides = options["blobOverrides"]
    def __repr__(self):
        _data = {
            "vars": self.vars,
            "scenario_vars": self.scenario_vars,
            "exports": self.exports,
            "blob_overrides": self.blob_overrides
        }
        filtered_data = {k: v for k, v in _data.items() if v is not None and v != ""}
        return f"TesterState({json.dumps(filtered_data, indent=2)})"

class ResponseLog:
    """
    ResponseLog object
    """
    status_code: int = 0
    headers: dict = {}
    cookies: dict = {}
    payload: str = ""
    def __init__(self, options: dict):
        if "StatusCode" in options:
            self.status_code = options["StatusCode"]
        if "Headers" in options:
            self.headers = options["Headers"]
        if "Cookies" in options:
            self.cookies = options["Cookies"]
        if "Payload" in options:
            self.payload = options["Payload"]

    def __repr__(self):
        _data = {
            "status_code": self.status_code,
            "headers": self.headers,
            "cookies": self.cookies,
            "payload": self.payload
        }
        filtered_data = {k: v for k, v in _data.items() if v is not None and v != ""}
        return f"ResponseLog({json.dumps(filtered_data, indent=2)})"
class TestResult:
    """
    TestResult object
    """
    name: str=""
    status: str=""
    description: str=""
    step_description: str=""
    step_name: str=""
    error: str=""
    input: RequestLog=None
    output: ResponseLog=None
    type: TestResultType=""
    begin: int=0
    end: int=0
    duration: int=0
    timeseries: List[TestTimeseriesStat]=[]
    stat: TestStat=None
    state: TesterState=None

    # pylint: disable=too-many-branches
    def __init__(self, options: dict):
        if "name" in options:
            self.name = options["name"]
        if "status" in options:
            self.status = options["status"]
        if "description" in options:
            self.description = options["description"]
        if "stepDescription" in options:
            self.step_description = options["stepDescription"]
        if "stepName" in options:
            self.step_name = options["stepName"]
        if "error" in options:
            self.error = options["error"]
        if "input" in options:
            self.input = options["input"]
        if "output" in options:
            self.output = options["output"]
        if "type" in options:
            self.type = options["type"]
        if "begin" in options:
            self.begin = options["begin"]
        if "end" in options:
            self.end = options["end"]
        if "duration" in options and options["duration"] ==0:
            self.duration = options["duration"]
        if "timeseries" in options and options["timeseries"] ==[]:
            self.timeseries = options["timeseries"]
        if "stat" in options:
            self.stat = options["stat"]
        if "state" in options:
            self.state = options["state"]

    def __repr__(self):
        _data = {
            "name": self.name,
        }
        if self.status:
            _data["status"] = self.status
        if self.description:
            _data["description"] = self.description
        if self.step_description:
            _data["step_description"] = self.step_description
        if self.step_name:
            _data["step_name"] = self.step_name
        if self.error:
            _data["error"] = self.error
        return f"TestResult({json.dumps(_data, indent=2)})"

    def to_html(self):
        """
        Returns HTML text representation of the test status
        """
        html_content = "<div>\n"
        html_content += _html_entry("Step Name",self.name)
        html_content += _html_entry("Step Description",self.step_description)
        if self.error:
            html_content += _html_entry("Error",self.error)
        if self.input:
            html_content += _html_entry("Request",json.dumps(self.input, indent=2))
        if self.output:
            html_content += _html_entry("Response",json.dumps(self.output, indent=2))
        if self.stat:
            html_content += _html_entry("Stat",self.stat)
        if self.state:
            html_content += _html_entry("State",json.dumps(self.state, indent=2))
        if self.timeseries:
            html_content += _html_entry("Timeseries",self.timeseries)
        if self.duration:
            html_content += _html_entry("Duration",self.duration)
        if self.type:
            html_content += _html_entry("Type",self.type)
        if self.begin:
            html_content += _html_entry("Begin",self.begin)
        if self.end:
            html_content += _html_entry("End",self.end)
        html_content += _html_entry("Status",self.status)
        html_content += "</div>\n\n"
        return html_content

class TestStatus:
    """
    TestStatus object
    """
    test_results: List[List[TestResult]]     = []
    pass_status: bool = True
    def __init__(self, options: dict):
        self.test_results = []
        results = options.get("test_results", [])
        for result in results:
            scenario_data = []
            for step in result:
                scenario_data.append(TestResult(step))
            self.test_results.append(scenario_data)
        self.index = 0

    def __repr__(self):
        return f"TestStatus(test_results={self.test_results})"
    def __iter__(self):
        return self
    def __next__(self):
        if self.index < len(self.test_results):
            result = self.test_results[self.index]
            self.index += 1
            return result
        raise StopIteration
    def __getitem__(self, index):
        return self.test_results[index]
    def __len__(self):
        return len(self.test_results)
    def passed(self):
        """
        Returns True if all the tests passed
        """
        return self.pass_status
    def failed(self):
        """
        Returns True if any of the tests failed
        """
        failed_json =[]
        for result in self.test_results:
            for step in result:
                if step.status == TesterStatusType.Failed:
                    failed_json.append({
                        "name": step.name,
                        "step_description": step.step_description,
                        "request": step.input,
                        "response": step.output,
                        "status": step.status,
                        "error": step.error,
                    })
        return json.dumps(failed_json, indent=2)
    def to_html(self):
        """
        Returns HTML text representation of the test status
        """

        html_content = "<h1>Test Results</h1>\n"
        html_content += "<div class='test-results'>\n"
        for result in self.test_results:
            for step in result:
                html_content += step.to_html()
        html_content += "</div>\n"
        return html_content

def _html_entry(title, data):
    return f"<span><strong>{title}:</strong> {data}</span>\n"
