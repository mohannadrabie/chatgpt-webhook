import base64
import os
import openai
import json
import boto3
import re
import pytoml as toml


# This function is the main function of the AWS Lambda function. It is called when a POST request is made to the API Gateway endpoint.
def lambda_handler(event, context):
    openai.api_key =  get_secret()
    request_body = parse_results(event)
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=request_body,
        max_tokens=100,
        temperature=0.8,
        top_p=1,
        n=1
    )
    message = response.choices[0].text
    result = message.strip()
    return {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": result,
        "headers": {
        "content-type": "application/json"
  }
}
    

    # Code to hide credentials in a string
    # string is a string that may contain credentials
    # returns string with all credentials hidden
def hide_credentials(string):
    s3 = boto3.resource('s3')
    # read the toml configuration file from S3
    obj = s3.Object('chatgpt-webhook', 'gitleaks.toml')
    config = obj.get()['Body'].read().decode('utf-8')
    parsed_toml = toml.loads(config)
    #Loop through all the rules
    for ruleconfig in parsed_toml['rules']:
         pattern = re.compile(ruleconfig["regex"])
         if pattern.search(string):
            string = re.sub(pattern, "***Hidden sensitive information***", string)
          
    return string


# This function gets the secret string from AWS Secrets Manager
# The secret string contains the OpenAI API key
def get_secret():
    secret_name = "openai-key"
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    return secret


# This code takes an event and parses the response body. It returns the body with the credentials hidden.
def parse_results(event) -> list[dict]:
    # Extract the body of the event
    requestevent = json.dumps( event )
    body = json.loads(
        requestevent)
    # Hide credentials in the body
    return hide_credentials(body["body"])