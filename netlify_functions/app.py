from ov_crawl.app import app as ov_crawl_app
from flask import request
import json

def handler(event, context):
    headers = event.get("headers")
    path = event.get("path")
    query_string = event.get("queryStringParameters")
    http_method = event.get("httpMethod")

    with ov_crawl_app.test_request_context(
        path=path, base_url="http://localhost/", query_string=query_string, method=http_method
    ):
        ov_crawl_app.preprocess_request()
        response = ov_crawl_app.full_dispatch_request()
        body = json.dumps(response.get_json())

        return {
            "statusCode": response.status_code,
            "headers": {"Content-Type": "application/json"},
            "body":  body
    }