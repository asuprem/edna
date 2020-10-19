import enum

class IngestPattern(enum.Enum):
    """Enum to determine which type of ingest the StreamingContext has received. 
    This is set inside the Ingest primitive base class and can be modified by subclasses that
    themselves are primitives. 

    New Patterns might be added here in the future.
    """
    SERVER_SIDE_STREAM = 1
    CLIENT_SIDE_STREAM = 2