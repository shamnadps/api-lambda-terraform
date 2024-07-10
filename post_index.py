import json

def handler(event, context):
    request_body = json.loads(event['body'])
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Request received for python',
            'data': request_body
        })
    }
    return response