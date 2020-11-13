from __future__ import annotations
from abc import ABC

class EdnaDefault(ABC):
    """Contains default parameters for edna

    Attributes:
        BUFFER_MAX_SIZE (int): The maximum size of a network buffer, set to 32768kB
        BUFFER_MAX_TIMEOUT_S (int): The maximum timeout of a network buffer, set to 100ms
        BUFFER_NAME (str): Default name of a network buffer, set to 'default'
        TASK_PRIMITIVE_HOST (str): The default host ip for a task primitive, set to localhost
        POLL_TIMEOUT_S (float): Default timeout for general polling, set to 100ms. Not used.
        TASK_POLL_TIMEOUT_S (float): Time to wait before polling tasks about status, set to 100ms. Not used.
    """
    BUFFER_MAX_SIZE : int = 32768
    BUFFER_MAX_TIMEOUT_S : float = 0.1
    BUFFER_NAME : str = "default"

    TASK_PRIMITIVE_HOST : str = "0.0.0.0"
    POLL_TIMEOUT_S : float = 0.1
    TASK_POLL_TIMEOUT_S: float = 0.1