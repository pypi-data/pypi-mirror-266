from pymongo.errors import ConnectionFailure
from pymongo import MongoClient, DESCENDING, ASCENDING
from cgc.sdk.handlers import exception_handler


class MongoConnector:
    """
    :param database_name: Database name
    :type database_name: str
    :param hosts: Host address defined as IP or DNS Name with port ex. db.example.com:27017
    :type hosts: list
    :param username: Username used for connection, not required, defaults to None
    :type username: str | None
    :param password: Password for Username, used with Username, defaults to None
    :type password: str | None
    :param authsource: Database to authenticate user with, defaults to admin
    :type authsource: str
    """

    def __init__(
        self,
        database_name: str,
        hosts: str,
        username: str = None,
        password: str = None,
        authsource: str = "admin",
        replica_set: str = None,
    ) -> None:
        self._database_name = database_name
        self._hosts = hosts
        assert type(hosts) is str
        'hosts must be a str of host addresses ex. "db.example.com:27017,db2.example.com:27017"'
        self._username = username
        self._password = password
        self._authsource = authsource
        _extra_args = []
        if replica_set:
            _extra_args.append(f"replicaSet={replica_set}")
        if authsource:
            _extra_args.append(f"authSource={authsource}")
        _extra_args.append("readPreference=primaryPreferred")
        _extra_args.append("ssl=false")
        self._extra_args = "&".join(_extra_args)
        print(self._extra_args)
        self.connect()

    def disconnect(self):
        print(f"Disconnecting from MongoDB: {self._hosts}")
        self._mongo_client.close()
        print(f"Disconnected from MongoDB")

    def connect(self):
        _credentials = (
            ":".join([self._username, self._password]) if self._username else ""
        )
        _host_connection_string = (
            "@".join([_credentials, self._hosts]) if _credentials else self._hosts
        )
        while True:
            try:
                self._mongo_client = MongoClient(
                    "mongodb://{}/{}?{}".format(
                        _host_connection_string, self._database_name, self._extra_args
                    )
                )
                self._mongo_client_server_info = self._mongo_client.server_info()
                print(f"Connected to MongoDB ({self._database_name}): {self._hosts}")
                self._db = self._mongo_client[self._database_name]
                break
            except (ConnectionFailure,) as e:
                print(f"MongoDB connection error: {e}")
                print(f"retrying to connect...")

    def _select_collection(self, collection_name: str):
        return self._db[collection_name]

    def get_pymongo_client(self):
        return self._mongo_client

    @staticmethod
    def _ascending():
        return ASCENDING

    @staticmethod
    def _descending():
        return DESCENDING

    @exception_handler
    def find(self, collection_name: str, query: dict, session=None):
        collection = self._select_collection(collection_name)
        return collection.find(query, session=session)

    @exception_handler
    def find_one(self, collection_name: str, query: dict, session=None):
        collection = self._select_collection(collection_name)
        return collection.find_one(query, session=session)

    @exception_handler
    def insert_one(self, collection_name: str, query: dict, session=None):
        collection = self._select_collection(collection_name)
        return collection.insert_one(query, session=session)

    @exception_handler
    def delete_one(self, collection_name: str, query: dict, session=None):
        collection = self._select_collection(collection_name)
        return collection.delete_one(query, session=session)

    @exception_handler
    def aggregate(self, collection_name: str, pipeline, session=None):
        collection = self._select_collection(collection_name)
        return collection.aggregate(pipeline=pipeline, session=session)

    @exception_handler
    def count_documents(self, collection_name: str, query: dict, session=None):
        collection = self._select_collection(collection_name)
        return collection.count_documents(query, session=session)

    @exception_handler
    def update_one(
        self,
        collection_name: str,
        query: dict,
        update: dict,
        upsert: bool = False,
        session=None,
    ):
        collection = self._select_collection(collection_name)
        return collection.update_one(query, update, upsert=upsert, session=session)

    @exception_handler
    def watch(
        self,
        collection_name: str,
        operation_before_watch,
        operation_on_event,
        first_operation_kwargs={},
        second_operation_kwargs={},
    ):
        """Function to watch for changes in a collection. Preferred to run over threading as daemon.

        :param collection_name: Name of the collection to watch
        :type collection_name: str
        :param operation_on_event: Function to run on event
        :type operation_on_event: function
        """
        operation_before_watch(**first_operation_kwargs)
        while True:
            print("Creating new watch cursor")
            watch_cursor = self._select_collection(
                collection_name=collection_name
            ).watch()
            print("Watching: {}.{}\n".format(self._database_name, collection_name))
            for d in watch_cursor:
                if d["operationType"] == "invalidate":
                    print(
                        "Watch cursor invalidated (deleted collection: {}?)".format(
                            collection_name
                        )
                    )
                    print("Closing watch cursor")
                    watch_cursor.close()
                    break
                else:
                    operation_on_event(d, **second_operation_kwargs)
                    watch_cursor.close()
                    return d
            else:
                continue
            break

    @staticmethod
    def example_operation_for_watch(d):
        print(d)
        # del d["fullDocument"]["_id"]
        # print("local time   : {}".format(datetime.utcnow()))
        # print("cluster time : {}".format(d["clusterTime"].as_datetime()))
        # print("collection   : {}.{}".format(d["ns"]["db"], d["ns"]["coll"]))
        # try:
        #     print("doc          : {}".format(d["fullDocument"]))
        # except KeyError:
        #     pass


def get_mongo_access(
    app_name: str, password: str, database: str = "db", restart: bool = False
):
    global _mongo_access

    def init_access():
        global _mongo_access
        _mongo_access = MongoConnector(
            database_name=database,
            hosts=f"{app_name}:27017",
            username="admin",
            password=password,
        )

    try:
        if not isinstance(_mongo_access, MongoConnector) or restart:
            init_access()
    except NameError:
        init_access()
        pass
    return _mongo_access
