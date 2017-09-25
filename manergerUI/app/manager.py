from flask import render_template, redirect, url_for
from app import webapp

import mysql.connector
from app.config import db_config, mybucket, ami_id
import boto3
from datetime import datetime, timedelta
from operator import itemgetter


@webapp.route('/mgr_index')
def mgr_index():
    return render_template('mgr/index.html',
                           title='Hello, Manager!')


@webapp.route('/worker_pool')
def worker_pool():
    ec2 = boto3.resource('ec2')

    instances = ec2.instances.filter(
        Filters=[
            {'Name': 'image-id', 'Values': [ami_id]},
            {'Name': 'instance-state-name', 'Values': ['running', 'pending']}
        ]
    )
    return render_template("mgr/worker_pool.html",
                           title="Worker Pool",
                           instances=instances)


@webapp.route('/worker/<id>')
def worker_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')
    
    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistics=['Average'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )
    
    cpu_stats = []


    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))


    network_in = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkIn',
        Namespace='AWS/EC2',
        Statistics=['Sum'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_in_stats = []

    for point in network_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_in_stats.append([time,point['Sum']])

    net_in_stats = sorted(net_in_stats, key=itemgetter(0))



    network_out = client.get_metric_statistics(
        Period=5 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkOut',
        Namespace='AWS/EC2',
        Statistics=['Sum'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )


    net_out_stats = []

    for point in network_out['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_out_stats.append([time,point['Sum']])

        net_out_stats = sorted(net_out_stats, key=itemgetter(0))

    return render_template('mgr/worker_view.html',
                           title='Worker Info',
                           instance=instance,
                           time=datetime.now(),
                           cpu_stats=cpu_stats,
                           net_in_stats=net_in_stats,
                           net_out_stats=net_out_stats)
