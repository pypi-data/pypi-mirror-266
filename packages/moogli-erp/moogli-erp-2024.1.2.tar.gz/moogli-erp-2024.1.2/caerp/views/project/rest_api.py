from caerp.utils.compat import Iterable

import colanderalchemy
import colander

from caerp.forms.project import (
    APIProjectListSchema,
    APIBusinessListSchema,
    get_business_type_options,
    get_project_type_options,
    get_compute_modes,
)

from caerp.forms.jsonschema import convert_to_jsonschema

from caerp.models.project import Project, Phase
from caerp.models.third_party import Customer
from caerp.models.project.types import ProjectType, BusinessType

from caerp.views import (
    RestListMixinClass,
    BaseRestView,
)
from .controller import (
    ProjectAddEditController,
    ProjectTreeController,
)
from .routes import (
    PHASE_COLLECTION_API,
    API_COMPANY_PROJECTS,
    PROJECT_ITEM_API,
    PROJECT_TREE_API,
    PROJECT_TYPE_COMPANY_COLLECTION_API,
    PROJECT_TYPE_ITEM_API,
    BUSINESS_TYPE_COMPANY_COLLECTION_API,
    BUSINESS_TYPE_ITEM_API,
)


class ProjectTypeRestView(BaseRestView):
    """
    ProjectType s REST view, scoped to company

    .. http:get:: /api/v1/companies/(int:company_id)/project_types

        The project types of a given company allowed for the given user

    .. http:get:: /api/v1/project_types/(project_type_id)

        Return a more descriptive json representation of the project type
    """

    def collection_get(self):
        return [
            ptype
            for ptype in ProjectType.query_for_select()
            if ptype.allowed(self.request)
        ]

    def get(self):
        result = self.context.__json__(self.request)
        result["other_business_type_ids"] = self.context.get_other_business_type_ids()
        return result


class BusinessTypeRestView(RestListMixinClass, BaseRestView):
    """
    BusinessType s REST view, scoped to company

    .. http:get:: /api/v1/companies/(int:company_id)/business_types

        Returns the business types of a given company `company_id` allowed for the
        current authenticated user

        :query project_type_id: Filter by associated project type id

    .. http:get:: /api/v1/business_types/(int:business_types_id)

        Return a more descriptive json representation of the business type
    """

    list_schema = APIBusinessListSchema

    def query(self) -> Iterable[BusinessType]:
        return BusinessType.query()

    def filter_project_type_id(self, query, appstruct):
        ptype_id = appstruct.get("project_type_id")
        if ptype_id not in (colander.null, None):
            query = query.filter(
                BusinessType.other_project_types.any(ProjectType.id == ptype_id)
            )
        return query

    def collection_get(self):
        result = super().collection_get()
        return [btype for btype in result if btype.allowed(self.request)]


