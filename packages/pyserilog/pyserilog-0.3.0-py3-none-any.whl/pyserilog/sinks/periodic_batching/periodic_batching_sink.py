import queue
import threading
import time
from _signal import signal
from abc import ABC, abstractmethod
import signal
from queue import Empty
from time import thread_time

from pyserilog import Guard
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.events.log_event import LogEvent
from pyserilog.sinks.periodic_batching.failure_aware_batch_scheduler import FailureAwareBatchScheduler
from pyserilog.sinks.periodic_batching.options import PeriodicBatchingSinkOptions


class IBatchedLogEventSink(ABC):

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    def emit_batch(self, events: list[LogEvent]) -> None:
        """
        Emit a batch of log events, running asynchronously.
        :param events: The batch of events to emit.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def on_empty_batch(self) -> None:
        """
        Allows sinks to perform periodic work without requiring additional threads
        or timers (thus avoiding additional flush/shut-down complexity).
        :return:
        """
        raise NotImplementedError


class PeriodicPatchingSink(ILogEventSink):

    def __init__(self, batched_sink: IBatchedLogEventSink, options: PeriodicBatchingSinkOptions):
        Guard.against_null(options)
        if options.batch_size_limit <= 0:
            raise ValueError("batch_size_limit must be a positive number")
        if options.period <= 0:
            raise ValueError("period must be a positive number")
        self._target_sink: IBatchedLogEventSink = Guard.against_null(batched_sink)
        self._batched_size_limit = options.batch_size_limit
        self._eagerly_emit_first_event = options.eagerly_emit_first_event

        self._batch_scheduler = FailureAwareBatchScheduler(options.period)

        if options.queue_limit is not None:
            self._queue = queue.Queue(options.queue_limit)
        else:
            self._queue = queue.Queue()

        self._current_batch = queue.Queue()
        self._is_shut_down = False
        signal.signal(signal.SIGINT, self.signal_shutdown_handler)
        signal.signal(signal.SIGTERM, self.signal_shutdown_handler)
        self._job = threading.Thread(target=self._run_background_job)
        self._job.start()

    def signal_shutdown_handler(self, sig, frame):
        self._is_shut_down = True
        self._job.join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._is_shut_down = True
        self._job.join()
        if hasattr(self._target_sink, "__exit__"):
            self._target_sink.__exit__(exc_type, exc_val, exc_tb)

    def emit(self, log_event: LogEvent):
        Guard.against_null(log_event)

        self._queue.put(log_event)

    def _run_background_job(self):
        is_eager_batch = self._eagerly_emit_first_event
        while not self._is_shut_down:
            self._fill_current_batch(is_eager_batch)

            try:
                if self._current_batch.empty():
                    self._target_sink.on_empty_batch()
                else:
                    is_eager_batch = False
                    self._target_sink.emit_batch(list(self._current_batch.queue))
                    self._current_batch.queue.clear()
                    self._batch_scheduler.mark_success()
            except Exception as ex:
                print(f"failed emitting a batch ex => {ex}")
                self._batch_scheduler.mark_failure()
                if self._batch_scheduler.should_drop_batch:
                    self._current_batch.queue.clear()
                    print("dropping the current batch")
                if self._batch_scheduler.should_drop_queue:
                    print("dropping the batch")
                    self._queue.queue.clear()

    def _fill_current_batch(self, is_eager_batch: bool):
        while not self._is_shut_down:
            while not self._is_shut_down and \
                    self._current_batch.qsize() < self._batched_size_limit and \
                    self._queue.qsize() > 0:
                try:
                    log_event = self._queue.get_nowait()
                    self._current_batch.put(log_event, block=False)
                except queue.Empty:
                    break

            if (self._current_batch.qsize() < self._batched_size_limit and not is_eager_batch) or \
                    self._current_batch.qsize() == 0 and not self._is_shut_down :
                try:
                    log_event = self._queue.get(block=True, timeout=self._batch_scheduler.next_interval)
                    if log_event:
                        self._current_batch.put(log_event)
                except Empty:
                    break
            else:
                break
