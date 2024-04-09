import math

MINIMUM_BACKOFF_PERIOD = 5
MAXIMUM_BACKOFF_INTERVAL = 10 * 60
FAILURES_BEFORE_DROPPING_BATCH = 8
FAILURES_BEFORE_DROPPING_QUEUE = 10


class FailureAwareBatchScheduler:
    def __init__(self, period: float):
        if period < 0:
            raise ValueError("period must be a non-negative number")

        self._period = period
        self._failures_since_successful_batch = 0

    def mark_success(self):
        self._failures_since_successful_batch = 0

    def mark_failure(self):
        self._failures_since_successful_batch += 1

    @property
    def next_interval(self) -> float:
        # Available, and first failure, just try the batch interval
        if self._failures_since_successful_batch <= 1:
            return self._period

        # Second failure, start ramping up the interval - first 2x, then 4x, ...
        backoff_factor = math.pow(2, self._failures_since_successful_batch - 1)

        # If the period is ridiculously short, give it a boost so we get some visible backoff.
        backoff_period = max(self._period, MINIMUM_BACKOFF_PERIOD)

        # The "ideal" interval
        backoff = backoff_period * backoff_factor

        capped_backoff = min(backoff, MAXIMUM_BACKOFF_INTERVAL)

        actual = max(capped_backoff, self._period)

        return actual

    @property
    def should_drop_batch(self) -> bool:
        return self._failures_since_successful_batch >= FAILURES_BEFORE_DROPPING_BATCH

    @property
    def should_drop_queue(self) -> bool:
        return self._failures_since_successful_batch >= FAILURES_BEFORE_DROPPING_QUEUE
