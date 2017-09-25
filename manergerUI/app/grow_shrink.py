from flask import render_template
from app import webapp

from app.config import ami_id, instance_type, key_name, userdata, security_group, elbname
import boto3


def grow(num2grow):
    ec2 = boto3.resource('ec2')
    
    instances = []
    for no in range(num2grow):
        instance = ec2.create_instances(ImageId=ami_id,
                                        InstanceType=instance_type,
                                        MinCount=1,
                                        MaxCount=1,
                                        KeyName=key_name,
                                        UserData=userdata,
                                        SecurityGroupIds=security_group,
                                        Monitoring={'Enabled': True})
        
        client = boto3.client('elb')
        response = client.register_instances_with_load_balancer(
            LoadBalancerName=elbname,
            Instances=[
                {'InstanceId': instance[0].id},
            ]
        )
        
        instances.append(instance[0])
        
    return instances

def shrink(num2shrink):
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[
            {'Name': 'image-id', 'Values': [ami_id]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    no = 0
    des_instances = []
    for instance in instances:
        des_instance = Instance(instance.id,
                                instance.instance_type,
                                instance.placement)
        des_instances.append(des_instance)
        
        instance.terminate()
        no += 1
        if no == num2shrink:
            break
        
    return des_instances

class Instance:
    def __init__(self, id, instance_type, placement):
        self.id = id
        self.instance_type = instance_type
        self.placement = placement
        
@webapp.route('/worker/destory_<id>')
def destory(id):
    ec2 = boto3.resource('ec2')
    
    instance = ec2.Instance(id)
    des_instance = Instance(instance.id,
                            instance.instance_type,
                            instance.placement)
    instance.terminate()
    
    return render_template('mgr/grow_shrink_complete.html',
                           title='Worker pool is shrinked',
                           action='shrink',
                           instances=[des_instance])


@webapp.route('/worker/man_grow')
def man_grow():
    instances = grow(1)
    
    return render_template('mgr/grow_shrink_complete.html',
                           title='Worker pool is growed',
                           action='grow',
                           instances=instances)

@webapp.route('/worker/man_shrink')
def man_shrink():
    des_instances = shrink(1)
    return render_template('mgr/grow_shrink_complete.html',
                           title='Worker pool is shrinked',
                           action='shrink',
                           instances=des_instances)