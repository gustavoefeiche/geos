# AWS
AWS_INFO = {
    'AWS_VPC_CIDR'                   : '172.31.0.0/16',
    'AWS_VPC_NAME'                   : 'GEOS-VPC',
    'AWS_SUBNET_BASE_NAME'           : 'GEOS-SUBNET-',
    'AWS_ROUTE_TABLE_NAME'           : 'GEOS-ROUTE-TABLE',
    'AWS_GATEWAY_NAME'               : 'GEOS-GATEWAY',
    'AWS_INSTANCE_NAME'              : 'GEOS-INSTANCE',
    'AWS_INSTANCE_TYPE'              : 't2.micro',
    'AWS_LAUNCH_CONFIG_NAME'         : 'GEOS-LAUNCH-CONFIG',
    'AWS_AUTO_SCALING_GROUP_NAME'    : 'GEOS-AUTO-SCALING-GROUP',
    'AWS_LOAD_BALANCER_NAME'         : 'GEOS-LOAD-BALANCER',
    'AWS_TARGET_GROUP_NAME'          : 'GEOS-TARGET-GROUP',
    'AWS_TARGET_GROUP_PROTOCOL'      : 'HTTP',
    'AWS_TARGET_GROUP_PORT'          : 80,
    'AWS_SECURITY_GROUP_NAME'        : 'GEOS-SECURITY-GROUP',
    'AWS_SECURITY_GROUP_DESCRIPTION' : 'GEOS security group (allow HTTP)',
    'AWS_KEYPAIR_NAME'               : 'GEOS-KEYPAIR',
    'AWS_MIN_INSTANCES'              : 4,
    'AWS_MAX_INSTANCES'              : 6,
    'AWS_DESIRED_INSTANCES'          : 4,
    'AWS_USER_DATA'                  : "echo $(hostname -I | cut -d\  -f1) $(hostname) | sudo tee -a /etc/hosts\nsudo apachectl restart"
}

# STATUS MESSAGES
STATUS_MSGS = {
    'STATUS_SUCCESS'                    : 'Done!',
    'STATUS_THE_END'                    : 'Deploy completed!',
    'STATUS_CONNECT_EC2'                : 'Connecting to AWS EC2 service...',
    'STATUS_CONNECT_AS'                 : 'Connecting to AWS Auto Scaling service...',
    'STATUS_CONNECT_ELB'                : 'Connecting to AWS Elastic Load Balancing service...',
    'STATUS_CREATE_VPC'                 : 'Creating VPC (Name: {0}, CIDR: {1})'.format(AWS_INFO['AWS_VPC_NAME'], AWS_INFO['AWS_VPC_CIDR']),
    'STATUS_CREATE_SUBNETS'             : 'Creating subnets (1 subnet for each Availability Zone)',
    'STATUS_CREATE_GATEWAY'             : 'Creating Internet Gateway (Name: {})'.format(AWS_INFO['AWS_GATEWAY_NAME']),
    'STATUS_ADD_ROUTE'                  : 'Adding route with destination 0.0.0.0/0 to target {}'.format(AWS_INFO['AWS_GATEWAY_NAME']),
    'STATUS_ATTACH_SUBNETS'             : 'Attaching subnets to route table {}'.format(AWS_INFO['AWS_ROUTE_TABLE_NAME']),
    'STATUS_CREATE_SECURITY_GROUP'      : 'Creating Security Group {} (allow ingress on port 80 - HTTP)'.format(AWS_INFO['AWS_SECURITY_GROUP_NAME']),
    'STATUS_CREATE_KEYPAIR'             : 'Creating keypair {0} and saving private key to {0}.pem'.format(AWS_INFO['AWS_KEYPAIR_NAME']),
    'STATUS_CREATE_LAUNCH_CONFIG'       : 'Creating launch configuration {}'.format(AWS_INFO['AWS_LAUNCH_CONFIG_NAME']),
    'STATUS_CREATE_AUTO_SCALING_GROUP'  : 'Creating Auto Scaling Group {}'.format(AWS_INFO['AWS_AUTO_SCALING_GROUP_NAME']),
    'STATUS_CREATE_TARGET_GROUP'        : 'Creating Target Group {}'.format(AWS_INFO['AWS_TARGET_GROUP_NAME']),
    'STATUS_CREATE_LOAD_BALANCER'       : 'Creating Load Balancer {}'.format(AWS_INFO['AWS_LOAD_BALANCER_NAME']),
    'STATUS_REGISTER_TARGETS'           : 'Registering targets',
    'STATUS_ATTACH_TARGET_GROUP'        : 'Attaching Target Group {0} to Auto Scaling Group {1}'.format(AWS_INFO['AWS_TARGET_GROUP_NAME'], AWS_INFO['AWS_AUTO_SCALING_GROUP_NAME'])
}
# ERROR MESSAGES
ERROR_MSGS = {
    'ERROR_CONFIG_FILE_NOTFOUND'        : 'Configuration file not found (geosconfig.py). Was file moved or deleted?',
    'ERROR_BOTO3_NOTFOUND'              : 'AWS Boto3 was not found. Run: pip3 install boto3',
    'ERROR_CONNECT_EC2'                 : 'Connection to AWS EC2 service failed. Exiting...',
    'ERROR_CONNECT_AS'                  : 'Connection to AWS Auto Scaling service failed. Exiting...',
    'ERROR_CONNECT_ELB'                 : 'Connection to AWS Elastic Load Balancing service failed. Exiting...',
}

def geos_log(message):
    print(message)