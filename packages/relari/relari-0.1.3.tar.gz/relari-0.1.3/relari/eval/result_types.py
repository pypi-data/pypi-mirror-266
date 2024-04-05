import json
from collections import ChainMap
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from relari.eval.modules import AgentModule
from relari.eval.pipeline import Pipeline
from relari.eval.utils import instantiate_type

TOOL_PREFIX = "_tool__"


class EvaluationResults:
    def __init__(self, pipeline: Optional[Pipeline] = None) -> None:
        if pipeline is None:
            self.results: List[Dict] = list()
        else:
            num_samples = len(pipeline.dataset.data)
            self.results: List[Dict] = [self._build_empty_samples(pipeline) for _ in range(num_samples)]

    def __len__(self):
        return len(self.results)

    def is_empty(self) -> bool:
        return not bool(self.results)

    def _build_empty_samples(self, pipeline: Pipeline):
        if pipeline is None:
            raise ValueError("Pipeline not set")
        empty_samples = dict()
        for module in pipeline.modules:
            empty_samples[module.name] = instantiate_type(module.output)
            if isinstance(module, AgentModule):
                empty_samples[f"{TOOL_PREFIX}{module.name}"] = list()
        return empty_samples

    def save(self, filepath: Path):
        assert filepath.suffix == ".jsonl", "File must be a JSONL file"
        assert self.results, "No samples to save"
        with open(filepath, "w") as f:
            for line in self.results:
                json_record = json.dumps(line, ensure_ascii=False)
                f.write(json_record + "\n")

    def load(self, filepath: Path):
        assert filepath.suffix == ".jsonl", "File must be a JSONL file"
        with open(filepath, "r") as f:
            self.results = [json.loads(line) for line in f]

