import os


db_config = {
    'user': 'ece1779',
    'password': 'ece1779pass',
    'host': '54.164.212.253',
    'database': 'ece1779_a1'
}

mybucket = 'ece1779b1'

instance_type = 't2.small'
key_name = 'ece1779_syr'
security_group = ['sg-b60ac3c9']
elbname = 'syr-load-balancer'
ami_id = 'ami-e240e9f4'
userdata = """#cloud-config
runcmd:
 - cd /home/ubuntu/Desktop/ece1779/aws
 - ./venv/bin/python run.py

output : { all : '| tee -a /var/log/cloud-init-output.log' }
"""
