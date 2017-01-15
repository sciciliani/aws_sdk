import botocore.session
import boto3
import config
import pprint
import datetime
import json 

cfg = config.params['ignite']


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def get_ec2_instances():
	ec2 = session.resource('ec2')
	instances = ec2.instances.filter(    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
	dump(instances)
	

def s3():
	s3 = session.resource('s3')

	for bucket in s3.buckets.all():
		print(bucket.name)

def main():
#	get_ec2_instances()
#	get_autoscalinggroups()
#	asgid = "mybb110-asgmybbautoscalling-SSPYQ0ZS8Y8L"
#	metricname = "GroupMaxSize"
#	get_cw_metrics(asgid, metricname)
#	dynamo_create_table()
#	dynamo_use_table()
#	dynamo_put_item()
#	dynamo_get_item()
	dynamo_list_tables()

def dump(obj):
	for attr in dir(obj):
		print "obj.%s = %s" % (attr, getattr(obj, attr))

def get_autoscalinggroups():
	client = boto3.client('autoscaling', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
	response = client.describe_auto_scaling_groups( MaxRecords=100 )
	print json.dumps(response, default=datetime_handler)

#	for r in response['AutoScalingGroups']:
#		print r['AutoScalingGroupARN']
#		print json.dumps(r)

#	print json.dumps(response, indent=4, sort_keys=True)

#	a = []
#	for r in response['AutoScalingGroups']:
#		a.append(r['ResourceId'])
		
#	print json.dumps(a, indent=4, sortKeys=True)

def get_autoscalinggroups_instances(AutoScalingGroupName):
	client = boto3.client('autoscaling', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
	response = client.describe_auto_scaling_instances( AutoScalingGroupName=AutoScalingGroupName, MaxRecords=100 )
	print response

def get_cw_metrics(asgid, metricname):

	from datetime import date, datetime

	client = boto3.client('cloudwatch', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])

	response = client.get_metric_statistics(
	    Namespace='AWS/AutoScaling',
	    MetricName=metricname,
	    Dimensions=[
	        {
	            'Name': 'AutoScalingGroupName',
	            'Value': asgid
	        },
	    ],
	    StartTime=datetime(2017, 1, 14, 0, 0, 0),
	    EndTime=datetime(2017, 1, 14, 23, 59, 59),
	    Period=60,
	    Statistics=[
	        'Average'
	    ],
	    Unit='None'
	)

	print json.dumps(response, default=datetime_handler)


def dynamo_create_table():
	client = boto3.client('dynamodb', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
	response = client.create_table(
    		TableName='users',
    		KeySchema=[
        		{
	            		'AttributeName': 'username',
        	    		'KeyType': 'HASH'
        		},
        		{
            			'AttributeName': 'password',
            			'KeyType': 'RANGE'
        		}
    		],
		    AttributeDefinitions=[
        		{
		            'AttributeName': 'username',
		            'AttributeType': 'S'
        		},
        		{
		            'AttributeName': 'password',
		            'AttributeType': 'S'
		        },

    		],
    		ProvisionedThroughput={
		        'ReadCapacityUnits': 5,
		        'WriteCapacityUnits': 5
		    }
		)

	print json.dumps(response, default=datetime_handler)


def dynamo_use_table():
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('users')

	print(table.creation_date_time)

def dynamo_put_item():
	client = boto3.client('dynamodb', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
	response = client.put_item(
	   TableName="users",
	   Item={ 'username': 'admin',
        	'first_name': 'Santiago',
        	'last_name': 'Ciciliani',
        	'age': 32,
        	'account_type': 'administrator',
		'password': 'letmein'
	    }
	)
	print json.dumps(response, default=datetime_handler)

def dynamo_get_item():
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('users')
	response = table.get_item(
    	Key={
        	'username': 'admin',
        	'password': 'password1'
    	}
	)
	item = response['Item']
	print(item)

def dynamo_delete_table():
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('users')
	table.delete()

def dynamo_list_tables():
	client = boto3.client('dynamodb', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
	response = client.list_tables()
	print json.dumps(response, default=datetime_handler)
	
if  __name__ =='__main__':main()

