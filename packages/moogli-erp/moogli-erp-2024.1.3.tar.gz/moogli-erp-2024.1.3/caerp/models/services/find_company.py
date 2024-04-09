from caerp_base.models.base import DBSESSION


class FindCompanyService:
    """
    Tools used to retrieve company informations like :

        employee logins

        find company from node
    """

    @classmethod
    def find_company_id_from_node(cls, node_instance):
        from caerp.models.company import Company

        if isinstance(node_instance, Company):
            return node_instance.id

        elif hasattr(node_instance, "company_id"):
            return node_instance.company_id

        elif hasattr(node_instance, "project_id"):
            from caerp.models.project import Project

            return (
                DBSESSION()
                .query(Project.company_id)
                .filter_by(id=node_instance.project_id)
                .scalar()
            )

    @classmethod
    def find_employees_login_from_node(cls, node_instance):
        from caerp.models.company import Company
        from caerp.models.user.user import User
        from caerp.models.user.login import Login

        cid = cls.find_company_id_from_node(node_instance)
        query = (
            DBSESSION()
            .query(Login.login)
            .join(Login.user)
            .join(User.companies)
            .filter(Company.id == cid)
        )
        return [u[0] for u in query]
