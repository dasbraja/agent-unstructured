import boto3
import json
from textract import TextractDocumentAnalysis
from config import AWS_PROFILE_NAME, S3_URI, AWS_REGION_NAME
 
# Specify the AWS profile
profile_name = AWS_PROFILE_NAME
## specifiy the S3 URI
s3uri = S3_URI


def parse_s3_uri(s3uri):
    """Parses an S3 URI to extract the bucket name and the original file path."""
    parts = s3uri.split('/')
    bucket_name = parts[2]
    path_elements = parts[3:]
    return bucket_name, path_elements
 
def replace_file_extension(original_file_name, new_extension):
    """Replaces the file extension of the given filename with a new extension."""
    file_base = '.'.join(original_file_name.split('.')[:-1])
    new_file_name = f"{file_base}.{new_extension}"
    return new_file_name
 
def construct_object_key(path_elements, new_filename):
    """Constructs a new object key for S3 based on the original path elements and a new filename."""
    return '/'.join(path_elements[:-1] + [new_filename])
 
bucket_name, path_elements = parse_s3_uri(s3uri)
new_filename = replace_file_extension(path_elements[-1], 'json')
object_key = construct_object_key(path_elements, new_filename)
 
# Creating a session using a specific profile
s3 = boto3.client('s3')     
 
extractor = TextractDocumentAnalysis(region=AWS_REGION_NAME , source=s3uri)
extractor.analyze_document(features=["TABLES"])
response = extractor.get_response()
 
 
response_json = json.dumps(response, indent=2)
 
 
# Upload the JSON string to S3
s3.put_object(Bucket=bucket_name, Key=object_key, Body=response_json)