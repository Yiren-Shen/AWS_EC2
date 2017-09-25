from flask import render_template, request
from app import webapp

from app.config import ami_id
from app.grow_shrink import grow, shrink
import boto3
from datetime import datetime, timedelta
from operator import itemgetter


def get_pool_state():
    ec2 = boto3.resource('ec2')

    instances = ec2.instances.filter(
        Filters=[
            {'Name': 'image-id', 'Values': [ami_id]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )    
    
    client = boto3.client('cloudwatch')
    
    num = 0
    cpu_util = 0
    for instance in instances:
        cpu = client.get_metric_statistics(
            Period=1 * 60,
            StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
            EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            Statistics=['Average'],
            Dimensions=[{'Name': 'InstanceId', 'Value': instance.id}]
        )

        points = cpu['Datapoints']
        end = sorted(points, key=itemgetter('Timestamp'))[-1]
        
        cpu_util += end['Average']
        num += 1
        
    if num == 0:
        pool_state = [0, 0]
    else:
        cpu_util /= num
        pool_state = [num, cpu_util]
        
    return pool_state

@webapp.route('/auto_scaling/threshold_configure')
def thre_conf():
    pool_state = get_pool_state()
    
    return render_template('mgr/auto_scaling.html',
                           title='Auto-scaling',
                           num=pool_state[0],
                           cpu=pool_state[1]
                           )


@webapp.route('/auto_scaling/scale', methods=['get','post'])
def auto_scale():
    
    grow_thre = int(request.form.get('grow_thre'))
    grow_ratio = float(request.form.get('grow_ratio'))
    shrink_thre = int(request.form.get('shrink_thre'))
    shrink_ratio = int(request.form.get('shrink_ratio'))
        
    if cpu > grow_thre:
        num2grow = int(num * grow_ratio) - num
        instances = grow(num2grow)
        action='grow'
    elif cpu < shrink_thre:
        num2shrink = num - int(num // shrink_ratio)
        instances = shrink(num2shrink)
        action='shrink'
    else:
        instances = []
        action='none'
    
    pool_state = get_pool_state()
    num = pool_state[0]
    cpu = pool_state[1]
    
    return render_template('mgr/auto_scaling.html',
                           title='Auto-scaling',                           
                           action=action,
                           num=num,
                           cpu=cpu,
                           instances=instances,
                           conf=True)