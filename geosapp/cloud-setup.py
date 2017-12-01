import sys

try:
    from geosconfig import AWS_INFO, STATUS_MSGS, ERROR_MSGS, geos_log
except ModuleNotFoundError:
    geos_log(ERROR_MSGS['ERROR_CONFIG_FILE_NOTFOUND'])
    sys.exit()

try:
    import boto3
except ModuleNotFoundError:
    geos_log(ERROR_MSGS['ERROR_BOTO3_NOTFOUND'])
    sys.exit()

# Connect to AWS services
try:
    geos_log(STATUS_MSGS['STATUS_CONNECT_EC2'])
    ec2_client = boto3.client('ec2')    
except:
    geos_log(ERROR_MSGS['ERROR_CONNECT_EC2'])
    sys.exit()

try:
    geos_log(STATUS_MSGS['STATUS_CONNECT_AS'])
    as_client = boto3.client('autoscaling')    
except Exception:
    geos_log(ERROR_MSGS['ERROR_CONNECT_AS'])
    sys.exit()

try:
    geos_log(STATUS_MSGS['STATUS_CONNECT_ELB'])
    elb_client = boto3.client('elbv2')
except:
    geos_log(ERROR_MSGS['ERROR_CONNECT_ELB'])
    sys.exit()

# Create new VPC and set name tag
print(STATUS_MSGS['STATUS_CREATE_VPC'])
geos_vpc = ec2_client.create_vpc(CidrBlock=AWS_INFO['AWS_VPC_CIDR'])
geos_vpc_id = geos_vpc['Vpc']['VpcId']

ec2_client.create_tags(
    Resources=[
        geos_vpc_id
    ],
    Tags = [
        {
            'Key': 'Name',
            'Value': AWS_INFO['AWS_VPC_NAME']
        }
    ]
)

# Create subnets and attach to newly create VPC
print(STATUS_MSGS['STATUS_CREATE_SUBNETS'])
avail_zones = ec2_client.describe_availability_zones()['AvailabilityZones']
region = avail_zones[0]['RegionName']

geos_subnets = []
subnet_names = []
subnet_ids = []
sufix = 'a'

for octet in range(0, len(avail_zones) * 16, 16):
    subnet = {
        'name':'{0}{1}'.format(AWS_INFO['AWS_SUBNET_BASE_NAME'], sufix),
        'cidr':'172.31.{}.0/20'.format(octet),
        'az':'{0}{1}'.format(region, sufix)
    }
    
    sufix = chr(ord(sufix) + 1)

    subnet_names.append(subnet['name'])
    print('Creating subnet {0} with CIDR {1}'.format(subnet['name'], subnet['cidr']))
    geos_subnets.append(ec2_client.create_subnet(AvailabilityZone=subnet['az'], CidrBlock=subnet['cidr'], VpcId=geos_vpc_id))

for subnet in geos_subnets:
    subnet_id = subnet['Subnet']['SubnetId']
    subnet_ids.append(subnet_id)
    ec2_client.create_tags(
        Resources=[
            subnet_id
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': subnet_names[geos_subnets.index(subnet)]
            }
        ]
    )

# Create Internet Gateway and attach to newly created VPC
print(STATUS_MSGS['STATUS_CREATE_GATEWAY'])
geos_gateway = ec2_client.create_internet_gateway()
geos_gateway_id = geos_gateway['InternetGateway']['InternetGatewayId']

ec2_client.create_tags(
    Resources=[
        geos_gateway_id
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': AWS_INFO['AWS_GATEWAY_NAME']
        }
    ]
)

print('Attaching gateway {0} to {1}'.format(AWS_INFO['AWS_GATEWAY_NAME'], AWS_INFO['AWS_VPC_NAME']))
ec2_client.attach_internet_gateway(InternetGatewayId=geos_gateway_id, VpcId=geos_vpc_id)

# Add route (0.0.0.0/0 => gateway) in VPC route table
print(STATUS_MSGS['STATUS_ADD_ROUTE'])
geos_route_table_id = ec2_client.describe_route_tables(
    Filters=[
        {
            'Name': 'vpc-id',
            'Values': [
                geos_vpc_id,
            ]
        }
    ]
)['RouteTables'][0]['RouteTableId']

ec2_client.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=geos_gateway_id, RouteTableId=geos_route_table_id)

# Attach newly created subnets to route table
print(STATUS_MSGS['STATUS_ATTACH_SUBNETS'])
for subnet in geos_subnets:
    geos_subnet_id = subnet['Subnet']['SubnetId']
    ec2_client.associate_route_table(RouteTableId=geos_route_table_id, SubnetId=geos_subnet_id)

# Rename route table
ec2_client.create_tags(
    Resources=[
        geos_route_table_id
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': AWS_INFO['AWS_ROUTE_TABLE_NAME']
        }
    ]
)

# Create security group to be used with auto scaling instances
print(STATUS_MSGS['STATUS_CREATE_SECURITY_GROUP'])
geos_security_group = ec2_client.create_security_group(
    GroupName=AWS_INFO['AWS_SECURITY_GROUP_NAME'], VpcId=geos_vpc_id, Description=AWS_INFO['AWS_SECURITY_GROUP_DESCRIPTION'])

