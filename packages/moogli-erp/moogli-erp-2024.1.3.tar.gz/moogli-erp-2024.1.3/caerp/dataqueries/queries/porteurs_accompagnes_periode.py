from caerp.models.activity import Attendance, Event
from caerp.models.user import User
from caerp.models.user.userdatas import STATUS_OPTIONS
from caerp.models.user.utils import (
    get_userdatas_entry_date,
    get_userdatas_exit,
    get_user_analytical_accounts,
    get_tuple_option_label,
    get_social_statuses_label,
    get_active_custom_fields,
    get_active_custom_fields_labels,
    get_custom_field_value_string,
)
from caerp.dataqueries.base import BaseDataQuery
from caerp.utils.dataqueries import dataquery_class


@dataquery_class()
class SupportedESQuery(BaseDataQuery):
    name = "porteurs_accompagnes_periode"
    label = "Détail des porteurs accompagnés sur une période"
    description = """
    <p>Liste de tous les porteurs de projets accompagnés sur la période choisie avec un 
    maximum d'informations.</p>
    <br/>
    <p>Un porteur de projet est considéré comme accompagné s'il a eu un rendez-vous 
    d'accompagnement ou a participé à un atelier (en étant présent) sur la période.'</p>
    """

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        headers = [
            "Identifiant de MooGLi",
            "Identifiant interne",
            "Code(s) analytique(s)",
            "Civilité",
            "Nom",
            "Nom de naissance",
            "Prénom",
            "Situation actuelle dans la CAE",
            "Antenne de rattachement",
            "Accompagnateur",
            "Date d'entrée dans la CAE",
            "Date d'entrée au sociétariat",
            "Date info coll",
            "Prescripteur",
            "Nom du prescripteur",
            "Motif de non admission en CAE",
            "",
            "E-mail 1",
            "E-mail 2",
            "Tél. fixe",
            "Tél. mobile",
            "Adresse",
            "Code postal",
            "Ville",
            "Zone d'habitation",
            "Qualification de la zone d'habitation",
            "Sexe",
            "Date de naissance",
            "Age",
            "Lieu de naissance",
            "Code postal du lieu de naissance",
            "Nationalité",
            "Fin de validité de la carte de séjour",
            "",
            "Numéro de sécurité sociale",
            "Situation familiale",
            "Nombre d'enfants",
            "Niveau d'études",
            "Contact urgent : Nom",
            "Contact urgent : Téléphone",
            "Statut social à l'entrée",
            "Statut social actuel",
            "Date de fin de droit",
            "Allocation adulte handicapé - échéance",
            "Objectifs",
            "Date de la visite médicale",
            "Date limite de la visite médicale",
            "Résultat de la visite médicale",
            "",
        ]
        for custom_field_label in get_active_custom_fields_labels():
            headers.append(custom_field_label)
        headers += [
            "",
            "Date de sortie",
            "Type de sortie",
            "Motif de sortie",
            "",
            "Créé(e) le",
            "Mis(e) à jour le",
        ]
        return headers

    def data(self):
        data = []

        supported_users = (
            User.query()
            .join(Attendance)
            .join(Event)
            .where(Event.datetime.between(self.start_date, self.end_date))
            .where(Attendance.status == "attended")
            .distinct()
            .order_by(User.lastname, User.firstname)
        )
        for user in supported_users:
            if user.login.primary_group() != "contractor" and not user.has_userdatas():
                continue
            if not user.has_userdatas():
                data.append(
                    [
                        user.id,
                        "",
                        get_user_analytical_accounts(user.id),
                        user.civilite,
                        user.lastname,
                        user.firstname,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        user.email,
                    ]
                )
            else:
                u = user.userdatas
                user_data = [
                    u.user_id,
                    u.coordonnees_identifiant_interne,
                    get_user_analytical_accounts(u.user_id),
                    u.coordonnees_civilite,
                    u.coordonnees_lastname,
                    u.coordonnees_ladies_lastname,
                    u.coordonnees_firstname,
                    u.situation_situation.label if u.situation_situation else "",
                    u.situation_antenne.label if u.situation_antenne else "",
                    u.situation_follower.label if u.situation_follower else "",
                    self.date_tools.format_date(get_userdatas_entry_date(u.id)),
                    self.date_tools.format_date(u.situation_societariat_entrance),
                    self.date_tools.format_date(u.parcours_date_info_coll),
                    u.parcours_prescripteur.label if u.parcours_prescripteur else "",
                    u.parcours_prescripteur_name,
                    u.parcours_non_admission.label if u.parcours_non_admission else "",
                    "",
                    u.coordonnees_email1,
                    u.coordonnees_email2,
                    u.coordonnees_tel,
                    u.coordonnees_mobile,
                    u.coordonnees_address,
                    u.coordonnees_zipcode,
                    u.coordonnees_city,
                    u.coordonnees_zone.label if u.coordonnees_zone else "",
                    u.coordonnees_zone_qual.label if u.coordonnees_zone_qual else "",
                    u.coordonnees_sex,
                    self.date_tools.format_date(u.coordonnees_birthday),
                    self.date_tools.age(u.coordonnees_birthday),
                    u.coordonnees_birthplace,
                    u.coordonnees_birthplace_zipcode,
                    u.coordonnees_nationality,
                    self.date_tools.format_date(u.coordonnees_resident),
                    "",
                    u.coordonnees_secu,
                    get_tuple_option_label(STATUS_OPTIONS, u.coordonnees_family_status),
                    u.coordonnees_children,
                    u.coordonnees_study_level.label
                    if u.coordonnees_study_level
                    else "",
                    u.coordonnees_emergency_name,
                    u.coordonnees_emergency_phone,
                    get_social_statuses_label(u.social_statuses),
                    get_social_statuses_label(u.today_social_statuses),
                    self.date_tools.format_date(u.statut_end_rights_date),
                    self.date_tools.format_date(
                        u.statut_handicap_allocation_expiration
                    ),
                    u.parcours_goals,
                    self.date_tools.format_date(u.parcours_medical_visit),
                    self.date_tools.format_date(u.parcours_medical_visit_limit),
                    u.parcours_status.label if u.parcours_status else "",
                    "",
                ]
                # Champs complémentaires
                for field in get_active_custom_fields():
                    user_data.append(get_custom_field_value_string(u, field))
                # Sortie
                exit = get_userdatas_exit(u.id)
                if exit:
                    user_data += [
                        "",
                        self.date_tools.format_date(exit.start_date),
                        exit.type_sortie.label if exit.type_sortie else "",
                        exit.motif_sortie.label if exit.motif_sortie else "",
                    ]
                else:
                    user_data += [
                        "",
                        "",
                        "",
                        "",
                    ]
                # Création / modification
                user_data += [
                    "",
                    self.date_tools.format_date(u.created_at),
                    self.date_tools.format_date(u.updated_at),
                ]
                data.append(user_data)

        return data
