"""Script which loads all pubmed data into an AWS S3 bucket."""
from boto3 import client
import os


def upload_pubmed_output(s3_client: client, bucket: str):
    """Uploads the output .csv file into an AWS S3 bucket."""

    s3_client.upload_file("./output.csv", bucket,
                          "c9-cai-output/output.csv")

    os.remove("./input.xml")
    os.remove("./output.csv")
