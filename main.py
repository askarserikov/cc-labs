import boto3

# Initializing a client for interaction with s3. AWS credentials are automatically extracted from awscli
s3 = boto3.client('s3')

# Creating an s3 bucket
s3.create_bucket(
    ACL='public-read',
    Bucket='celtic-lab2',
    CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'}
)

# opening a file and uploading it to the bucket
data = open('/Users/askarserikov/Pictures/inu.jpg', 'rb')
s3.put_object(
    ACL='public-read',
    Bucket='celtic-lab2',
    Key='test.jpg',
    Body=data
)

# s3.Bucket('celtic-m7024elab1bucket1').put_object(Key='programmatically.jpg', Body=data)
