from .secnet_analyzer import AnalyzerEngine
from .secnet_analyzer.nlp_engine import TransformersNlpEngine
from .secnet_anonymizer import AnonymizerEngine, DeanonymizeEngine
from .secnet_anonymizer.entities import (
    RecognizerResult,
    OperatorResult,
    OperatorConfig,
)
from uuid import uuid4
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib


class SkyNET:
    def __init__(self, apikey: str) -> None:
        self.apikey = apikey
        self.encrypt_key = ""
        self.model_config = [{
            "lang_code": "en",
            "model_name": {
                "spacy": "en_core_web_sm",
                "transformers": "StanfordAIMI/stanford-deidentifier-base"
            }
        }]
        self.anonymizing_engine = AnonymizerEngine()
        self.nlp_engine = TransformersNlpEngine(models=self.model_config)
        self.analyzer = AnalyzerEngine(nlp_engine=self.nlp_engine)
        self.operator_config = {
            "person": OperatorConfig("encrpyt", {
                "key": self.apikey
            })
        }


        password = self.apikey.encode('utf-8')  # Encode the API key string to bytes using UTF-8 encoding

        # Salt for PBKDF2 (can be any random bytes)
        salt = str(hashlib.sha256(self.apikey.encode("utf-8"))).encode("utf-8")

        # Derive a key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Length of the derived key (in bytes) for AES-256
            salt=salt,
            iterations=100000,  # Adjust as needed for your security requirements
            backend=default_backend()
        )
        self.encrypt_key = kdf.derive(password)

    def wrap(self, content: str, encrypt: bool = False):
        """The function to wrap the text with appropriate excryption."""
        identification_results = self.analyzer.analyze(text=content, language=self.model_config[0]["lang_code"])
        anonymized_results = self.anonymizing_engine.anonymize(text=content, analyzer_results=identification_results)
        anonymized_results_items = anonymized_results.items

        if not encrypt:
            return anonymized_results.to_json()
        else:
            encryption_results = self.anonymizing_engine.anonymize(
                text=content,
                analyzer_results=identification_results,
                operators={
                    "DEFAULT": OperatorConfig("encrypt", {"key": self.encrypt_key})
                }
            )

            return encryption_results.to_json()
    
    def unwrap(self, content: str, encrypt: bool = False):
        """The function to unwrap the text from applicable encryption."""