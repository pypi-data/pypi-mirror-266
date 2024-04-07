"""Presidio analyzer package."""

import logging

from .pattern import Pattern
from .analysis_explanation import AnalysisExplanation
from .recognizer_result import RecognizerResult
from .dict_analyzer_result import DictAnalyzerResult
from .entity_recognizer import EntityRecognizer
from .local_recognizer import LocalRecognizer
from .pattern_recognizer import PatternRecognizer
from .remote_recognizer import RemoteRecognizer
from .recognizer_registry import RecognizerRegistry
from .analyzer_engine import AnalyzerEngine
from .batch_analyzer_engine import BatchAnalyzerEngine
from .analyzer_request import AnalyzerRequest
from .context_aware_enhancers import ContextAwareEnhancer
from .context_aware_enhancers import LemmaContextAwareEnhancer
from .analyzer_utils import PresidioAnalyzerUtils

# Define default loggers behavior

# 1.  logger

logging.getLogger("presidio-analyzer").addHandler(logging.NullHandler())

# 2. decision_process logger.
# Setting the decision process trace here as we would want it
# to be activated using a parameter to AnalyzeEngine and not by default.

decision_process_logger = logging.getLogger("decision_process")
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s]%(message)s")
ch.setFormatter(formatter)
decision_process_logger.addHandler(ch)
decision_process_logger.setLevel("INFO")
__all__ = [
    "Pattern",
    "AnalysisExplanation",
    "RecognizerResult",
    "DictAnalyzerResult",
    "EntityRecognizer",
    "LocalRecognizer",
    "PatternRecognizer",
    "RemoteRecognizer",
    "RecognizerRegistry",
    "AnalyzerEngine",
    "AnalyzerRequest",
    "ContextAwareEnhancer",
    "LemmaContextAwareEnhancer",
    "BatchAnalyzerEngine",
    "PresidioAnalyzerUtils",
]
