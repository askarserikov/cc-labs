import boto3
import os

regions = ['eu-central-1', 'us-west-1', 'ap-northeast-1']

for i in range(0, len(regions)):
    s3 = boto3.client('s3', region_name=regions[i])
    try:
        s3.delete_object(
            Bucket='celtic-lab2-{}'.format(regions[i]),
            Key='test.jpg'
        )
        s3.delete_bucket(
            Bucket='celtic-lab2-{}'.format(regions[i])
        )
        os.remove('tmp-{}.jpg'.format(regions[i]))
    except Exception as e:
        pass
print('Success')
