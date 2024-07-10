# Terraform Project to Setup API Gateway with Lambda Functions

This project uses Terraform to create an AWS API Gateway that exposes an API endpoint. The endpoint can handle both GET and POST requests, triggering corresponding AWS Lambda functions written in Python.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) installed
- AWS CLI configured with appropriate credentials
- Zip utility to package Lambda functions

## Setup Instructions

### Step 1: Create Python Lambda Functions

Create two Python files, `index.py` and `post_index.py`, for handling GET and POST requests respectively.

#### `index.py`

```python
def handler(event, context):
response = {
'statusCode': 200,
'body': 'Hello from Lambda!'
}
return response
```

#### `post_index.py`

```python
import json

def handler(event, context):
request_body = json.loads(event['body'])
response = {
'statusCode': 200,
'body': json.dumps({
'message': 'Request received',
'data': request_body
})
}
return response
```

### Step 2: Package the Python Lambda Functions

Use the zip utility to package the Lambda functions:

```sh
zip lambda_function_payload.zip index.py
zip post_lambda_function_payload.zip post_index.py
```

### Step 3: Create Terraform Configuration

Create a file named `main.tf` and add the following Terraform configuration:

```hcl
provider "aws" {
region = "us-east-1"
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_execution" {
name = "lambda_execution_role"
assume_role_policy = jsonencode({
Version = "2012-10-17",
Statement = [
{
Action = "sts:AssumeRole",
Effect = "Allow",
Principal = {
Service: "lambda.amazonaws.com"
}
}
]
})
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
role       = aws_iam_role.lambda_execution.name
policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function for GET
resource "aws_lambda_function" "lambda_function" {
filename         = "lambda_function_payload.zip"
function_name    = "MyLambdaFunction"
role             = aws_iam_role.lambda_execution.arn
handler          = "index.handler"
runtime          = "python3.9"
source_code_hash = filebase64sha256("lambda_function_payload.zip")
}

# Lambda Function for POST
resource "aws_lambda_function" "post_lambda_function" {
filename         = "post_lambda_function_payload.zip"
function_name    = "MyPostLambdaFunction"
role             = aws_iam_role.lambda_execution.arn
handler          = "post_index.handler"
runtime          = "python3.9"
source_code_hash = filebase64sha256("post_lambda_function_payload.zip")
}

# API Gateway
resource "aws_api_gateway_rest_api" "api_gateway" {
name        = "MyAPIGateway"
description = "API Gateway to trigger Lambda functions"
}

# API Gateway Resource
resource "aws_api_gateway_resource" "api_gateway_resource" {
rest_api_id = aws_api_gateway_rest_api.api_gateway.id
parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
path_part   = "myresource"
}

# GET Method
resource "aws_api_gateway_method" "api_gateway_get_method" {
rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
resource_id   = aws_api_gateway_resource.api_gateway_resource.id
http_method   = "GET"
authorization = "NONE"
}

# POST Method
resource "aws_api_gateway_method" "api_gateway_post_method" {
rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
resource_id   = aws_api_gateway_resource.api_gateway_resource.id
http_method   = "POST"
authorization = "NONE"
request_parameters = {
"method.request.header.Content-Type" = true
}
}

# Lambda Permission for GET
resource "aws_lambda_permission" "api_gateway_lambda_permission" {
statement_id  = "AllowAPIGatewayInvoke"
action        = "lambda:InvokeFunction"
function_name = aws_lambda_function.lambda_function.function_name
principal     = "apigateway.amazonaws.com"
source_arn    = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
}

# Lambda Permission for POST
resource "aws_lambda_permission" "post_api_gateway_lambda_permission" {
statement_id  = "AllowPostAPIGatewayInvoke"
action        = "lambda:InvokeFunction"
function_name = aws_lambda_function.post_lambda_function.function_name
principal     = "apigateway.amazonaws.com"
source_arn    = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
}

# Integration for GET Method
resource "aws_api_gateway_integration" "api_gateway_get_integration" {
rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
resource_id             = aws_api_gateway_resource.api_gateway_resource.id
http_method             = aws_api_gateway_method.api_gateway_get_method.http_method
type                    = "AWS_PROXY"
integration_http_method = "POST"
uri                     = aws_lambda_function.lambda_function.invoke_arn
}

# Integration for POST Method
resource "aws_api_gateway_integration" "api_gateway_post_integration" {
rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
resource_id             = aws_api_gateway_resource.api_gateway_resource.id
http_method             = aws_api_gateway_method.api_gateway_post_method.http_method
type                    = "AWS_PROXY"
integration_http_method = "POST"
uri                     = aws_lambda_function.post_lambda_function.invoke_arn
}

# Deployment
resource "aws_api_gateway_deployment" "api_gateway_deployment" {
depends_on = [
aws_api_gateway_integration.api_gateway_get_integration,
aws_api_gateway_integration.api_gateway_post_integration
]
rest_api_id = aws_api_gateway_rest_api.api_gateway.id
stage_name  = "prod"
}

# Output the API URL
output "api_url" {
value = "${aws_api_gateway_deployment.api_gateway_deployment.invoke_url}/${aws_api_gateway_resource.api_gateway_resource.path_part}"
}
```

### Step 4: Initialize and Apply Terraform Configuration

Initialize and apply the Terraform configuration:

```sh
terraform init
terraform apply
```

Follow the prompts to apply the changes. Once the process completes, you should see the API URL in the output.

### Step 5: Test the API

#### Testing the GET Method

```sh
curl <api_url>/myresource
```

Replace `<api_url>` with the actual URL provided by Terraform output.

#### Testing the POST Method

```sh
curl -X POST <api_url>/myresource -d '{"key1":"value1", "key2":"value2"}' -H "Content-Type: application/json"
```

Replace `<api_url>` with the actual URL provided by Terraform output.
