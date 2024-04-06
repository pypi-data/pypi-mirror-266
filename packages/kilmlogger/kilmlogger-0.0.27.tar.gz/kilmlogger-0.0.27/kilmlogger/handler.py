import sys

from logging import Handler, LogRecord
from concurrent.futures import ThreadPoolExecutor

from kilmlogger.services.scribe.client import ScribeBaseClient, DefaultScribeClient
from kilmlogger.constants import ACCEPTED_LEVELS


executors = ThreadPoolExecutor(max_workers=50)


class GRPCEventStreamingHandler(Handler):
    def __init__(self, client: ScribeBaseClient = DefaultScribeClient(), accepted_levels: list[str] = ACCEPTED_LEVELS) -> None:
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        Handler.__init__(self)
        self._client = client
        self.accepted_levels = accepted_levels

    def emit(self, record: LogRecord) -> None:
        # NOTE: Only sent log to scribe and DP if the log level is in ACCEPTED_LEVELS
        if record.levelname not in self.accepted_levels:
            return

        try:
            executors.submit(self._client.log, msg=record.msg)
        except Exception:
            sys.stdout.write("--- Logging error ---\n")