geos_security_group_id = geos_security_group['GroupId']

ec2_client.authorize_security_group_ingress(
    GroupId=geos_security_group_id, IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=80, ToPort=80)

ec2_client.authorize_security_group_ingress(
    GroupId=geos_security_group_id, IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=27017, ToPort=27017)

ec2_client.create_tags(
    Resources=[
        geos_security_group_id
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': AWS_INFO['AWS_SECURITY_GROUP_NAME']
        }
    ]
)

# Create key pair to be used with project instances
print(STATUS_MSGS['STATUS_CREATE_KEYPAIR'])
geos_keypair = ec2_client.create_key_pair(KeyName=AWS_INFO['AWS_KEYPAIR_NAME'])
keypair_file = open('{}.pem'.format(AWS_INFO['AWS_KEYPAIR_NAME']), 'w')
keypair_file.write('{}'.format(geos_keypair['KeyMaterial']))
keypair_file.close()

# Create launch configuration for autoscaling instances
print(STATUS_MSGS['STATUS_CREATE_LAUNCH_CONFIG'])
if region == 'us-east-1':
    image_id = 'ami-caa930b0'
elif region == 'us-east-2':
    image_id = 'ami-945b72f1'

geos_launch_config = as_client.create_launch_configuration(
    LaunchConfigurationName=AWS_INFO['AWS_LAUNCH_CONFIG_NAME'],
    ImageId=image_id,
    InstanceType=AWS_INFO['AWS_INSTANCE_TYPE'],
    SecurityGroups=[geos_security_group_id],
    UserData=AWS_INFO['AWS_USER_DATA'],
    KeyName=AWS_INFO['AWS_KEYPAIR_NAME']
)

# Create Auto Scaling Group
print(STATUS_MSGS['STATUS_CREATE_AUTO_SCALING_GROUP'])
subnet_list = ",".join(subnet_ids)
geos_auto_scaling_group = as_client.create_auto_scaling_group(
    AutoScalingGroupName=AWS_INFO['AWS_AUTO_SCALING_GROUP_NAME'],
    LaunchConfigurationName=AWS_INFO['AWS_LAUNCH_CONFIG_NAME'],
    MinSize=AWS_INFO['AWS_MIN_INSTANCES'],
    MaxSize=AWS_INFO['AWS_MAX_INSTANCES'],
    VPCZoneIdentifier=subnet_list
)

# Create Target Group
print(STATUS_MSGS['STATUS_CREATE_TARGET_GROUP'])
geos_target_group = elb_client.create_target_group(
    Name=AWS_INFO['AWS_TARGET_GROUP_NAME'],
    Protocol=AWS_INFO['AWS_TARGET_GROUP_PROTOCOL'],
    Port=AWS_INFO['AWS_TARGET_GROUP_PORT'],
    VpcId=geos_vpc_id
)

for tg in geos_target_group['TargetGroups']:
    if tg['TargetGroupName'] == AWS_INFO['AWS_TARGET_GROUP_NAME']:
        geos_target_group_arn = tg['TargetGroupArn']

# Create Load Balancer and attach targets inside Target Group
print(STATUS_MSGS['STATUS_CREATE_LOAD_BALANCER'])
geos_load_balancer = elb_client.create_load_balancer(
    Name=AWS_INFO['AWS_LOAD_BALANCER_NAME'],
    Subnets=subnet_ids,
    SecurityGroups=[geos_security_group_id]
)

for lb in geos_load_balancer['LoadBalancers']:
    if lb['LoadBalancerName'] == AWS_INFO['AWS_LOAD_BALANCER_NAME']:
        geos_load_balancer_url = lb['DNSName']
        geos_load_balancer_arn = lb['LoadBalancerArn']

# Create Load Balancer listener for target group
elb_client.create_listener(
    LoadBalancerArn=geos_load_balancer_arn,
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
            'TargetGroupArn': geos_target_group_arn,
            'Type': 'forward',
        },
    ],
)

# Attach Target Group to Auto Scaling Group
print(STATUS_MSGS['STATUS_ATTACH_TARGET_GROUP'])
as_client.attach_load_balancer_target_groups(
    AutoScalingGroupName=AWS_INFO['AWS_AUTO_SCALING_GROUP_NAME'],
    TargetGroupARNs=[
        geos_target_group_arn,
    ]
)

# Attach public addresses to instances
# ids = []
# ips = []
# instances = ec2_client.describe_instances()

# for i in instances['Reservations']:
#     ids.append(i['Instances'][0]['InstanceId'])

# for i in ids:
#     address = ec2_client.allocate_address(Domain='vpc')
#     ips.append(address['PublicIp'])

# for i in range(len(ips)):
#     ec2_client.associate_address(
#         InstanceId=ids[i],
#         PublicIp=ips[i],
#     )

# Send URL to CLI
lburl = open('lburl.py', 'w')
lburl.write('LOAD_BALANCER_URL = "http://{}/api/users"'.format(geos_load_balancer_url))
lburl.close()

print(STATUS_MSGS['STATUS_THE_END'])
print("GEOS URL: {}".format(geos_load_balancer_url))
