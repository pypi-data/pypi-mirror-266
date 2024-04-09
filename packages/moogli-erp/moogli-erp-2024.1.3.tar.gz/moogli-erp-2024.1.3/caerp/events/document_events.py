class StatusChangedEvent:
    """
    Event fired when a document changes its status
    """

    def __init__(self, request, node, status, comment=None):
        self.request = request
        self.node = node
        self.comment = comment
        self.status = status
        self.node_type = node.type_

    def get_settings(self):
        return self.request.registry.settings
