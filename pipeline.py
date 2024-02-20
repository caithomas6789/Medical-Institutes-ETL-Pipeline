from os import environ

from dotenv import load_dotenv
from boto3 import client

from extract import download_pubmed_input
from transform import load_xml_data
from load import upload_pubmed_output

if __name__ == "__main__":
    load_dotenv()

    s3 = client("s3",
                aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])

    download_pubmed_input(s3, "sigma-pharmazer-input")
    load_xml_data()
    upload_pubmed_output(s3, "sigma-pharmazer-output")
