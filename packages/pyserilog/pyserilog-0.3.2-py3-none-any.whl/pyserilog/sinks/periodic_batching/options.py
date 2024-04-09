from typing import Optional


class PeriodicBatchingSinkOptions:
    def __init__(self, eagerly_emit_first_event: bool = True,
                 batch_size_limit: int = 1000,
                 period: float = 2,
                 queue_limit: Optional[int] = 100000):
        self.eagerly_emit_first_event: bool = eagerly_emit_first_event
        """
        Eagerly emit a batch containing the first received event, regardless of the target batch size or batching time.
         This helps with perceived "liveness" when running/debugging applications interactively. The default is `True`.
        """

        self.batch_size_limit: int = batch_size_limit
        """
        The maximum number of events to include in a single batch. The default is `1000`.
        """

        self.period: float = period
        """
        The maximum buffering delay between event batches. The default is `two` seconds.
        """

        self.queue_limit: Optional[int] = queue_limit
        """
        Maximum number of events to hold in the sink's internal queue, or `null` for an unbounded queue. The default is `100000`.
        """
