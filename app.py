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
    3600,
    os.environ['ConfigClient']
)


@app.route('/')
def hello_world():
    ddb_client = boto3.client('dynamodb',
                              region_name=os.environ['AWS_DEFAULT_REGION'])
    TABLE_NAME = get_table_name()
    try:
        response = ddb_client.get_item(
            TableName=TABLE_NAME, Key={'Application': {'S': 'TwelveFactorApp'}})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return f"Hello from {response['Item']['Name']['S']}"


def get_table_name():
    appconfig.update_config()
    return appconfig.config["TableName"]

@app.route('/refresh-config')
def refresh():
    result = "Config Refreshed" if appconfig.update_config(force=True) else "Nothing to refresh"
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
