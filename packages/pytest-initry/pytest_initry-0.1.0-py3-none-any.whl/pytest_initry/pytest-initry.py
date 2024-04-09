import uuid
import time
from _pytest.mark import deselect_by_keyword, deselect_by_mark
from collections import deque
import grpc
from protobufs import test_run_pb2_grpc
from protobufs import test_pb2_grpc
from protobufs import tests_pb2_grpc
from protobufs import test_run_pb2
from protobufs import test_pb2
from protobufs import tests_pb2
from google.protobuf.timestamp_pb2 import Timestamp


class GrpcClient:
    def __init__(self, server_address, service_stub):
        self.server_address = server_address
        self.service_stub = service_stub

    def _create_channel(self):
        return grpc.insecure_channel(self.server_address)

    def _handle_rpc_error(self, e):
        pass

    def call_rpc_method(self, method_name, request):
        with self._create_channel() as channel:
            stub = self.service_stub(channel)

            try:
                rpc_method = getattr(stub, method_name)
                response = rpc_method(request)
                return response
            except grpc.RpcError as e:
                self._handle_rpc_error(e)
                return None

class PytestInitry:
    def __init__(self, config=None):
        self.config = config
        self.tests = list()
        # self.xmlpath = config.option.xmlpath
        self.test_run_uuid = str(uuid.uuid4())
        self.test_uuid = None
        self.pairs = []
        self.start_records = []
        self.finished_tests = deque()
        self.batching: bool = config.option.initry_batching
        self.initry_host = config.option.initry_host
        self.initry_grpc_host = config.option.initry_grpc_host
        self.test_run_grpc_client = GrpcClient(f"{self.initry_host}:{self.initry_grpc_host}", test_run_pb2_grpc.TestRunServiceStub)
        self.test_grpc_client = GrpcClient(f"{self.initry_host}:{self.initry_grpc_host}", test_pb2_grpc.TestServiceStub)
        self.cs_test_grpc_client = GrpcClient(f"{self.initry_host}:{self.initry_grpc_host}", test_pb2_grpc.ClientStreamTestServiceStub)
        self.tests_grpc_client = GrpcClient(f"{self.initry_host}:{self.initry_grpc_host}", tests_pb2_grpc.TestsServiceStub)

    def append_test(self, item):
        test = dict()
        test["location"] = item.location[2]
        test["nodeid"] = item.nodeid
        test["uuid"] = str(uuid.uuid4())
        test["test_run_uuid"] = self.test_run_uuid
        test["description"] = item._obj.__doc__
        self.tests.append(test)

    def pytest_collection_modifyitems(self, session, items, config):
        deselect_by_keyword(items, config)
        deselect_by_mark(items, config)

        for item in session.items:
            self.append_test(item)

        request_data = test_run_pb2.CreateTestRunRequest(
                tests_count=len(session.items),
                started_at=Timestamp(seconds=int(time.time())),
                uuid=self.test_run_uuid,
                plugin_type="pytest"
            )
        self.test_run_grpc_client.call_rpc_method("CreateTestRun", request_data)

        request_data = tests_pb2.CreateTestsRequest(tests=self.tests)
        self.tests_grpc_client.call_rpc_method("CreateTests", request_data)


    def pytest_runtest_logstart(self, nodeid):
        for item in self.tests:
            if item["nodeid"] == nodeid:
                self.test_uuid = item["uuid"]

        if self.test_uuid is not None:
            request_data = test_pb2.StartTestRequest(uuid=self.test_uuid, started_at=Timestamp(seconds=int(time.time())), status=test_pb2.TestStatus.RUNNING)
            if self.batching:
                self.start_records.append(request_data)
            else:
                self.test_grpc_client.call_rpc_method("StartTest", request_data)

    def started_finished_pairs(self):

        def find_something(uuid: str):
            _started_at = [req.started_at for req in self.pairs if req.uuid == uuid and hasattr(req, "started_at")][0]
            _stopped_at = [req.stopped_at for req in self.pairs if req.uuid == uuid and hasattr(req, "stopped_at")][0]
            _status = [req.status for req in self.pairs if req.uuid == uuid and hasattr(req, "stopped_at")][0]
            return _started_at, _stopped_at, _status

        request = None
        for item in self.pairs:
            started_at, stopped_at, status = find_something(item.uuid)
            request = test_pb2.ModifyTestRequest(uuid=item.uuid, started_at=started_at,
                                        stopped_at=stopped_at, status=status)
        yield request

    def create_pairs_for_batching(self, request):
        start_record = [record for record in self.start_records if record.uuid == self.test_uuid][0]
        if start_record:
            # send start and stop to self.pairs
            self.pairs.append(start_record)
            self.pairs.append(request)

            # clean start_records for previous start_record
            self.start_records = [record for record in self.start_records if record.uuid != self.test_uuid]

            self.cs_test_grpc_client.call_rpc_method("ModifyTest", self.started_finished_pairs())
            self.pairs = []

    def pytest_runtest_logreport(self, report):
        if self.test_uuid is not None:
            if report.when == "call" and report.outcome == "failed":
                if report.failed and not hasattr(report, "wasxfail"):
                    request = test_pb2.StopTestRequest(uuid=self.test_uuid, stopped_at=Timestamp(seconds=int(time.time())),
                                                   status=test_pb2.TestStatus.FAILED)
                    if not self.batching:
                        self.test_grpc_client.call_rpc_method("StopTest", request)
                    else:
                        self.create_pairs_for_batching(request)
            elif report.when == "setup" and report.outcome == "failed":
                if report.failed and not hasattr(report, "wasxfail"):
                    request = test_pb2.StopTestRequest(uuid=self.test_uuid, stopped_at=Timestamp(seconds=int(time.time())),
                                                   status=test_pb2.TestStatus.FAILED)
                    if not self.batching:
                        self.test_grpc_client.call_rpc_method("StopTest", request)
                    else:
                        self.create_pairs_for_batching(request)
            elif report.when == "call" and report.outcome == "passed":
                self.finished_tests.append(self.test_uuid)
                request = test_pb2.StopTestRequest(uuid=self.test_uuid, stopped_at=Timestamp(seconds=int(time.time())), status=test_pb2.TestStatus.PASSED)
                if not self.batching:
                    self.test_grpc_client.call_rpc_method("StopTest", request)
                else:
                    self.create_pairs_for_batching(request)

            elif (report.when == "call" and report.outcome == "skipped") or (report.when == "setup" and
                                                                             report.outcome == "skipped"):
                request = test_pb2.StopTestRequest(uuid=self.test_uuid, stopped_at=Timestamp(seconds=int(time.time())),
                                               status=test_pb2.TestStatus.SKIPPED)
                if not self.batching:
                    self.test_grpc_client.call_rpc_method("StopTest", request)
                else:
                    self.create_pairs_for_batching(request)
            elif report.when == "call" and report.outcome == "xfailed":
                request = test_pb2.StopTestRequest(uuid=self.test_uuid, stopped_at=Timestamp(seconds=int(time.time())),
                                               status=test_pb2.TestStatus.EXPECTED_FAILED)
                if not self.batching:
                    self.test_grpc_client.call_rpc_method("StopTest", request)
                else:
                    self.create_pairs_for_batching(request)
            elif report.when == "call" and report.outcome == "xpassed":
                request = test_pb2.StopTestRequest(uuid=self.test_uuid, stopped_at=Timestamp(seconds=int(time.time())),
                                               status=test_pb2.TestStatus.EXPECTED_PASSED)
                if not self.batching:
                    self.test_grpc_client.call_rpc_method("StopTest", request)
                else:
                    self.create_pairs_for_batching(request)

    def pytest_sessionfinish(self, session):
        # self.config.option.xmlpath
        request_data = test_run_pb2.StopTestRunRequest(uuid=self.test_run_uuid, stopped_at=Timestamp(seconds=int(time.time())))
        self.test_run_grpc_client.call_rpc_method("StopTestRun", request_data)


def pytest_addoption(parser):
    group = parser.getgroup("pytest-initry")
    group.addoption("--initry", default=False, dest="initry_mode", action="store_true",
                    help="Enable pytest-initry data collector")
    group.addoption("--initry-host", default=None, dest="initry_host", action="store", help="Initry host")
    group.addoption("--initry-grpc-port", default=None, dest="initry_grpc_port", action="store", help="Initry gRPC port")
    group.addoption("--initry-batching", default=True, dest="initry_batching", action="store", help="Batching mode")


def pytest_configure(config):
    initry = config.getoption("initry")
    if initry:
        plugin = PytestInitry(config)
        config._initry = plugin
        config.pluginmanager.register(plugin)


def pytest_unconfigure(config):
    plugin = getattr(config, "_initry", None)
    if plugin is not None:
        del config._initry
        config.pluginmanager.unregister(plugin)

