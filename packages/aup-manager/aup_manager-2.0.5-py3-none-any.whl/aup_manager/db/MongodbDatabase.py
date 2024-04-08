import json
from typing import Union, List, Optional

from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

from aup_manager.db.DatabaseInterface import DatabaseInterface
from aup_manager.models import Aup, Acceptance, Request, Status


class MongodbDatabase(DatabaseInterface):
    def __init__(self, config):
        self.client = MongoClient(config["uri"])
        self.db = self.client[config["db_name"]]
        try:
            self.db.create_collection("aup")
            self.db.create_collection("acceptance")
            self.db.create_collection("request")
        except CollectionInvalid:
            pass

    def insert_aup(self, aup: Aup) -> Union[str, int]:
        delattr(aup, "_id")
        delattr(aup, "acceptances")
        aup_dict = aup.__dict__
        result = self.db["aup"].insert_one(aup_dict)
        return result.inserted_id

    def insert_acceptance(self, acceptance: Acceptance) -> Union[str, int]:
        delattr(acceptance, "_id")
        result = self.db["acceptance"].insert_one(acceptance.__dict__)
        return result.inserted_id

    def insert_acceptances(
        self, acceptances: List[Acceptance]
    ) -> List[Union[str, int]]:
        insert_list = []
        for acceptance in acceptances:
            delattr(acceptance, "_id")
            acceptance.aup_id = ObjectId(acceptance.aup_id)
            insert_list.append(acceptance.__dict__)
        result = self.db["acceptance"].insert_many(insert_list)
        return result.inserted_ids

    def get_all_aups_with_acceptances(self) -> List[Aup]:
        aups = self.db["aup"].aggregate(
            [
                {
                    "$lookup": {
                        "from": "acceptance",
                        "localField": "_id",
                        "foreignField": "aup_id",
                        "as": "acceptances",
                    }
                }
            ]
        )
        return self.__aup_list_mongo_to_python(aups)

    def get_aup_with_acceptances_by_id(self, _id: Union[str, int]) -> Optional[Aup]:
        aup = self.db["aup"].aggregate(
            [
                {"$match": {"_id": ObjectId(_id)}},
                {
                    "$lookup": {
                        "from": "acceptance",
                        "localField": "_id",
                        "foreignField": "aup_id",
                        "as": "acceptances",
                    }
                },
            ]
        )
        aups = self.__aup_list_mongo_to_python(aup)
        if not aups:
            return None
        return aups[0]

    def get_all_aups(self) -> List[Aup]:
        aups = self.db["aup"].find()
        return self.__aup_list_mongo_to_python(aups)

    def get_aups_by_entitlement(self, entitlement: str) -> List[Aup]:
        aups = self.db["aup"].find({"entitlement": entitlement})
        return self.__aup_list_mongo_to_python(aups)

    def get_aup_by_id(self, _id: Union[str, int]) -> Optional[Aup]:
        aup_m = self.db["aup"].find_one({"_id": ObjectId(_id)})
        if not aup_m:
            return None
        return self.__aup_mongo_to_python(aup_m)

    def get_all_user_accepted_aups(self, user_id: Union[int, str]) -> List[Aup]:
        aups = self.db["aup"].aggregate(
            [
                {
                    "$lookup": {
                        "from": "acceptance",
                        "as": "acceptances",
                        "let": {"aup_id": "$_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$aup_id", "$$aup_id"]},
                                            {"$eq": ["$user_id", user_id]},
                                        ]
                                    }
                                }
                            }
                        ],
                    }
                },
                {"$match": {"acceptances.user_id": user_id}},
            ]
        )
        return self.__aup_list_mongo_to_python(aups)

    def get_aups_by_condition(self, condition: List[str]) -> List[Aup]:
        aups = self.db["aup"].find(
            {
                "conditions": {
                    "$elemMatch": {"$not": {"$elemMatch": {"$nin": condition}}}
                }
            }
        )
        return self.__aup_list_mongo_to_python(aups)

    def get_aups_by_condition_with_acceptances(self, condition: List[str]) -> List[Aup]:
        aups = self.db["aup"].aggregate(
            [
                {
                    "$match": {
                        "conditions": {
                            "$elemMatch": {"$not": {"$elemMatch": {"$nin": condition}}}
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "acceptance",
                        "localField": "_id",
                        "foreignField": "aup_id",
                        "as": "acceptances",
                    }
                },
            ]
        )
        return self.__aup_list_mongo_to_python(aups)

    def get_user_accepted_aups_by_condition(
        self, user_id: Union[int, str], condition: List[str]
    ) -> List[Aup]:
        aups = self.db["aup"].aggregate(
            [
                {
                    "$match": {
                        "conditions": {
                            "$elemMatch": {"$not": {"$elemMatch": {"$nin": condition}}}
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "acceptance",
                        "as": "acceptances",
                        "let": {"aup_id": "$_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$aup_id", "$$aup_id"]},
                                            {"$eq": ["$user_id", user_id]},
                                        ]
                                    }
                                }
                            }
                        ],
                    }
                },
                {"$match": {"acceptances.user_id": user_id}},
            ]
        )
        return self.__aup_list_mongo_to_python(aups)

    def get_user_not_accepted_aups_by_condition(
        self, user_id: Union[int, str], condition: List[str]
    ) -> List[Aup]:
        aups = self.db["aup"].aggregate(
            [
                {
                    "$match": {
                        "actual_aup_id": None,
                        "conditions": {
                            "$elemMatch": {"$not": {"$elemMatch": {"$nin": condition}}}
                        },
                    }
                },
                {
                    "$lookup": {
                        "from": "acceptance",
                        "as": "acceptances",
                        "let": {"aup_id": "$_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$aup_id", "$$aup_id"]},
                                            {"$eq": ["$user_id", user_id]},
                                        ]
                                    }
                                }
                            }
                        ],
                    }
                },
                {"$match": {"acceptances.user_id": {"$ne": user_id}}},
            ]
        )
        return self.__aup_list_mongo_to_python(aups)

    def delete_aup_by_id(self, aup_id: Union[int, str]):
        self.db["aup"].delete_one({"_id": ObjectId(aup_id)})
        self.db["acceptance"].delete_many({"aup_id": ObjectId(aup_id)})
        highest_aup = (
            self.db["aup"]
            .find({"actual_aup_id": ObjectId(aup_id)})
            .sort("version", -1)
            .limit(1)
        )
        highest_aup = list(highest_aup)
        if highest_aup:
            self.db["aup"].update_one(
                {"_id": highest_aup[0]["_id"]}, {"$set": {"actual_aup_id": None}}
            )
            self.db["aup"].update_many(
                {"actual_aup_id": ObjectId(aup_id)},
                {"$set": {"actual_aup_id": highest_aup[0]["_id"]}},
            )
            return highest_aup[0]["_id"]
        return None

    def delete_all_aups(self):
        self.db["aup"].delete_many({})

    def set_aup_name(self, aup_id: Union[str, int], new_name: str):
        self.db["aup"].update_one(
            {"_id": ObjectId(aup_id)}, {"$set": {"name": new_name}}
        )
        self.db["aup"].update_many(
            {"actual_aup_id": ObjectId(aup_id)}, {"$set": {"name": new_name}}
        )

    def update_aup_text(
        self, aup_id: Union[str, int], markdown: str, html: str
    ) -> Optional[Union[str, int]]:
        aup = self.get_aup_by_id(aup_id)
        if not aup:
            return None
        new_aup = Aup(
            aup.name,
            markdown,
            html,
            aup.conditions,
            aup.entitlement,
            version=aup.version + 1,
        )
        inserted_id = self.insert_aup(new_aup)
        if not inserted_id:
            return None
        self.db["aup"].update_one(
            {"_id": ObjectId(aup_id)}, {"$set": {"actual_aup_id": inserted_id}}
        )
        self.db["aup"].update_many(
            {"actual_aup_id": ObjectId(aup_id)},
            {"$set": {"actual_aup_id": inserted_id}},
        )
        return inserted_id

    def set_aup_conditions(self, aup_id: Union[str, int], conditions: List[List[str]]):
        self.db["aup"].update_one(
            {"_id": ObjectId(aup_id)}, {"$set": {"conditions": conditions}}
        )
        self.db["aup"].update_many(
            {"actual_aup_id": ObjectId(aup_id)}, {"$set": {"conditions": conditions}}
        )

    def save_request(self, request: Request) -> str:
        delattr(request, "_id")
        request.status = request.status.value
        result = self.db["request"].insert_one(request.__dict__)
        return result.inserted_id

    def get_request_by_id(self, request_id: Union[str, int]) -> Optional[Request]:
        return self.__get_request({"_id": ObjectId(request_id)})

    def get_request_by_nonce(self, nonce: str) -> Optional[Request]:
        return self.__get_request({"nonce": nonce})

    def __get_request(self, m_filter: json):
        request_m = self.db["request"].find_one(m_filter)
        if not request_m:
            return None
        return Request(
            request_m["nonce"],
            request_m["user_id"],
            request_m["_id"],
            Status(request_m["status"]),
        )

    def make_request_success(self, request_id: Union[str, int]):
        self.db["request"].update_one(
            {"_id": ObjectId(request_id)}, {"$set": {"status": Status.SUCCESS.value}}
        )

    def make_request_invalid(self, request_id: Union[str, int]):
        self.db["request"].update_one(
            {"_id": ObjectId(request_id)}, {"$set": {"status": Status.INVALID.value}}
        )

    @staticmethod
    def __aup_list_mongo_to_python(aup_list):
        return [MongodbDatabase.__aup_mongo_to_python(aup) for aup in aup_list]

    @staticmethod
    def __aup_mongo_to_python(aup_m):
        aup = Aup(**aup_m)
        aup.acceptances = [Acceptance(**ac) for ac in aup.acceptances]
        return aup