class ProjectRestView(RestListMixinClass, BaseRestView):
    """
    Projects REST view, scoped to company

    .. http:get:: /api/v1/companies/(int:company_id)/projects

        Returns the projects of a given company

        :query search: Filter the name of the project containing the search string
        :query customer_id: Filter projects attached to the given customer
        :query form_config: Return the options used to build new projects (available
        options for the given company, form schema ...)

    .. http:get::  /api/v1/projects/(int:project_id)

        Return the project with id project_id in json format

        :query related: List of related objects we want to be added to the response
    """

    list_schema = APIProjectListSchema

    def __init__(self, context, request=None):
        super().__init__(context, request)
        edit = False
        if isinstance(context, Project):
            edit = True
        self.controller = ProjectAddEditController(self.request, edit=edit)

    def get_schema(self, submitted: dict) -> colanderalchemy.SQLAlchemySchemaNode:
        return self.controller.get_schema(submitted)

    def query(self) -> Iterable[Project]:
        company = self.request.context
        main_query = Project.query()
        main_query = main_query.outerjoin(Project.customers)
        return main_query.filter(Project.company_id == company.id).distinct()

    def filter_archived(self, query, appstruct):
        include_archived = appstruct.get("archived", False)
        if not include_archived:
            query = query.filter(Project.archived == False)
        return query

    def filter_search(self, query, appstruct):
        search = appstruct["search"]
        if search:
            query = query.filter(
                Project.name.like("%" + search + "%"),
            )
        return query

    def filter_customer_id(self, query, appstruct):
        customer_id = appstruct.get("customer_id")
        if customer_id:
            query = query.filter(Project.customers.any(Customer.id == customer_id))
        return query

    def form_config(self) -> dict:
        """Collect informations necessary to build the project add form"""
        schema = self.controller.get_schema({})
        schema = schema.bind(request=self.request)
        schema = convert_to_jsonschema(schema)
        if isinstance(self.context, Project):
            company_id = self.context.company_id
        else:
            company_id = self.context.id
        return {
            "options": {
                "project_types": list(get_project_type_options(self.request)),
                "invoicing_modes": [
                    {"value": mode[0], "label": mode[1]}
                    for mode in get_compute_modes(self.request)
                ],
                "business_types": get_business_type_options(self.request),
                "company_id": company_id,
            },
            "schemas": {"default": schema},
        }

    def format_collection(self, query):
        return [self.controller.to_json(project) for project in query]

    def format_item_result(self, item):
        return self.controller.to_json(item)

    def post_format(self, entry, edit, attributes):
        """
        Associate a newly created element to the parent company
        """
        return self.controller.after_add_edit(entry, edit, attributes)


class ProjectTreeRestView(BaseRestView):
    """Rest entry point for getting the project tree management"""

    controller_class = ProjectTreeController

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.controller = self.controller_class(request, context)

    def collection_get(self):
        return self.controller.collection_get()

    def form_config(self):
        is_admin = self.request.has_permission("admin") or self.request.has_permission(
            "manage"
        )
        return {
            "options": {
                "is_admin": is_admin,
            },
        }


class PhaseRestView(BaseRestView):
    """
    Project Phase (subdir) REST view, scoped to project

    .. http:get:: /api/v1/projects/(project_id)/phases
        :noindex:

            Returns the phases of a given project



        :query int:  project_id (*required*) -- The id of the project
    """

    def collection_get(self):
        return Phase.query().filter_by(project=self.context).all()


def includeme(config):
    config.add_rest_service(
        factory=ProjectRestView,
        route_name=PROJECT_ITEM_API,
        collection_route_name=API_COMPANY_PROJECTS,
        view_rights="view_project",
        add_rights="add.project",
        edit_rights="edit.project",
        collection_view_rights="list_projects",
    )
    # Form config for customer add/edit
    for route, perm in (
        (PROJECT_TYPE_ITEM_API, "edit.project"),
        (API_COMPANY_PROJECTS, "add.project"),
    ):
        config.add_view(
            ProjectRestView,
            attr="form_config",
            route_name=route,
            renderer="json",
            request_param="form_config",
            permission=perm,
        )

    config.add_rest_service(
        factory=ProjectTypeRestView,
        route_name=PROJECT_TYPE_ITEM_API,
        collection_route_name=PROJECT_TYPE_COMPANY_COLLECTION_API,
        view_rights="view_project",
        collection_view_rights="list_projects",
    )
    config.add_rest_service(
        factory=BusinessTypeRestView,
        route_name=BUSINESS_TYPE_ITEM_API,
        collection_route_name=BUSINESS_TYPE_COMPANY_COLLECTION_API,
        view_rights="view_project",
        collection_view_rights="list_projects",
    )
    config.add_view(
        PhaseRestView,
        route_name=PHASE_COLLECTION_API,
        attr="collection_get",
        permission="view_project",
        renderer="json",
    )
    config.add_view(
        ProjectTreeRestView,
        route_name=PROJECT_TREE_API,
        attr="collection_get",
        permission="view_project",
        renderer="json",
    )
    config.add_view(
        ProjectTreeRestView,
        route_name=PROJECT_TREE_API,
        attr="form_config",
        permission="view_project",
        renderer="json",
        request_param="form_config",
    )
