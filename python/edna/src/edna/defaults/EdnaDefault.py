from __future__ import annotations
from abc import ABC

class EdnaDefault(ABC):
    BUFFER_MAX_SIZE : int = 32768
    BUFFER_MAX_TIMEOUT_S : float = 0.1
    BUFFER_NAME : str = "default"

    TASK_PRIMITIVE_HOST : str = "0.0.0.0"
    POLL_TIMEOUT : float = 0.1