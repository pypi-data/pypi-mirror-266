"""
Rest api for file management

.. http:get:: /api/v1/nodes/:node_id/files

    Returns a list of files attached to the given node

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        [
            {
                "id": 123,
                "label": "My file",
                "name": "My file",
                "size": 1024,
                "human_size": "1ko",
                "mimetype": "application/octet-stream",
                "description": "My file is very important",
                "created_at": "12/05/2023",
                "updated_at": "18/05/2023",
                "file_type_id": 12,
                "parent_id": 12,
            },
            ...
        ]

.. http:post:: /api/v1/nodes/:node_id/files

    Add a file to the given node (or switch it to another regarding the parameters)
    
        - In case an indicator_id is given we will try to attach the file to the given 
        indicator and to its node
        - In case a file_type_id is given we will try to find an indicator to attach the file 
        to (going also on upper levels)

    :form name: name of the file
    :form description: description of the file
    :form upload: File object
    :form file_type_id: the FileType's id
    :form indicator_id: Optional Indicator's id    

.. http:post:: /api/v1/files/

    Add a file

    :form parent_id: the parent's id
    :form name: name of the file
    :form description: description of the file
    :form upload: File object
    :form file_type_id: the FileType's id
    :form indicator_id: Optional Indicator's id
    

.. http:get:: /api/v1/files/:id

    Return a specific file

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "id": 123,
            "label": "My file",
            "name": "My file",
            "size": 1024,
            "human_size": "1ko",
            "mimetype": "application/octet-stream",
            "description": "My file is very important",
            "created_at": "12/05/2023",
            "updated_at": "18/05/2023",
            "file_type_id": 12,
            "parent_id": 12,
        }

.. http:put:: /api/v1/files/:id

    Allows to edit a specific file

    :form parent_id: the parent's id
    :form name: name of the file
    :form description: description of the file
    :form upload: File object
    :form file_type_id: the FileType's id
    :form indicator_id: Optional Indicator's id
"""
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from caerp.models.files import File
from caerp.models.node import Node
from caerp.forms.files import get_file_upload_schema
from caerp.utils.image import ImageResizer
from caerp.views import BaseRestView
from caerp.views.files.controller import FileController

from .routes import FILE_API, FILE_ITEM_API, NODE_FILE_API


class FileRestView(BaseRestView):
    """
    Base rest view for accessing files

    """

    def get_schema(self, submitted: dict):
        return get_file_upload_schema()

    def __init__(self, context, request=None):
        super().__init__(context, request)

    def query(self):
        return File.query()

    def _parent(self):
        """
        Returns the new file's parent
        """
        return self.context

    def _add_element(self, schema, attributes):
        self.controller = FileController(self.request, edit=False)
        instance = self.controller.save(attributes, self._parent())
        return instance

    def _edit_element(self, schema, attributes):
        self.controller = FileController(self.request, edit=True)
        instance = self.controller.save(attributes)
        return instance

    def delete(self):
        self.controller = FileController(self.request, edit=True)
        self.controller.delete()
        return {}

    def move_view(self):
        """Get the node id from the request json body, retrieve the Node instance and
        check if the user has permission to add a file to the node then move the file to this node
        """
        parent_id = self.request.json_body.get("parent_id")
        node = Node.get(parent_id)
        if node is None:
            return HTTPNotFound(
                {
                    "message": (
                        f"L'élément avec l'identifiant {parent_id} n'a pas pu"
                        " être retrouvé"
                    )
                }
            )

        if not self.request.has_permission("add.file", node):
            return HTTPForbidden(
                {
                    "message": (
                        "Vous n'êtes pas autorisé à ajouter un " "fichier à cet élément"
                    )
                }
            )

        self.controller = FileController(self.request, edit=True)
        self.controller.move({}, node)
        return self.context


class NodeFileRestView(FileRestView):
    """Common Rest entry point for all node parents"""

    def get_schema(self, submitted: dict):
        return get_file_upload_schema([ImageResizer(1200, 1200, "PDF")])

    def collection_get(self):
        return self.context.files


def includeme(config):
    config.add_view(
        FileRestView,
        request_method="POST",
        attr="post",
        route_name=FILE_API,
        permission="view",
        require_csrf=True,
        renderer="json",
    )
    config.add_rest_service(
        NodeFileRestView,
        route_name=FILE_ITEM_API,
        collection_route_name=NODE_FILE_API,
        collection_view_rights="list.files",
        add_rights="add.file",
        view_rights="view.file",
        edit_rights="edit.file",
        delete_rights="delete.file",
    )
    config.add_view(
        NodeFileRestView,
        attr="move_view",
        route_name=FILE_ITEM_API,
        permission="delete.file",
        require_csrf=True,
        request_method="PUT",
        request_param="action=move",
        context=File,
        renderer="json",
    )
