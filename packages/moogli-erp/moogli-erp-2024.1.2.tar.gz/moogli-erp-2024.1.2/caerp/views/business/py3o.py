"""
Business templates related views
"""
import logging
from pyramid.httpexceptions import HTTPFound
from genshi.template.eval import UndefinedError

from caerp.export.utils import write_file_to_request
from caerp.views.project.business import ProjectBusinessListView
from caerp.views.business.routes import BUSINESS_ITEM_PY3O_ROUTE
from caerp.views.business.controller import BusinessPy3oController
from caerp.views import (
    BaseView,
    TreeMixin,
)

logger = logging.getLogger(__name__)


def get_key_from_genshi_error(err):
    """
    Genshi raises an UndefinedError, but doesn't store the key name in the
    Exception object
    We get the missing key from the resulting message
    """
    msg = err.msg
    if " not defined" in msg:
        return msg.split(" not defined")[0]
    else:
        return msg


class BusinessFileGeneration(BaseView, TreeMixin):
    help_message = """
    Vous pouvez générer et télécharger des documents modèles définis
    par la coopérative qui seront pré-remplis avec vos coordonnées et
    celles du client."""

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.controller = BusinessPy3oController(context, request)

    @property
    def title(self):
        return "Génération de documents pour l'affaire {0}".format(self.context.name)

    @property
    def tree_url(self):
        return self.request.route_path(self.route_name, id=self.context.id)

    def default_context_task_id(self):
        """
        Return the last estimation as default context for template generation
        """
        last_estimation = self.context.estimations[-1]
        return last_estimation.id if last_estimation else None

    def py3o_action_view(self, business_type_id, file_type_id, context_task_id):
        model = self.context
        try:
            template, output_buffer = self.controller.compile_template(
                business_type_id,
                file_type_id,
                context_task_id or self.default_context_task_id(),
            )
            write_file_to_request(self.request, template.file.name, output_buffer)
            return self.request.response
        except UndefinedError as err:
            key = get_key_from_genshi_error(err)
            msg = """Erreur à la compilation du modèle la clé {0}
n'est pas définie""".format(
                key
            )
            logger.exception(msg)
            self.session.flash(msg, "error")
        except IOError:
            logger.exception("Le template n'existe pas sur le disque")
            self.session.flash(
                "Erreur à la compilation du modèle, le modèle de fichier "
                "est manquant sur disque. Merci de contacter votre "
                "administrateur.",
                "error",
            )
        except KeyError:
            logger.exception("Le modèle n'existe pas")
            self.session.flash("Erreur : ce modèle est manquant", "error")
        except Exception:
            logger.exception(
                "Une erreur est survenue à la compilation du template "
                "avec un contexte {} (id {})".format(
                    model.__class__.__name__,
                    model.id,
                )
            )
            self.session.flash(
                "Erreur à la compilation du modèle, merci de contacter "
                "votre administrateur",
                "error",
            )

        return HTTPFound(self.request.current_route_path(_query={}))

    def __call__(self):
        self.populate_navigation()
        business_type_id = self.context.business_type_id
        file_type_id = self.request.GET.get("file")
        context_task_id = self.request.GET.get("task")
        if file_type_id:
            return self.py3o_action_view(
                business_type_id, file_type_id, context_task_id
            )
        else:
            templates = self.controller.get_available_templates(business_type_id)
            return dict(
                title=self.title,
                help_message=self.help_message,
                templates=templates,
            )


def includeme(config):
    config.add_tree_view(
        BusinessFileGeneration,
        route_name=BUSINESS_ITEM_PY3O_ROUTE,
        parent=ProjectBusinessListView,
        permission="py3o.business",
        renderer="/business/py3o.mako",
        layout="business",
    )
