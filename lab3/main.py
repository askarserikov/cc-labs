import boto3
import logging
import json
import time
import base64

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

logging.getLogger().setLevel(logging.INFO)
regions = ['eu-central-1', 'us-west-1', 'ap-northeast-1']

@app.route("/s3")
def hello():
    return render_template('file_picker.html')


@app.route("/s3/processing", methods=['POST'])
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


@app.route("/s3/cleanup", methods=['POST'])
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


@app.route("/ec2")
def ec2():
    return render_template("index.html")


@app.route("/ec2/create_instance", methods=['POST'])
def create_instance():
    print(request.form)
    try:
        ec2r = initialize_ec2_resource(request.form['region'])
        ins = ec2r.create_instances(
            ImageId=request.form['ami-id'],
            KeyName=request.form['keypair'],
            InstanceType='t2.micro',
            SecurityGroupIds=[request.form['sec-group']],
            MinCount=1,
            MaxCount=1
        )
        instance = ins[0]
        instance.create_tags(
            Tags=[{'Key': 'Name', 'Value': request.form['name']}]
        )
        response = {'type': 'success', 'message': 'Successfully created the instance'}
    except Exception as e:
        response = {'type': 'error', 'message': str(e)}

    return jsonify(response)


@app.route("/ec2/create_key_pair", methods=['POST'])
def create_key_pair():
    print(request.form)
    try:
        ec2r = initialize_ec2_resource(request.form['region'])
        create_key_pair(ec2r, request.form['keyname'])
        response = {'type': 'success', 'message': 'Successfully created the key pair'}
    except Exception as e:
        response = {'type': 'error', 'message': str(e)}
    return jsonify(response)


