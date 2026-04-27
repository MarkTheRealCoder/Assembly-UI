from source.platform import roundColors
from .CompoundMemoryChunk import CompoundMemoryChunk
from .SingleMemoryChunk import SingleMemoryChunk


class MemoryChunk:
    def __new__(cls, parent, key: str, value: str or int or None = 0x0, color_section: str = None):
        if value is None:
            return CompoundMemoryChunk(parent, key, roundColors(color_section))
        else:
            return SingleMemoryChunk(parent, key, value)