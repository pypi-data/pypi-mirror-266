from typing import Union, List, Optional

from pymongo import MongoClient

from aup_manager.connectors.ConnectorInterface import ConnectorInterface
from aup_manager.models import Admin, Entity


class MongodbConnector(ConnectorInterface):
    def __init__(self, config):
        self.client = MongoClient(config["uri"])
        self.db = self.client[config["db_name"]]
        self.admins_collection = config["admins_collection"]
        self.entities_collection = config["entities_collection"]

    def get_admin(self, ext_login: str, ext_name: str = None) -> Optional[Admin]:
        admin = self.db[self.admins_collection].find_one({"ext_login": ext_login})
        if not admin:
            return None
        return MongodbConnector.__admin_mongo_to_python(admin)

    def get_relevant_entity_id_types(
        self, entity_type_id: str, user_id: Union[str, int]
    ) -> List[str]:
        return [entity_type_id]

    def get_entities_for_admin(
        self, admin_uid: Union[str, int] = None
    ) -> dict[str, List[Entity]]:
        entities = self.db[self.entities_collection].find()
        result = {}
        for entity_m in entities:
            entity = MongodbConnector.__entity_mongo_to_python(entity_m)
            if not result.get(entity.get_entity_type()):
                result[entity.get_entity_type()] = [entity]
            else:
                result[entity.get_entity_type()].append(entity)
        return result

    def get_user_id(self, ext_login: str, ext_name: str = None) -> Union[int, str]:
        return ext_login

    @staticmethod
    def __admin_mongo_to_python(admin_m):
        return Admin(**admin_m)

    @staticmethod
    def __entity_mongo_to_python(entity_m):
        return Entity(entity_m["_id"], entity_m["name"], entity_m["type"])
