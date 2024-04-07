# Description: This file contains the reporting contract and utilities for
# rendering reports

import json
import typing

from abc import ABC, abstractmethod
from detoxio.models import LLMScanResult
from google.protobuf.json_format import MessageToDict

class LLMScanReport(ABC):
    """
    LLMScanReport is an abstract base class that defines the contract for
    rendering reports from LLM scans.
    """
    @abstractmethod
    def render(self, results: LLMScanResult):
        """
        Render the report from the results.
        """
        raise NotImplementedError("Subclasses must implement this method")

class JSONLinesLLMScanReport(LLMScanReport):
    """
    JSONLinesLLMScanReport renders each prompt evaluation result as JSON lines.
    This reporting format is suitable for tool integrations, where the tool expects
    raw results for its own rendering and visualization.
    """

    def __init__(self, file: typing.TextIO = None):
        if file is None:
            raise ValueError("file is required for JSONLinesLLMScanReport")

        self.file = file

    def render(self, results: LLMScanResult):
        for result in results:
            self.file.write(json.dumps(MessageToDict(result, preserving_proto_field_name=True)) + "\n")

