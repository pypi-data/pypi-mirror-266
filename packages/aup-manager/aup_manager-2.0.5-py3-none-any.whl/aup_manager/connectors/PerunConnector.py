from typing import Union, List, Optional

from perun.connector import AdaptersManager
from perun.connector.adapters.AdaptersManager import AdaptersManagerNotExistsException

from aup_manager.connectors.ConnectorInterface import ConnectorInterface
from aup_manager.models import Entity, Admin


class PerunConnector(ConnectorInterface):
    def __init__(self, config):
        self.connector = AdaptersManager(config, attrs_map={})

    def get_admin(self, ext_login: str, ext_name: str = None) -> Optional[Admin]:
        """
        :param ext_login: user login
        :param ext_name: external source name
        :return: Admin object with perun user id and login
        """
        try:
            user = self.connector.get_perun_user(ext_name, [ext_login])
        except AdaptersManagerNotExistsException:
            return None
        return Admin(str(user.id), ext_login)

    def get_relevant_entity_id_types(
        self, entity_type_id: str, user_id: Union[str, int]
    ) -> List[str]:
        """
        :param entity_type_id: entity type with its id (facility:1)
        :param user_id: id of user
        :return: List of type:id of all entities related to given facility.
        Related entities are all resources and their VOs on facility, together with
        groups assigned to them which the user is a member of.
        (list also includes entity_type_id passed in parameter)
        """
        entity_type, entity_id = entity_type_id.split(":", 2)
        if entity_type != "facility":
            raise ValueError("Entity type has to be facility")
        result = {entity_type_id}

        resources = self.connector.get_resources_for_facility(int(entity_id), False)
        for resource in resources:
            if not self.connector.get_groups_for_resource(resource, False):
                result |= {f"resource:{resource.id}", f"vo:{resource.vo.id}"}
            else:
                groups = self.connector.get_groups_where_user_is_active_resource(
                    int(user_id), resource, False
                )
                if not groups:
                    continue
                result |= {f"resource:{resource.id}", f"vo:{resource.vo.id}"}
                for group in groups:
                    result.add(f"group:{group.id}")
                    for parent_group in self.connector.get_all_parent_groups_for_group(
                        group.id, False
                    ):
                        result.add(f"group:{parent_group.id}")

        return list(result)

    def get_entities_for_admin(
        self, admin_uid: Union[str, int] = None
    ) -> dict[str, List[Entity]]:
        """
        :param admin_uid: id of User
        :return: List of all entities to which given user has admin rights.
        """
        if isinstance(admin_uid, str):
            admin_uid = int(admin_uid)
        return {
            "resource": self._get_resources_from_perun_as_entities(admin_uid),
            "vo": self._get_vo_from_perun_as_entities(admin_uid),
            "facility": self._get_facilities_from_perun_as_entities(admin_uid),
            "group": self._get_groups_from_perun_as_entities(admin_uid),
        }

    def _get_resources_from_perun_as_entities(
        self, admin_uid: Union[str, int] = None
    ) -> List[Entity]:
        resources = self.connector.get_resources_where_user_is_admin(admin_uid)
        return [
            Entity(resource.id, resource.name, "resource") for resource in resources
        ]

    def _get_vo_from_perun_as_entities(
        self, admin_uid: Union[str, int] = None
    ) -> List[Entity]:
        vos = self.connector.get_vos_where_user_is_admin(admin_uid)
        return [Entity(vo.id, vo.name, "vo") for vo in vos]

    def _get_facilities_from_perun_as_entities(
        self, admin_uid: Union[str, int] = None
    ) -> List[Entity]:
        facilities = self.connector.get_facilities_where_user_is_admin(admin_uid)
        return [
            Entity(facility.id, facility.name, "facility") for facility in facilities
        ]

    def _get_groups_from_perun_as_entities(
        self, admin_uid: Union[str, int] = None
    ) -> List[Entity]:
        groups = self.connector.get_groups_where_user_is_admin(admin_uid)
        return [Entity(group.id, group.name, "group") for group in groups]

    def get_user_id(self, ext_login: str, ext_name: str = None) -> Union[int, str]:
        user = self.connector.get_perun_user(ext_name, [ext_login])
        return user.id
