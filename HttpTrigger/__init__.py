import logging
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        key = req.params.get('key')
        if not key:
            return func.HttpResponse(
                "Please pass a key in the query string",
                status_code=400
            )

        data = req.get_json()
        value = data.get(key)

        if not value:
            return func.HttpResponse(
                f"Key '{key}' not found in JSON data",
                status_code=400
            )

        return func.HttpResponse(value)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(
            "An error occurred while processing the request",
            status_code=500
        )