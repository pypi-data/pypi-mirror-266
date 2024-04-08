import abc
from typing import Union, List, Optional

from aup_manager.models import Aup, Acceptance, Request


class DatabaseInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "insert_aup")
            and callable(subclass.insert_aup)
            and hasattr(subclass, "insert_acceptance")
            and callable(subclass.insert_acceptance)
            and hasattr(subclass, "insert_acceptances")
            and callable(subclass.insert_acceptances)
            and hasattr(subclass, "get_all_aups_with_acceptances")
            and callable(subclass.get_all_aups_with_acceptances)
            and hasattr(subclass, "get_aup_with_acceptances_by_id")
            and callable(subclass.get_aup_with_acceptances_by_id)
            and hasattr(subclass, "get_all_aups")
            and callable(subclass.get_all_aups)
            and hasattr(subclass, "get_aups_by_entitlement")
            and callable(subclass.get_aups_by_entitlement)
            and hasattr(subclass, "get_aup_by_id")
            and callable(subclass.get_aup_by_id)
            and hasattr(subclass, "get_all_user_accepted_aups")
            and callable(subclass.get_all_user_accepted_aups)
            and hasattr(subclass, "get_aups_by_condition")
            and callable(subclass.get_aups_by_condition)
            and hasattr(subclass, "get_aups_by_condition_with_acceptances")
            and callable(subclass.get_aups_by_condition_with_acceptances)
            and hasattr(subclass, "get_user_accepted_aups_by_condition")
            and callable(subclass.get_user_accepted_aups_by_condition)
            and hasattr(subclass, "get_user_not_accepted_aups_by_condition")
            and callable(subclass.get_user_not_accepted_aups_by_condition)
            and hasattr(subclass, "delete_aup_by_id")
            and callable(subclass.delete_aup_by_id)
            and hasattr(subclass, "set_aup_name")
            and callable(subclass.set_aup_name)
            and hasattr(subclass, "update_aup_text")
            and callable(subclass.update_aup_text)
            and hasattr(subclass, "set_aup_conditions")
            and callable(subclass.set_aup_conditions)
            and hasattr(subclass, "save_request")
            and callable(subclass.save_request)
            and hasattr(subclass, "get_request_by_id")
            and callable(subclass.get_request_by_id)
            and hasattr(subclass, "get_request_by_nonce")
            and callable(subclass.get_request_by_nonce)
            and hasattr(subclass, "make_request_success")
            and callable(subclass.make_request_success)
            and hasattr(subclass, "make_request_invalid")
            and callable(subclass.make_request_invalid)
            or NotImplemented
        )

    @abc.abstractmethod
    def insert_aup(self, aup: Aup) -> Union[str, int]:
        """Insert given Aup to database"""
        raise NotImplementedError

    @abc.abstractmethod
    def insert_acceptance(self, acceptance: Acceptance) -> Union[str, int]:
        """Insert given Acceptance to database"""
        raise NotImplementedError

    @abc.abstractmethod
    def insert_acceptances(
        self, acceptances: List[Acceptance]
    ) -> List[Union[str, int]]:
        """Insert multiple Acceptances to database"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_aups_with_acceptances(self) -> List[Aup]:
        """Get all Aups with filled acceptance array"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_aup_with_acceptances_by_id(self, _id: Union[str, int]) -> Optional[Aup]:
        """Get Aup by id with filled acceptance array"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_aups(self) -> List[Aup]:
        """Get all Aups without acceptances"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_aups_by_entitlement(self, entitlement: str) -> List[Aup]:
        """Get all Aups by entitlement"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_aup_by_id(self, _id: Union[str, int]) -> Optional[Aup]:
        """Get Aup by id without acceptances"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_user_accepted_aups(self, user_id: Union[int, str]) -> List[Aup]:
        """
        Get all Aups accepted by given user,
        acceptances array contains only user acceptances
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_aups_by_condition(self, condition: List[str]) -> List[Aup]:
        """Get Aups which fulfill condition without acceptances"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_aups_by_condition_with_acceptances(self, condition: List[str]) -> List[Aup]:
        """Get Aups which fulfill condition with filled acceptance array"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_accepted_aups_by_condition(
        self, user_id: Union[int, str], condition: List[str]
    ) -> List[Aup]:
        """Get Aups which fulfill condition and are accepted by given user,
        acceptances array contains only user acceptances"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_not_accepted_aups_by_condition(
        self, user_id: Union[int, str], condition: List[str]
    ) -> List[Aup]:
        """
        Get Aups which fulfill condition and are not accepted by given user,
        acceptance array is empty
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_aup_by_id(self, aup_id: Union[int, str]):
        """Delete Aup by id from database, deletes all acceptances assigned to Aup"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_aup_name(self, aup_id: Union[str, int], new_name: str):
        """Set name to Aup and its previous versions"""
        raise NotImplementedError

    @abc.abstractmethod
    def update_aup_text(
        self, aup_id: Union[str, int], markdown: str, html: str
    ) -> Optional[Union[str, int]]:
        """
        Creates new version of Aup with new markdown and html texts,
        version is raised by 1
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_aup_conditions(self, aup_id: Union[str, int], conditions: List[str]):
        """Set conditions to Aup and its previous versions"""
        raise NotImplementedError

    @abc.abstractmethod
    def save_request(self, request: Request) -> str:
        """Save request to database"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_request_by_id(self, request_id: Union[str, int]) -> Optional[Request]:
        """Get request by id"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_request_by_nonce(self, nonce: str) -> Optional[Request]:
        """Get request by nonce"""
        raise NotImplementedError

    @abc.abstractmethod
    def make_request_success(self, request_id: Union[str, int]):
        """Update request result to success"""
        raise NotImplementedError

    @abc.abstractmethod
    def make_request_invalid(self, request_id: Union[str, int]):
        """Update request result to invalid"""
        raise NotImplementedError
