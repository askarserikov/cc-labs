import boto3
import logging
import time
import csv

logging.getLogger().setLevel(logging.INFO)
regions = ['eu-central-1', 'us-west-1', 'ap-northeast-1']

with open('measurements.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['ul-eu-central-1', 'ul-us-west-1',	'ul-ap-northeast-1',
                     'dl-eu-central-1',	'dl-us-west-1',	'dl-ap-northeast-1'])
f.close()

csv_values = []
for i in range(0, len(regions)):
    s3 = boto3.client('s3', region_name=regions[i])
    s3.create_bucket(
        ACL='public-read',
        Bucket='celtic-lab2-{}'.format(regions[i]),
        CreateBucketConfiguration={'LocationConstraint': regions[i]}
    )
    logging.info('Created a bucket: celtic-lab2-{}'.format(regions[i]))
    data = open('737400.jpg', 'rb')
    start = time.time()
    s3.put_object(
        ACL='public-read',
        Bucket='celtic-lab2-{}'.format(regions[i]),
        Key='test.jpg',
        Body=data
    )
    end = time.time()
    logging.info('Uploaded the file to celtic-lab2-{} in {} seconds'.format(regions[i], end-start))
    csv_values.append(end-start)

logging.info('Done with part I. Now to downloading...')

for i in range(0, len(regions)):
    s3 = boto3.client('s3', region_name=regions[i])
    start = time.time()
    with open('tmp-{}.jpg'.format(regions[i]), 'wb') as data:
        s3.download_fileobj('celtic-lab2-{}'.format(regions[i]), 'test.jpg', data)
    end = time.time()
    data.close()
    logging.info('Downloaded the file from celtic-lab2-{} in {} seconds'.format(regions[i], end-start))
    csv_values.append(end-start)

with open('measurements.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(csv_values)
f.close()

logging.info('Measurements successfully added to the csv-file. Exiting...')
