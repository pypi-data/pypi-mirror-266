import os as _os
from typing_extensions import override

# Assuming that _globals.py defines these constants:
from ._globals import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES, BASE_URL
from .errors import (
    BRAHMAIError,
    APIKeyError
)
from . import chat, embeddings
from .chat import Chat
from .skynet import SkyNET
from .moderations import Moderations
from .ZeroShot.text import ZeroShotClassifier as ZSTC

# Initialize variables with None or default values
class BRAHMAI:
    apikey: str
    api_version: str
    timeout: int
    chat: Chat
    zeroshot_text: ZSTC
    moderations: Moderations
    skynet: SkyNET
    def __init__(
        self,
        *,
        apikey: str | None = None,
        api_version: str | None = None,
        organization: str | None = None,
        base_url: str | None = BASE_URL,
        timeout: int | None = DEFAULT_TIMEOUT
    ) -> None:
        if apikey == None:
            apikey = _os.environ.get("BRAHMAI_API_KEY")
        if apikey == None:
            raise BRAHMAIError(
                "The apikey option must be set either by passing apikey to the client or by setting the BRAHMAI_API_KEY environment variable"
            )
        
        self.apikey = apikey
        self.api_version = api_version
        self.organization = organization
        self.timeout = timeout
        self.chat = Chat(apikey, api_version, timeout)
        self.zeroshot_text = ZSTC(apikey, api_version, timeout)
        self.skynet = SkyNET(apikey)
        self.moderations = Moderations(apikey, api_version, timeout)

