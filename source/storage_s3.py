import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

from source.model import StorageManager, FlashCard


class S3Storage(StorageManager):
    s3_client = boto3.client('s3')

    def __init__(self, bucket_name):
        super().__init__()
        self.s3_bucket = bucket_name
        if not self.bucket_exists(self.s3_bucket):
            self.create_bucket()

    def check_file_exists(self, flash_card: FlashCard, base_name: str) -> bool:
        file_name = os.path.join(flash_card.url, base_name)
        return self.check_exists(file_name=file_name)

    def check_exists(self, file_name: str):
        try:
            meta = self.s3_client.head_object(
                Bucket=self.s3_bucket,
                Key=file_name
            )
            return True
        except ClientError as e:
            return False

    def read_translation(self, flash_card: FlashCard) -> str:
        file_name = os.path.join(flash_card.url, self.flashcard_file)
        if not self.check_exists(file_name=file_name):
            return ""

        try:
            object_data = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=file_name
            )
            filedata = object_data['Body'].read()
            json_flash = filedata.decode('utf-8')
            flash_dict = json.loads(json_flash)
            id_value = flash_dict['id']
            source_phrase = flash_dict['source_phrase']
            dest_phrase = flash_dict['dest_phrase']
            if flash_card.id != id_value or flash_card.source_phrase != source_phrase:
                return ""
            flash_card.dest_phrase = dest_phrase
            return dest_phrase

        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(e)
            return ""

    def write_translation(self, flash_card: FlashCard) -> bool:
        try:
            data = flash_card.to_string()
            key = os.path.join(flash_card.url, self.flashcard_file)
            response = self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=data,
                ACL='public-read'
            )
            presigned: str = self.s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': self.s3_bucket,
                                                                'Key': flash_card.url},
                                                        ExpiresIn=3600)
            if presigned and len(presigned) > 0:
                return True

            return False

        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(e)
            return False
        except Exception as ex:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(ex)
            return False

    def get_audio_url(self, flash_card):
        key = os.path.join(flash_card.url, self.mp3_file)
        presigned: str = self.s3_client.generate_presigned_url('get_object',
                                                               Params={'Bucket': self.s3_bucket,
                                                                       'Key': key},
                                                               ExpiresIn=3600)
        if presigned and len(presigned) > 0:
            url = presigned
            if "?" in presigned:
                url = presigned.split("?")[0]
            return url.strip()

    def write_audio(self, flash_card: FlashCard, buffer: bytes) -> str:
        try:
            key = os.path.join(flash_card.url, self.mp3_file)
            response = self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=buffer,
                ACL='public-read'
            )

            presigned: str = self.s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': self.s3_bucket,
                                                                'Key': key},
                                                        ExpiresIn=3600)
            if presigned and len(presigned) > 0:
                url = presigned
                if "?" in presigned:
                    url = presigned.split("?")[0]
                return url.strip()

            return ""

        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(e)
            return False

    def read_audio(self) -> (dict, bool):
        try:
            object_data = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=self.flash_card.url
            )
            return object_data, True
        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(e)
            return None, False

    def bucket_exists(self, bucket):
        response = self.s3_client.list_buckets()
        return bucket in response['Buckets']

    def create_bucket(self, region=None):
        try:
            if region is None:
                s3_client = boto3.client('s3')
                s3_client.create_bucket(Bucket=self.s3_bucket)
            else:
                s3_client = boto3.client('s3', region_name=region)
                location = {'LocationConstraint': region}
                s3_client.create_bucket(Bucket=self.s3_bucket,
                                        CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return True
