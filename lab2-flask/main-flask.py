import time

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import boto3

app = Flask(__name__)


@app.route("/s3")
def hello():
    return render_template('file_picker.html')


@app.route("s3/processing", methods=['POST'])
def processing():
    output = []
    file = request.files['file'].read()
    regions = request.form.getlist('region[]')
    for region in regions:
        s3 = boto3.client('s3', region_name=region)
        output.append('Creating a bucket in {}'.format(region))
        start = time.time()
        s3.create_bucket(
            ACL='public-read',
            Bucket='celtic-lab2-{}'.format(region),
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        end = time.time()
        output.append('Created the bucket in {} seconds'.format(end-start))
        output.append('Uploading the file...')
        start = time.time()
        s3.put_object(
            ACL='public-read',
            Bucket='celtic-lab2-{}'.format(region),
            Key='test.jpg',
            Body=file
        )
        end = time.time()
        output.append('Uploaded the file in {} seconds'.format(end - start))
        output.append('Success!')
        s = "<br>".join(output)
    return s


@app.route("s3/cleanup", methods=['POST'])
def cleanup():
    regions = ['eu-central-1', 'us-west-1', 'ap-northeast-1']
    output = []
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
            output.append('Removed the bucket at {}'.format(regions[i]))
        except Exception as e:
            pass
        #os.remove('tmp-{}.jpg'.format(regions[i]))
    output.append('Done')
    s = "<br>".join(output)
    return s

