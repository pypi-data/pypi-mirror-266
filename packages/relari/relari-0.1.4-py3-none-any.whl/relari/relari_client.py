import json
import os
from typing import Optional, Dict
import urllib
import requests
from dotenv import load_dotenv

from relari.eval.manager import eval_manager

load_dotenv()


class RelariClient:
    def __init__(self, api_key: Optional[str] = None, url="https://api.relari.ai/v1/"):
        self._api_url = url
        if api_key is None:
            self.api_key = os.getenv("RELARI_API_KEY")
        else:
            self.api_key = api_key
        if self.api_key is None:
            raise ValueError(
                "Please set the environment variable RELARI_API_KEY or pass it as an argument."
            )

        self._headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
        self.timeout = 10
        self.valid = self._validate()


    def status(self):
        try:
            response = requests.get(
                urllib.parse.urljoin(self._api_url, "status"),
                headers=self._headers,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            exit("Request timed out while trying to validate API key")
        if response.status_code != 200:
            return False
        return True
        
    def _validate(self):
        try:
            response = requests.get(
                urllib.parse.urljoin(self._api_url, "auth/"),
                headers=self._headers,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            exit("Request timed out while trying to validate API key")
        if response.status_code != 200:
            return False
        return True

    def start_remote_evaluation(self, pipeline_version: str):
        if eval_manager.is_running():
            raise ValueError("Cannot save while evaluation is running")
        payload = {
            "dataset": eval_manager.dataset.data,
            "version": pipeline_version,
            "pipeline": eval_manager.pipeline.asdict(),
            "results": eval_manager.evaluation.results,
            "metadata": eval_manager.metadata,
        }
        try:
            response = requests.post(
                urllib.parse.urljoin(self._api_url, "eval"),
                headers=self._headers,
                data=json.dumps(payload),
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise Exception("Request timed out while trying to start remote evaluation")
        if response.status_code != 200:
            raise Exception("Failed to start remote evaluation: " + response.text)
        print("Evaluation task submitted successfully")

    def run_metric(self, metric_name: str, args, **kwargs):
        # Version 1: metric_name, dataset, and sample_id
        if "dataset" in kwargs and "sample_id" in kwargs:
            endpoint = urllib.parse.urljoin(self._api_url, "metrics/dataset/")
            payload = {
                "metric": metric_name,
                "dataset": kwargs["dataset"],
                "id": kwargs["sample_id"],
                "kwargs": args,
            }
        # Version 2: metric_name and args
        elif isinstance(args, Dict):
            endpoint = urllib.parse.urljoin(self._api_url, "metrics/")
            payload = {
                "metric": metric_name,
                "kwargs": args,
            }
        else:
            raise ValueError("Invalid arguments provided to run_metric.")
        try:
            response = requests.post(
                endpoint,
                headers=self._headers,
                data=json.dumps(payload),
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise Exception("Request timed out while trying to run metric")
        if response.status_code != 200:
            raise Exception("Failed to run metric: " + response.text)
        return response.json()
