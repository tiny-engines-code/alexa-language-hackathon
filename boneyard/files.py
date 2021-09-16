import logging
import os

import boto3
from botocore.exceptions import ClientError

from source.model import AudioFile

s3_client = boto3.client('s3')
s3_bucket = "clomeli-language-audio"


class S3AudioCard:
    def create_audio_url(self):
        path = os.path.join(f"{self.source_lang}-{self.dest_lang}", self.verb, self.tense)
        object_name = f"{path}/{self.id}.mp3"
        metadata = {'language': self.dest_lang, 'phrase': self.dest_phrase}

    def get_audio_url(self):
        raise Exception("Cannot call abstract method")



class S3AudioFile(AudioFile):
    def create_audio_url(self):
        path = os.path.join(f"{self.source_lang}-{self.dest_lang}", self.verb, self.tense)
        object_name = f"{path}/{self.id}.mp3"
        metadata = {'language': self.dest_lang, 'phrase': self.dest_phrase}

    def get_audio_url(self):
        raise Exception("Cannot call abstract method")



class S3AudioLibrary(object):
    def __init__(self):
        pass

    def put_audio_file(self, audio_file: S3AudioFile, data) -> bool:
        try:
            response =  s3_client.put_object(
                Bucket=s3_bucket,
                Key=audio_file.object_name,
                Body=data,
                ACL='public-read',
                Metadata=audio_file.metadata
            )
            # todo: check response
            return True

        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(e)
            return False

    def head_audio_file(self, audio_file: AudioFile, data) -> dict:
        meta = s3_client.head_object(
            Bucket=s3_bucket,
            Key=audio_file.object_name
        )
        return meta

    def get_audio_file(self, audio_file: AudioFile) -> (dict,bool):
        try:
            object_data = s3_client.get_object(
                Bucket=s3_bucket,
                Key=audio_file.object_name
            )
            return object_data, True
        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(e)
            return None, False
