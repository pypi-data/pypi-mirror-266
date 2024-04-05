from enum import Enum
from typing import Any, List, Optional


from relari.eval.dataset import Dataset, DatasetField
from relari.eval.pipeline import Pipeline
from relari.eval.result_types import TOOL_PREFIX, EvaluationResults


class LogMode(Enum):
    APPEND = 0
    REPLACE = 1


class EvaluationManager:
    def __init__(self):
        self._pipeline: Optional[Pipeline] = None
        self._eval_results: EvaluationResults = EvaluationResults()
        self._is_running: bool = False
        self._metadata = dict()

        self._idx = 0

    @property
    def samples(self) -> List[dict]:
        return self._eval_results.results

    @property
    def evaluation(self) -> EvaluationResults:
        return self._eval_results

    @property
    def metadata(self) -> dict:
        return self._metadata

    @property
    def pipeline(self) -> Pipeline:
        if self._pipeline is None:
            raise ValueError("Pipeline not set")
        return self._pipeline

    @property
    def dataset(self) -> Dataset:
        if self._pipeline is None:
            raise ValueError("Pipeline not set")
        if self._pipeline.dataset is None:
            raise ValueError("Dataset not set")
        return self._pipeline.dataset

    def set_pipeline(self, pipeline: Pipeline):
        self._pipeline = pipeline

    def set_metadata(self, metadata: dict):
        self._metadata = metadata

    def is_running(self) -> bool:
        return self._is_running

    def start_run(self, metadata: Optional[dict] = None):
        self._idx = 0
        self._is_running = True
        self._eval_results = EvaluationResults(self._pipeline)
        if metadata is not None:
            self.set_metadata(metadata)

    @property
    def curr_sample(self):
        if self._pipeline is None:
            raise ValueError("Pipeline not set")
        if self._idx >= len(self.dataset.data):
            self._is_running = False
            return None
        return self.dataset.data[self._idx]

    def next_sample(self):
        if self._pipeline is None:
            raise ValueError("Pipeline not set")
        if self._idx >= len(self.dataset.data):
            self._is_running = False
        else:
            self._idx += 1
        return self.curr_sample

    # Context manager
    def new_experiment(self, metadata: Optional[dict] = None):
        class ExperimentContext:
            def __init__(self, manager):
                self._manager = manager
                self._metadata = metadata

            def __enter__(self):
                # Initialize the session
                self._manager.start_run(self._metadata)
                return (
                    self  # Return the session object itself to be used as an iterator
                )

            def __exit__(self, exc_type, exc_val, exc_tb):
                # Clean up the session
                self._manager._is_running = False
                # Optional: Handle exceptions
                if exc_type:
                    print(f"An error occurred: {exc_val}")
                return False  # Propagate exceptions

            def __iter__(self):
                while (
                    self._manager.is_running() and self._manager.curr_sample is not None
                ):
                    yield self._manager.curr_sample
                    self._manager.next_sample()

        return ExperimentContext(self)

    # Logging results

    def log(
        self,
        module: str,
        value: Any,
        mode: LogMode = LogMode.REPLACE,
        **kwargs,
    ):
        # Make sure everything looks good
        if self._pipeline is None:
            raise ValueError("Pipeline not set")
        if not self._is_running:
            raise ValueError("Cannot log when not running")
        if module not in self._eval_results.results[self._idx]:
            raise ValueError(f"module {module} not found, review your pipeline")

        if kwargs and "tool_args" in kwargs:
            key = f"{TOOL_PREFIX}{module}"
            self._eval_results.results[self._idx][key].append(
                {"name": value, "kwargs": kwargs["tool_args"]}
            )
        else:
            if mode == LogMode.REPLACE:
                self._eval_results.results[self._idx][module] = value
            elif mode == LogMode.APPEND:
                if not isinstance(self._eval_results.results[self._idx][module], list):
                    if isinstance(value, list):
                        self._eval_results.results[self._idx][module].extend(value)
                    else:
                        self._eval_results.results[self._idx][module].append(value)
                else:
                    self._eval_results.results[self._idx][module].add(value)

eval_manager = EvaluationManager()
