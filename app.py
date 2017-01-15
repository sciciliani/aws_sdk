import os
import boto3
import config
import json
import datetime
from flask import Flask, session, redirect, url_for, escape, request, render_template, flash, Response, send_from_directory
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

app = Flask(__name__)


def datetime_handler(x):
	if isinstance(x, datetime.datetime):
		return x.isoformat()
	raise TypeError("Unknown type")

@app.route("/")
def root():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		try:
			dynamodb = boto3.resource('dynamodb')
			table = dynamodb.Table('users')
			response = table.get_item(Key={'username': request.form['username'], 'password': request.form['password'] } )
		except ClientError as e:
			print(e.response['Error']['Message'])
			flash('There was a problem connecting with the backend service!')
		else:
			if 'Item' in response:
				item = response['Item']
				session['username'] = item['username']
				session['fullname'] = item['name'] + " " + item['lastname']
				session['logged_in'] = True
				return redirect(url_for('main'))
			else:
				flash('Incorrect Username or Password!')
	return render_template('login.html')

@app.route("/logout")
def logout():
	session.pop('logged_in', None)
	return redirect(url_for('root'))

@app.route("/main")
def main():
	if 'logged_in' in session:
		return render_template('main.html')
	else:
		return redirect(url_for('login'))

@app.route("/api/s3/buckets")
def get_s3_buckets():
	if 'logged_in' in session:
		client = boto3.client('s3', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
		ret = json.dumps(client.list_buckets(), default=datetime_handler)
		return Response(response=ret, status=200, mimetype="application/json")
	else:
		return redirect(url_for('login'))

@app.route("/api/autoscaling")
def get_autoscaling():
	if 'logged_in' in session:
		client = boto3.client('autoscaling', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
		response = client.describe_auto_scaling_groups( MaxRecords=100 )
		
		return json.dumps(response, default=datetime_handler)
	else:
		return redirect(url_for('login'))
@app.route("/api/test/<mynumber>/do")
def test(mynumber):
	return mynumber

@app.route("/api/asg/<asgid>/desired")
def set_desired(asgid):
	if 'logged_in' in session:
		capacity = request.args.get('desired')

		client = boto3.client('autoscaling', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
		response = client.set_desired_capacity(AutoScalingGroupName=asgid, DesiredCapacity=int(capacity))
		print response

		return json.dumps(response, default=datetime_handler)
	else:
		return redirect(url_for('login'))

@app.route("/api/asg/<asgid>/minsize")
def set_minsize(asgid):
	if 'logged_in' in session:
		capacity = request.args.get('minsize')

		client = boto3.client('autoscaling', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
		response = client.update_auto_scaling_group(AutoScalingGroupName=asgid, MinSize=int(capacity))
		print response

		return json.dumps(response, default=datetime_handler)
	else:
		return redirect(url_for('login'))

@app.route("/api/asg/<asgid>/maxsize")
def set_maxsize(asgid):
	if 'logged_in' in session:
		capacity = request.args.get('maxsize')

		client = boto3.client('autoscaling', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
		response = client.update_auto_scaling_group(AutoScalingGroupName=asgid, MaxSize=int(capacity))
		print response

		return json.dumps(response, default=datetime_handler)
	else:
		return redirect(url_for('login'))



@app.route("/api/asg/terminateinstance/<instance>")
def terminate_instace(instance):
	if 'logged_in' in session:
		client = boto3.client('autoscaling', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
		response =client.terminate_instance_in_auto_scaling_group(  InstanceId=instance, ShouldDecrementDesiredCapacity=False )
		
		return json.dumps(response, default=datetime_handler)
	else:
		return redirect(url_for('login'))


@app.route("/api/asg/detachinstance/<instance>")
def detach_instance(instance):
	if 'logged_in' in session:
		asgid = request.args.get('asgid')

		client = boto3.client('autoscaling', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])
		response =client.detach_instances(  InstanceIds=[ instance ],AutoScalingGroupName=asgid, ShouldDecrementDesiredCapacity=True )
		
		return json.dumps(response, default=datetime_handler)
	else:
		return redirect(url_for('login'))

@app.route("/api/metrics")
def get_metrics():
	if 'logged_in' in session:
		from datetime import date, datetime

		client = boto3.client('cloudwatch', region_name='us-west-1', aws_access_key_id=cfg['aws_access_key_id'], aws_secret_access_key=cfg['aws_secret_access_key'])

		metric = request.args.get('metric')
		asgid = request.args.get('asgid')
		period = request.args.get('period')

		response = client.get_metric_statistics(
			Namespace='AWS/AutoScaling',
			MetricName=metric,
			Dimensions=[
				{
					'Name': 'AutoScalingGroupName',
					'Value': asgid
				},
			],
			StartTime=datetime(2017, 1, 14, 0, 0, 0),
			EndTime=datetime(2017, 1, 15, 23, 59, 59),
			Period=int(period),
			Statistics=[
				'Average'
			],
			Unit='None'
		)

		return json.dumps(response, default=datetime_handler)
	else:
		return redirect(url_for('login'))


#	return send_from_directory(os.path.join(app.root_path, 'static'), 'metrics.json', mimetype='application/json')
	
@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static/img'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
	cfg = config.params['ignite']
	app.secret_key = os.urandom(12)
	app.run(debug=True)
	#app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='img/favicon.ico'))


