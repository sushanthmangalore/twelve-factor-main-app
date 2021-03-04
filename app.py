import os

from config_helper import AppConfigHelper

from flask import Flask
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

appconfig = AppConfigHelper(
    os.environ['ConfigApp'],
    os.environ['ConfigEnv'],
    os.environ['ConfigProfile'],
    3600,  # Auto refresh config every 1 hour
    os.environ['ConfigClient']
)


@app.route('/')
def health():
    return "All good !"


@app.route('/hello')
def hello_world():
    """
    Display hello message using the information from the Dynamo table
    """
    ddb_client = boto3.client(
        'dynamodb', region_name=os.environ['AWS_DEFAULT_REGION'])
    TABLE_NAME = get_table_name()
    try:
        response = ddb_client.get_item(
            TableName=TABLE_NAME, Key={'Application': {'S': 'TwelveFactorApp'}})
        return f"Hello from {response['Item']['Name']['S']}. Developed with
        {response['Item']['Language']['S']}, deployed with {response['Item']['Platform']['S']}"
    except ClientError as e:
        return response['Error']['Message']


def get_table_name():
    appconfig.update_config()
    return appconfig.config["TableName"]


@app.route('/table-name')
def table_name():
    """
     Return table name using API
    """
    return get_table_name()


@app.route('/refresh-config')
def refresh():
    """
     Force refresh config using the API endpoint
    """
    result = "Config Refreshed" if appconfig.update_config(
        force=True) else "Nothing to refresh"
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
