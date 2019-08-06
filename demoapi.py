from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from urllib.request import urlopen
import json

app = Flask(__name__)
CORS(app)  					#sets an open Cross origin policy for Development purposes
app.config["DEBUG"] = True

secretvalue = "5:CQP6.2R:1AOcedVPQWzIl-n08S=dFR"
#API_AUDIENCE = "9204643c-e631-4cdc-bb2c-bbc883ef1a54" 
API_AUDIENCE = "65250674-7c32-4e98-a20d-86da2f73a22b" 
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47" #Microsoft's Tenant ID
jsonurl = urlopen("https://login.microsoftonline.com/" + TENANT_ID + "/discovery/v2.0/keys")
#https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/discovery/v2.0/keys
def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must start with"
                         " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must be"
                         " Bearer token"}, 401)

    token = parts[1]
    return token

@app.route('/', methods=['GET'])
def home(): 
	#no cors because you are hitting just from browser
	return "Web API online"


	
@app.route('/api/', methods=['GET'])
def apiresponse():
	auth = request.headers.get("Authorization", None)
	if not auth:
		raise AuthError({"code": "authorization_header_missing",
						 "description":
						 "Authorization header is expected"}, 401)
	parts = auth.split()

	if parts[0].lower() != "bearer":
		raise AuthError({"code": "invalid_header",
						 "description":
						 "Authorization header must start with"
						 " Bearer"}, 401)
	elif len(parts) == 1:
		raise AuthError({"code": "invalid_header",
						 "description": "Token not found"}, 401)
	elif len(parts) > 2:
		raise AuthError({"code": "invalid_header",
						 "description":
						 "Authorization header must be"
						 " Bearer token"}, 401)
	token = parts[1]

	jsonurl = urlopen("https://login.microsoftonline.com/" +
					TENANT_ID + "/discovery/v2.0/keys")
	jwks = json.loads(jsonurl.read())
	unverified_header = jwt.get_unverified_header(token)
	rsa_key = {}
	for key in jwks["keys"]:
		if key["kid"] == unverified_header["kid"]:
			rsa_key = {
				"kty": key["kty"],
				"kid": key["kid"],
				"use": key["use"],
				"n": key["n"],
				"e": key["e"]
			}
	try:
		payload = jwt.decode(
					token,
					#verify=False
					rsa_key["n"],
					algorithm=["RS256"],
					audience=API_AUDIENCE,
					issuer="https://sts.windows.net/" + TENANT_ID + "/"
				)
	except:
		print(token)
		return(rsa_key)
	response = jsonify(payload)
	return response

	
app.run() 
