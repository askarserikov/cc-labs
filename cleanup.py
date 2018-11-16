import boto3

s3 = boto3.client('s3')

s3.delete_object(
    Bucket='celtic-lab2',
    Key='test.jpg'
)

s3.delete_bucket(
    Bucket='celtic-lab2'
)
