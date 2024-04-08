import boto3
import csv
import requests
import logging

logger = logging.getLogger()
logger.setLevel("INFO")


def nested_to_simple(nes_dict, exclude=None, new_dict=None, pref=""):
    if new_dict is None:
        new_dict = {}
    for key, val in nes_dict.items():
        if not isinstance(val, (dict, list)) and key not in exclude:
            new_dict[f'{pref}{key}'] = val
        elif isinstance(val, dict):
            pref = f"{key}_"
            nested_to_simple(val, new_dict=new_dict, pref=pref, exclude=exclude)
    return new_dict


def json_to_csv(file_api_dict, exclude_val, bucket_name, s3_folder):
    """
    This function converts any JSON format file to the CSV file.
    :param file_api_dict: A dict consisting the filenames (for csv files) as keys and api endpoints as the values.
    :param exclude_val: The list of values you want to exclude from the final data.
    :param bucket_name: The name of the s3 bucket in AWS.
    :param s3_folder: The folder name/ loc where you want to store the file in the bucket.
    :return: None. Creates the respective csv files and a log file at the defined location.
    """
    for filename, api_endpoint in file_api_dict.items():
        try:
            logger.info(f"Trying to request data from '{filename}' API Endpoint.")
            response = requests.get(api_endpoint)
            response.raise_for_status()
            users_data = response.json()
            logger.info(f"Successfully retrieved the data from '{filename}' API.")
            updated_data = []
            logger.info("Calling nested_to_simple function to restructre the data.")
            for u_data in users_data:
                simple_dict = nested_to_simple(u_data, exclude=exclude_val)
                updated_data.append(simple_dict)
            logger.info("Data restructred successfully.")
            logger.info(f"Begining to create '{filename}.csv' file")
            with open(f'/tmp/{filename}.csv', 'w', newline="", encoding='UTF-8') as data_file:
                csv_writer = csv.writer(data_file)
                count = 0
                for data in updated_data:
                    if count == 0:
                        header = data.keys()
                        csv_writer.writerow(header)
                        count += 1
                    csv_writer.writerow(data.values())
                logger.info(f"'{filename}.csv' created successfully.")
            s3_resource = boto3.resource('s3')
            logger.info(f"Uploading '{filename}.csv' to the Bucket.")
            s3_resource.Bucket(bucket_name).upload_file(f'/tmp/{filename}.csv',
                                                             Key=f'{s3_folder}/{filename}.csv')
            logger.info(f"Successfully Uploaded '{filename}.csv' to the Bucket.")
        except requests.exceptions.RequestException as ex:
            logger.error(f"{ex}")