@app.route("/ec2/create_sec_group", methods=['POST'])
def create_sec_group():
    print(request.form)
    try:
        ec2r = initialize_ec2_resource(request.form['region'])
        ec2 = initialize_ec2_client(request.form['region'])
        sg = ec2.create_security_group(Description=request.form['description'], GroupName=request.form['groupname'])
        sgr = ec2r.SecurityGroup(sg['GroupId'])
        sgr.authorize_ingress(
            GroupName=request.form['groupname'],
            IpPermissions=[
                {
                    'IpProtocol': '-1',
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        response = {
            'type': 'success',
            'message': 'Successfully created the security group. Security Group ID: {}'.format(sg['GroupId'])
        }
    except Exception as e:
        response = {'type': 'error', 'message': str(e)}
    return jsonify(response)


@app.route("/ec2/create_dashboard", methods=['POST'])
def create_dashboard():
    try:
        cw = initialize_cw_client(request.form['region'])
        cw.put_dashboard(
            DashboardName=request.form['name'],
            DashboardBody="""
            {
            "widgets":[
              {
                 "type":"metric",
                 "x":12,
                 "y":0,
                 "width":12,
                 "height":6,
                 "properties":{
                    "metrics":[
                       [
                          "AWS/EC2",
                          "StatusCheckFailed_Instance",
                          "InstanceId",
                          "i-0b6bd195ed8fb872d"
                       ]
                    ],
                    "period":300,
                    "stat":"Average",
                    "region":"eu-central-1",
                    "title":"Celtic EC2 Instance Status Check"
                 }
              },
              {
                 "type":"metric",
                 "x":0,
                 "y":0,
                 "width":12,
                 "height":6,
                 "properties":{
                    "metrics":[
                       [
                          "AWS/EC2",
                          "CPUUtilization",
                          "InstanceId",
                          "i-0b6bd195ed8fb872d"
                       ]
                    ],
                    "period":300,
                    "stat":"Average",
                    "region":"eu-central-1",
                    "title":"Celtic EC2 Instance CPU Utilization"
                 }
              },
              {
                 "type":"metric",
                 "x":12,
                 "y":0,
                 "width":12,
                 "height":6,
                 "properties":{
                    "metrics":[
                       [
                          "AWS/EC2",
                          "DiskReadBytes",
                          "InstanceId",
                          "i-0b6bd195ed8fb872d"
                       ],
                       [
                          "AWS/EC2",
                          "DiskWriteBytes",
                          "InstanceId",
                          "i-0b6bd195ed8fb872d"
                       ]
                    ],
                    "period":300,
                    "stat":"Average",
                    "region":"eu-central-1",
                    "title":"Celtic EC2 Instance Disk Read/Write Bytes"
                 }
              },
              {
                 "type":"metric",
                 "x":0,
                 "y":0,
                 "width":12,
                 "height":6,
                 "properties":{
                    "metrics":[
                       [
                          "AWS/EC2",
                          "NetworkIn",
                          "InstanceId",
                          "i-0b6bd195ed8fb872d"
                       ],
                       [
                          "AWS/EC2",
                          "NetworkOut",
                          "InstanceId",
                          "i-0b6bd195ed8fb872d"
                       ]
                    ],
                    "period":300,
                    "stat":"Average",
                    "region":"eu-central-1",
                    "title":"Celtic EC2 Instance Network In/Out"
                 }
              }
           ]
           }   
           """
        )
        response = {
            'type': 'success',
            'message': 'Successfully created the dashboard'
        }
    except Exception as e:
        response = {'type': 'error', 'message': str(e)}
    return jsonify(response)


@app.route("/ec2/dashboard_as_images", methods=['POST'])
def dashboard_as_images():
    cw = initialize_cw_client(request.form['region'])
    image = cw.get_metric_widget_image(
        MetricWidget="""
            {
                "width": 600,
                "height": 395,
                "metrics": [
                    [
                        "AWS/EC2",
                        "NetworkIn",
                        "InstanceId",
                        \"""" + request.form['name'] + """\",
                        {
                            "stat": "Average"
                        }
                    ],
                    [
                        "AWS/EC2",
                        "NetworkOut",
                        "InstanceId",
                        \"""" + request.form['name'] + """\",
                        {
                            "stat": "Average"
                        }
                    ]
                ],
                "period": 300,
                "start": "-PT3H",
                "end": "PT0H",
                "stacked": false,
                "yAxis": {
                    "left": {
                        "min": 1,
                        "max": 10000
                    },
                    "right": {
                        "min": 0
                    }
                },
                "title": "Network In/Out"
            }
        """
    )
    image = image['MetricWidgetImage']
    images = [base64.b64encode(image).decode('ascii')]
    image = cw.get_metric_widget_image(
        MetricWidget="""
                {
                    "width": 600,
                    "height": 395,
                    "metrics": [
                        [
                            "AWS/EC2",
                            "CPUUtilization",
                            "InstanceId",
                            \"""" + request.form['name'] + """\",
                            {
                                "stat": "Average"
                            }
                        ]
                    ],
                    "period": 300,
                    "start": "-PT3H",
                    "end": "PT0H",
                    "stacked": false,
                    "yAxis": {
                        "left": {
                            "min": 0.1,
                            "max": 10
                        },
                        "right": {
                            "min": 0
                        }
                    },
                    "title": "CPU Utilization"
                }
            """
    )
    image = image['MetricWidgetImage']
    images.append(base64.b64encode(image).decode('ascii'))

    image = cw.get_metric_widget_image(
        MetricWidget="""
                    {
                        "width": 600,
                        "height": 395,
                        "metrics": [
                            [
                                "AWS/EC2",
                                "DiskReadBytes",
                                "InstanceId",
                                \"""" + request.form['name'] + """\",
                                {
                                    "stat": "Average"
                                }
                            ],
                            [
                                "AWS/EC2",
                                "DiskWriteBytes",
                                "InstanceId",
                                \"""" + request.form['name'] + """\",
                                {
                                    "stat": "Average"
                                }
                            ]
                        ],
                        "period": 300,
                        "start": "-PT3H",
                        "end": "PT0H",
                        "stacked": false,
                        "yAxis": {
                            "left": {
                                "min": 1,
                                "max": 10000
                            },
                            "right": {
                                "min": 0
                            }
                        },
                        "title": "Disk Read/Write Bytes"
                    }
                """
    )

    image = image['MetricWidgetImage']
    images.append(base64.b64encode(image).decode('ascii'))

    image = cw.get_metric_widget_image(
        MetricWidget="""
                        {
                            "width": 600,
                            "height": 395,
                            "metrics": [
                                [
                                    "AWS/EC2",
                                    "StatusCheckFailed_Instance",
                                    "InstanceId",
                                    \"""" + request.form['name'] + """\",
                                    {
                                        "stat": "Average"
                                    }
                                ]
                            ],
                            "period": 300,
                            "start": "-PT3H",
                            "end": "PT0H",
                            "stacked": false,
                            "yAxis": {
                                "left": {
                                    "min": 0,
                                    "max": 1
                                },
                                "right": {
                                    "min": 0
                                }
                            },
                            "title": "Status Check"
                        }
                    """
    )

    image = image['MetricWidgetImage']
    images.append(base64.b64encode(image).decode('ascii'))

    response = {'images': images}

    return jsonify(response)


def initialize_ec2_client(region='eu-central-1'):
    ec2_client = boto3.client('ec2', region_name=region)
    return ec2_client


def initialize_ec2_resource(region='eu-central-1'):
    ec2_resource = boto3.resource('ec2', region_name=region)
    return ec2_resource


def initialize_cw_client(region='eu-central-1'):
    cw_client = boto3.client('cloudwatch', region_name=region)
    return cw_client


def initialize_cw_resource(region='eu-central-1'):
    cw_resource = boto3.resource('cloudwatch', region_name=region)
    return cw_resource


def get_metrics_from_dashboard(dn, cw):
    cw.get_dashboard(DashboardName=dn)


def create_security_group(description, groupname, ec2client, ec2resource):
    sg = ec2client.create_security_group(Description=description, GroupName=groupname)
    sgr = ec2resource.SecurityGroup(sg['GroupId'])
    sgr.authorize_ingress(
        GroupName=groupname,
        IpPermissions=[
            {
                'IpProtocol': '-1',
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
    return sg


def create_key_pair(ec2r, keyname):
    key_pair = ec2r.create_key_pair(
        KeyName=keyname,
    )
    return key_pair


def cleanup(ec2c, sg, kp, ins=None):
    ec2c.terminate_instances(
        InstanceIds=[ins[0].id]
    )

    ec2c.delete_key_pair(
        KeyName=kp.name
    )

    ec2c.delete_security_group(
        GroupId=sg['GroupId']
    )
