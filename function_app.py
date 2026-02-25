import azure.functions as func
import json
from agent import chat

app = func.FunctionApp()


@app.route(route="chat", methods=["POST"])
def chat_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body", status_code=400)

    message = body.get("message")
    if not message:
        return func.HttpResponse("Missing 'message' field", status_code=400)

    response = chat(message)
    return func.HttpResponse(
        json.dumps({"response": response}),
        mimetype="application/json"
    )
