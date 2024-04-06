import json
import grpc

from datetime import datetime

from kilmlogger.services.scribe.grpc.scribelog_pb2_grpc import ScribeLogServiceStub
from kilmlogger.services.scribe.grpc.scribelog_pb2 import (
    ListOfEntryRequest,
    LogEntryRequest,
    LogEntry,
)

from kilmlogger.envs import envs


class ScribeBaseClient(object):
    def __init__(
        self,
        host: str | None = envs.SCRIBE_HOST,
        port: str | None = envs.SCRIBE_PORT,
        category: str | None = envs.DP_CATEGORY,
        app_name: str | None = envs.APP_NAME,
        app_prop: str | None = envs.ENVIRONMENT,
        dp_cate: str | None = envs.DP_CATEGORY,
        dp_log: str | None = envs.DP_LOG,
    ):
        self.host = host
        self.port = port
        self.category = category
        self.app_name = app_name
        self.app_prop = app_prop
        self.dp_cate = dp_cate
        self.dp_log = dp_log

    @staticmethod
    def build_grpc_stub(host: str, port: str) -> ScribeLogServiceStub:
        channel: grpc.Channel = grpc.insecure_channel(
            target=f"{host}:{port}",
            compression=grpc.Compression.Gzip,
        )
        return ScribeLogServiceStub(channel)

    @property
    def grpc_stub(self) -> ScribeLogServiceStub:
        if not hasattr(self, "_grpc_stub"):
            self._grpc_stub = self.build_grpc_stub(self.host, self.port)
        return self._grpc_stub

    def log(self, msg: dict) -> None:
        if msg.get("metric_only"):
            self.grpc_stub.sendMultiLog(
                self._build_request(
                    category=msg.get("category"),
                    json_param=self._build_dp_params(msg),
                    start_time=msg.get("start_time"),
                    command=msg.get("command"),
                    sub_command=msg.get("sub_command"),
                    result=msg.get("result"),
                ),
                timeout=envs.SCRIBE_TIMEOUT,
            )
        else:
            self.grpc_stub.sendMultiLogV2(
                self._build_request(
                    category=msg.get("category"),
                    json_param=self._build_dp_params(msg),
                    start_time=msg.get("start_time"),
                    dp_log=msg.get("dp_log"),
                    dp_cate=msg.get("dp_cate"),
                    command=msg.get("command"),
                    sub_command=msg.get("sub_command"),
                    result=msg.get("result"),
                ),
                timeout=envs.SCRIBE_TIMEOUT,
            )


class DefaultScribeClient(ScribeBaseClient):
    def _build_request(
        self,
        category: str | None = None,
        json_param: dict = {},
        start_time: int | None = None,
        dp_log: str | None = None,
        dp_cate: str | None = None,
        command: int | None = None,
        sub_command: int | None = None,
        result: int | None = None,
    ) -> ListOfEntryRequest:
        log_time = int(datetime.utcnow().timestamp() * 1000)
        execute_time: int | None = log_time - start_time if start_time else None
        return ListOfEntryRequest(
            logEntryRequest=[
                LogEntryRequest(
                    category=category or self.category,
                    app_name=self.app_name,
                    app_prop=self.app_prop,
                    timestamp=log_time,
                    log_entry=LogEntry(
                        json_param=json.dumps(json_param),
                        start_time=start_time,
                        dp_log=dp_log or self.dp_log,
                        dp_cate=dp_cate or self.dp_cate,
                        command=command,
                        sub_command=sub_command,
                        result=result,
                        execute_time=execute_time,
                    ),
                )
            ]
        )

    def _build_dp_params(self, msg: dict) -> dict:
        return {
            "log_time": msg["time"],
            "app_name": self.app_name,
            "app_mode": self.app_prop,
            "event_category": msg["level"],
            "correlation_id": msg["correlation_id"],
            "message": {
                "time": msg["time"],
                "content": msg["msg"],
            },
            "metrics": msg.get("metrics", {}),
            "extra_data": msg.get("extra_data", {}),
        }
