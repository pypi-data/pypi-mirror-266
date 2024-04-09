"""
ThirdParty query service
"""
from sqlalchemy import func
from sqlalchemy.orm import load_only
from caerp.utils.strings import format_civilite


class ThirdPartyService:
    @classmethod
    def format_name(cls, instance):
        """
        Format the name of a third_party regarding the available datas
        :param obj instance: A ThirdParty instance
        :rtype: str
        """
        res = ""
        if instance.lastname:
            res = instance.lastname
            if instance.civilite:
                res = "{0} {1}".format(format_civilite(instance.civilite), res)

            if instance.firstname:
                res += " {0}".format(instance.firstname)
        return res

    @classmethod
    def get_label(cls, instance):
        """
        Return the label suitable for the given instance
        :param obj instance: A ThirdParty instance
        :returns: The label
        :rtype: str
        """
        if instance.type in ("company", "internal"):
            return instance.company_name
        else:
            return cls.format_name(instance)

    @classmethod
    def get_address(cls, instance):
        """
        Return the address suitable for the given instance
        :param obj instance: A ThirdParty instance
        :returns: The address
        :rtype: str
        """
        address = ""
        if instance.type in ("company", "internal"):
            address += "{0}\n".format(instance.company_name)
        name = cls.format_name(instance)
        if name:
            address += "{0}\n".format(name)
        if instance.address:
            address += "{0}\n".format(instance.address)
        if instance.additional_address:
            address += "{0}\n".format(instance.additional_address)

        address += "{0} {1}".format(instance.zip_code, instance.city)
        country = instance.country
        if country is not None and country.lower() != "france":
            address += "\n{0}".format(country)
        return address

    @classmethod
    def label_query(cls, third_party_class):
        """
        Return a query loading datas needed to compile ThirdParty label
        """
        query = third_party_class.query()
        query = query.options(
            load_only(
                "id",
                "label",
                "code",
                "company_id",
            )
        )
        return query

    @staticmethod
    def get_by_label(cls, label: str, company: "Company", case_sensitive: bool = False):
        """
        Even if case_sensitive == True, exact match is preferred.
        """
        query = cls.query().filter(
            cls.archived == False,  # noqa: E712
            cls.company == company,
        )
        exact_match = query.filter(cls.label == label).one_or_none()

        if exact_match or case_sensitive:
            return exact_match
        else:
            insensitive_match = query.filter(
                func.lower(cls.label) == func.lower(label)
            ).one_or_none()
            return insensitive_match

    @classmethod
    def get_third_party_account(cls, third_party_instance):
        raise NotImplementedError("get_third_party_account")

    @classmethod
    def get_general_account(cls, third_party_instance):
        raise NotImplementedError("get_general_account")
