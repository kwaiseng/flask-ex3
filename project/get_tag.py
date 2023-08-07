
import boto3
import uuid 

import os

S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("S3_KEY")
S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")

s3_client = boto3.client('s3',aws_access_key_id=S3_KEY,aws_secret_access_key= S3_SECRET)

#s3 = s3_resource.Bucket(S3_BUCKET)

response = s3_client.get_object_tagging(
    Bucket=S3_BUCKET,
    Key='50c6a7c6-f595-11ea-9649-8c85903cac62.jpg',
)

print (response["TagSet"])
