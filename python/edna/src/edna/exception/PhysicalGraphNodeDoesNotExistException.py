class PhysicalGraphNodeDoesNotExistException(Exception):
    """Exception raised if stream graph node does not exist.

    """
    def __init__(self, name: str = None, node_id: int = None):
        """Raise PhysicalGraphNodeDoesNotExistException
        """
        if name is not None:
            self.message = "Node with name {node_name} does not exist in PhysicalGraph".format(node_name=name)
        if id is not None:
            self.message = "Node with id {node_id} does not exist in PhysicalGraph".format(node_id=node_id)
        super().__init__(self.message)