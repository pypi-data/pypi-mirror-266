"""
    Json API views
    DEPRECATED 
"""


def json_model_view(request):
    """
    Return a json representation of a model
    """
    return request.context


def includeme(config):
    """
    Configure the views for this module
    """
    config.add_view(
        json_model_view,
        route_name="/companies/{id}",
        renderer="json",
        request_method="GET",
        permission="view_company",
    )

    for route_name in "project", "customer":
        config.add_view(
            json_model_view,
            route_name=route_name,
            renderer="json",
            request_method="GET",
            permission="view_%s" % route_name,
        )
