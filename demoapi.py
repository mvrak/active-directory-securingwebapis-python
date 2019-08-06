import flask
from jose import jwt

app = flask.Flask(__name__)
app.config["DEBUG"] = True

API_AUDIENCE = "<api_audience>"
TENANT_ID = "<tenant_id>"

@app.route('/', methods=['GET'])
def home():
    return "test1234"

app.run() 
