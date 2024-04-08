import abc
from typing import Union, List, Optional

from aup_manager.models import Admin, Entity


class ConnectorInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "get_admin")
            and callable(subclass.get_admin)
            and hasattr(subclass, "get_relevant_entity_id_types")
            and callable(subclass.get_relevant_entity_id_types)
            and hasattr(subclass, "get_entities_for_admin")
            and callable(subclass.get_entities_for_admin)
            and hasattr(subclass, "get_user_id")
            and callable(subclass.get_user_id)
            or NotImplementedError
        )

    @abc.abstractmethod
    def get_admin(self, ext_login: str, ext_name: str = None) -> Optional[Admin]:
        """Get User object from external source"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_relevant_entity_id_types(
        self, entity_type_id: str, user_id: Union[str, int]
    ) -> List[str]:
        """Get entity type_ids which are connected to given entity"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_entities_for_admin(
        self, admin_uid: Union[str, int] = None
    ) -> dict[str, List[Entity]]:
        """Get dict[type, List[Entity]] to which can admin assign Aups"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_id(self, ext_login: str, ext_name: str = None) -> Union[int, str]:
        """Get user id from external source"""
        raise NotImplementedError
