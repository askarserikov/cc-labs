from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver
import logging
import csv
import time

ACCESS_KEY = ''
SECRET_KEY = ''

logging.getLogger().setLevel(logging.INFO)
regions = ['eu-central-1', 'us-west-1', 'ap-northeast-1']
providers = [Provider.S3_EU_CENTRAL, Provider.S3_US_WEST, Provider.S3_AP_NORTHEAST1]

with open('measurements-libcloud.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['ul-eu-central-1', 'ul-us-west-1',	'ul-ap-northeast-1',
                     'dl-eu-central-1',	'dl-us-west-1',	'dl-ap-northeast-1'])
f.close()

csv_values = []
for i in range(0, len(regions)):
    cls = get_driver(providers[i])
    driver = cls(ACCESS_KEY, SECRET_KEY)
    container = driver.create_container(container_name='celtic-lab2-libcloud-{}'.format(regions[i]))
    logging.info('Created a bucket: celtic-lab2-libcloud-{}'.format(regions[i]))
    start = time.time()
    driver.upload_object(file_path='737400.jpg',
                         container=container,
                         object_name='test.jpg')
    end = time.time()
    logging.info('Uploaded the file in {} seconds'.format(end - start))
    csv_values.append(end - start)

logging.info('Done with part I. Now to downloading...')

for i in range(0, len(regions)):
    cls = get_driver(providers[i])
    driver = cls(ACCESS_KEY, SECRET_KEY)
    driver.get_container(container_name='celtic-lab2-libcloud-{}'.format(regions[i]))
    logging.info('Connected to the bucket: celtic-lab2-libcloud-{}. Downloading the file...'.format(regions[i]))
    start = time.time()
    obj = driver.get_object(container_name='celtic-lab2-libcloud-{}'.format(regions[i]), object_name='test.jpg')
    driver.download_object(obj, 'tmp-libcloud-{}.jpg'.format(regions[i]), overwrite_existing=True)
    end = time.time()
    logging.info('Downloaded the file in {} seconds'.format(end - start))
    csv_values.append(end - start)

with open('measurements-libcloud.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(csv_values)
f.close()

logging.info('Measurements successfully added to the csv-file. Exiting...')
