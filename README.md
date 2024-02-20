# Medical-Institutes-ETL-Pipeline
## Case study
PharmaZer is a pharmaceutical company that is currently focused on improving our understanding of Sjogren Syndrome, a disease that affects the glands responsible for producing tears and saliva. PharmaZer is interested in collating research papers from various research institutions to achieve this goal. By collecting and analysing these papers, PharmaZer aims to understand the disease comprehensively and develop new and effective treatments.

PharmaZer's approach of collecting and analysing research papers from various sources is a commonly used method in the pharmaceutical industry to advance our understanding of a particular disease or condition. By combining the findings from different research studies, PharmaZer can gain a complete picture of Sjogren Syndrome, including its causes, symptoms, and potential treatments. This approach of collating research papers and other relevant information is not limited to Sjogren Syndrome. In fact, this approach can be applied to many other diseases and conditions.

This information would then be used to develop new and innovative treatments that are safe and effective. By continuously expanding its focus to other diseases, PharmaZer could become a leading player in the pharmaceutical industry and help to bring new treatments to patients more quickly.

## Functionality
This project implements an ETL pipeline to find any relevant papers by loading data from an AWS S3 bucket, data transformation and matching in a cloud-based environment. AWS services, including S3 and ECS, facilitate the cloud-based infrastructure, ensuring scalability and reliability.

## Files

In this folder, you will find files required the run the pipeline.

- `README.md`
    - This is the file you are currently reading.
- `extract.py`
    - This file contains the extract script which extracts .xml files from an AWS S3 bucket.
    - This file should not be run independently. 
- `transform.py`
    - This file contains the transform script which transforms the data in the extracted .xml file.
    - This file should not be run independently. 
- `load.py`
    - This file contains the load script which loads a output .csv file to an AWS S3 bucket.
    - This file should not be run independently. 
- `pipeline.py`
    - This file contains the pipeline script which combines functions from the extract, transform and load scripts.
    - To run this script, use "python3 pipeline.py"
- `requirements.txt`
    - This file contains all the required modules to run the pipeline script.
    - This file can be run using "pip3 install -r requirements.txt"
- `Dockerfile`
    - This file contains all the instructions to create a docker image for this pipeline.
- `addresses.csv` & `institutes.csv`
    - These files contain all the relevant data to help with the data matching.

## Installation and Requirements
It is recommended before stating any installations that you make a new virtual environment. This can be done through commands in order:
- `python3 -m venv venv `
- `source ./venv/bin/activate`

Install all requirements for the pipeline using the command:
`pip3 install -r requirements.txt `

Create a .env file using the command:
`touch .env`

Required .env variable:
- AWS_ACCESS_KEY_ID = The access key for the AWS account you want to host this pipeline on.
- AWS_SECRET_ACCESS_KEY = The secret access key for the AWS account you want to host this pipeline on.