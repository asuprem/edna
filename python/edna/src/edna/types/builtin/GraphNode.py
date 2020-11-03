from __future__ import annotations

from edna.utils.NameUtils import NameUtils


class GraphNode:
    name: str
    node_id: int
    
    def __init__(self, node_id: int, name: str = None):
        self.node_id = node_id
        if name is None:
            self.name = NameUtils.createNameSuffix(suffix_length=10)
        else:
            self.name = name

    def setName(self, name: str):
        self.name = name

    def getName(self):
        return self.name

    def getNodeId(self):
        return self.node_id