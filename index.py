def handler(event, context):
    response = {
        'statusCode': 200,
        'body': 'Hello from Lambda for python!'
    }
    return response