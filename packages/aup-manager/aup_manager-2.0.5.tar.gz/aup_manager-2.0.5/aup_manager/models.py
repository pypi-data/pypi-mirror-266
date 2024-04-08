import json
from copy import deepcopy
from enum import Enum


class Status(Enum):
    FAILURE = 0
    SUCCESS = 1
    INVALID = 2


class Aup:
    def __init__(
        self,
        name,
        markdown,
        html,
        conditions,
        entitlement,
        _id=None,
        actual_aup_id=None,
        additional_data=None,
        version=1,
        acceptances=None,
    ):
        if acceptances is None:
            acceptances = []
        self._id = str(_id)
        self.actual_aup_id = str(actual_aup_id) if actual_aup_id else None
        self.name = name
        self.markdown = markdown
        self.html = html
        self.version = version
        self.conditions = conditions
        self.entitlement = entitlement
        self.additional_data = additional_data
        self.acceptances = acceptances

    def add_acceptance(self, acceptance):
        self.acceptances.append(acceptance)

    def to_dict(self):
        temp = deepcopy(self)
        temp.acceptances = [ac.__dict__ for ac in temp.acceptances]
        return temp.__dict__

    def to_response_dict(self):
        temp = deepcopy(self)
        acceptances = []
        for ac in temp.acceptances:
            ac._id = ac.get_id()
            ac.aup_id = str(ac.aup_id)
            acceptances.append(ac)

        temp._id = temp.get_id()
        temp.actual_aup_id = temp.get_actual_aup_id()
        response_dict = temp.to_dict()
        response_dict.pop("markdown")
        return response_dict

    def get_id(self):
        return self._id

    def get_actual_aup_id(self):
        return self.actual_aup_id

    def __str__(self):
        return str(self.to_dict())


class Acceptance:
    def __init__(self, aup_id, user_id, date_time, _id=None):
        self._id = str(_id)
        self.aup_id = aup_id
        self.user_id = user_id
        self.date_time = date_time

    def get_id(self):
        return self._id


class Request:
    def __init__(self, nonce, user_id, _id=None, status=Status.FAILURE):
        self._id = str(_id)
        self.nonce = nonce
        self.user_id = user_id
        self.status = status

    def get_id(self) -> str:
        return self._id

    def __str__(self):
        return str(self.__dict__)


class Admin:
    def __init__(self, _id, ext_login):
        self._id = str(_id)
        self.ext_login = ext_login

    def get_id(self):
        return self._id

    def __str__(self):
        return str(self.__dict__)

    def to_json(self):
        return json.dumps({"_id": self._id, "ext_login": self.ext_login})


class Entity:
    def __init__(self, _id, name, entity_type):
        self.name = name

        """type:id"""
        self.type_id = f"{entity_type}:{str(_id)}"

    def get_id(self) -> str:
        return self.type_id.split(":", 1)[1]

    def get_entity_type(self) -> str:
        return self.type_id.split(":", 1)[0]

    def __str__(self):
        return str(self.__dict__)
