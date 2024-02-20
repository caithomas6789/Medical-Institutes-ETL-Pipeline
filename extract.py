"""Script which extracts all the .xml files required from an AWS S3 bucket"""
from boto3 import client


def get_object_keys(s3_client: client, bucket: str) -> list[str]:
    """Gets all the keys of all the objects in the bucket"""

    content = s3_client.list_objects(
        Bucket=bucket)["Contents"]

    return [o["Key"] for o in content]


def download_pubmed_input(s3_client: client, bucket: str):
    """Downloads all the relevant .xml files from the S3 bucket"""
    keys = get_object_keys(s3_client, bucket)

    for key in keys:
        if "c9-cai-input/" in key and ".xml" in key:
            s3_client.download_file(bucket, key, "./input.xml")
