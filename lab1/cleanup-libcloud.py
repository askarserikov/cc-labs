from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver
import os

ACCESS_KEY = 'AKIAJJ6ZIQOWZTQYPNCQ'
SECRET_KEY = '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'

regions = ['eu-central-1', 'us-west-1', 'ap-northeast-1']
providers = [Provider.S3_EU_CENTRAL, Provider.S3_US_WEST, Provider.S3_AP_NORTHEAST1]

for i in range(0, len(regions)):
    cls = get_driver(providers[i])
    driver = cls(ACCESS_KEY, SECRET_KEY)
    try:
        obj = driver.get_object(container_name='celtic-lab2-libcloud-{}'.format(regions[i]), object_name='test.jpg')
        driver.delete_object(obj=obj)
        container = driver.get_container(container_name='celtic-lab2-libcloud-{}'.format(regions[i]))
        driver.delete_container(container=container)
    except Exception as e:
        pass

    try:
        container = driver.get_container(container_name='celtic-lab2-libcloud-{}'.format(regions[i]))
        driver.delete_container(container=container)
    except Exception as e:
        pass

    os.remove('tmp-libcloud-{}.jpg'.format(regions[i]))

print('Success')
