import json

from source.model import StorageManager, AudioPlayer
from source.player_alexa import AlexaPlayer
from source.player_local import LocalPlayer
from source.storage_local import LocalStorage
from source.storage_s3 import S3Storage

json_string:str = """{
    "database": "postgres",
    "database_user": "postgres",
    "database_password": "chinois1",
    "database_host": "aws-postgres-1.cxq7vuc4ekiv.us-east-1.rds.amazonaws.com",
    "database_port": "5432",
    "language_speed": "slow",
    "source_language": "english",
    "target_language": "spanish",
    "target_dialect" : "mexico",
    "bucket_name": "clomeli-language-phrases",
    "root_name": "/Users/clomeli/tmp",
    "storage_type" : "s3",
    "player_type" : "local",
    "page_size" : 5
    
}"""


class Configuration:
    _instance = None

    def __init__(self):
        self.database = ""
        self.database_user: str = ""
        self.database_password: str = ""
        self.database_host: str = ""
        self.database_port: str = ""
        self.language_speed: str = "slow"
        self.source_language: str = "english"
        self.target_language: str = "spanish"
        self.target_dialect: str = "mexico"
        self.storage_type: str = "s3"
        self.player_type: str = "alexa"
        self.bucket_name: str = "/Users/clomeli/tmp"
        self.root_name = ""
        self.storage_type = ""
        self.player_type = ""

    @staticmethod
    def get_instance():
        if Configuration._instance is None:
            Configuration._instance = Configuration()
            Configuration._instance.set_configuration()
        return Configuration._instance

    def get_configuration(self, key, default):
        try:
            return getattr(self, key)
        except:
            return default

    def set_configuration(self):
        configs = json.loads(json_string)
        for key, value in configs.items():
            setattr(self, key, value)

    def get_file_manager(self) -> StorageManager:
        if self.storage_type == "local":
            return LocalStorage(self.root_name)
        else:
            return S3Storage(self.bucket_name)

    def get_player(self) -> AudioPlayer:
        if self.player_type == "local":
            return LocalPlayer()
        else:
            return AlexaPlayer()
