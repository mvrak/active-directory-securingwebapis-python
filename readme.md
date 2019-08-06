---
services: active-directory
platforms: python, js
author: amikuma
level: 100
client: Python Web Api
service: Microsoft Graph
endpoint: AAD v2.0
---

# Securing Web APIs and microservices with Python

## About this sample

### Overview

This sample demonstrates how to build a secure Python web API with a minimal python webapp + /JS frontend and a minimal upstream service.  

1. The html/js frontend uses the MSAL.JS library (OAuth2 Implicit flow) to acquire a JWT access token.  
2. The html/js frontend sends the token to the Python web API.  
3. We display confirmation in the frontend that the web API was able to receive and read the secured token.
4. We display confirmation that the web API was able to further call the upstream service using an OBO (on behalf of) flow.

## How to run this sample

To run this sample, you'll need:

- [Python 3+](https://www.python.org/downloads/release/python-364/)
- [An Azure AD tenant](https://azure.microsoft.com/en-us/documentation/articles/active-directory-howto-tenant/)
- [An Azure AD user](https://docs.microsoft.com/en-us/azure/active-directory/add-users-azure-active-directory).

### Step 1.  Register the client app 

1. Go to https://portal.azure.com and log in.
1. Click "Azure Active Directory" on the left side.
1. Click "App Registrations" on the next blade.
	- [Shortcut](https://go.microsoft.com/fwlink/?linkid=2083908)
1. Select **New registration**.
1. Select an name for your app.  
1. For supported account types, select the third option, "All AAD + Personal Accounts".  
	- Read through the "Help me choose" documentation for any questions.
1. Set a redirect URI of http://localhost:30226 of type "Web"
1. Select **Register** to create the application.
1. You will be on the**Overview** page. Find the **Application (client) ID** value.  Copy this and keep it available.
1. While you are here, grab your ***Tenant ID*** also.
1. From the app's Overview page, select the **Authentication** section.
1. In the **Advanced settings** | **Implicit grant** section, check **Access Tokens** and **ID tokens**.  For more information read [Implicit grant flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-implicit-grant-flow).
1. Select **Save**.

### Step 2.  Generate the Secret
1. From the **Certificates & secrets** page, in the **Client secrets** section, choose **New client secret**:

   - Type a key description (of instance `app secret`),
   - Select a key duration of **Never Expires**.
   - When you press the **Add** button, the key value will be displayed
   - Save the value in a safe location right now.  You will not be able to retrieve this later.

1. Select the **API permissions** section
   - Click the **Add a permission** button and then,
   - Ensure that the **Microsoft APIs** tab is selected
   - In the *Commonly used Microsoft APIs* section, click on **Microsoft Graph**
   - In the **Delegated permissions** section, ensure that the right permissions are checked: **User.Read**. Use the search box if necessary.
   - Select the **Add permissions** button

### Step 3:  Configure your local test interface

To test locally and acquire the right tokens, you will need html/js UX, and a webhost.  We provide a minimal python webhost.

#### Configure the web host

1.  Download the provided demohost.py or copypaste the following code:

```python
import http.server
import socketserver

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", 30662), Handler) as httpd:
    httpd.serve_forever()
```
	
Note that the port is 30662.  You may modify this, but it must match the Redirect URI configured in the app registration.

By default, navigating to root `/` will call for index.html, or display a directory listing.  We will use index.html for ease of use.

#### Set up the local interface

1.  Download the provided index.html
1.  Add the CDN for MSAL JS within the html `<head>` element
```html
<script src="https://secure.aadcdn.microsoftonline-p.com/lib/1.0.0/js/msal.js"></script>
```

1.  Add the following code to configure the necessary parts of MSAL JS.  You can add this at the beginning of the `<script>` section within `<body>`.

``` javascript
   var msalConfig = {
        auth: {
            clientId: '<application id>', //This is the Application (Client) ID you saved from above
            authority: "https://login.microsoftonline.com/common"
        },
        cache: {
            cacheLocation: "localStorage",
            storeAuthStateInCookie: true
        }
    };
```

1.  This index.html provides minimal html and JS needed to invoke the sign-in call.

### Step 4. Run the sample

1.  Open up a shell and switch to the local directory that contains your demohost.py and index.html.
1.  Run the demohost:  `python demohost.py`
1.  Browse to [localhost](http://localhost:30662) 
1.  Rejoice, basic auth has succeeded.  **Milestone 1**

### Step 5.  Configuring the Web API

Now we will build a minimal secure web API with Python 

1.	If you need flask or pip, open an Administrator Command Prompt
1.  Install flask:  `pip install flask`
	- Flask provides simpler and more manageable code to respond to web requests
1.  Install jose:  `pip install jose`
	- Jose provides cryptographic functions
	- Pip should be available in the scripts folder within your Python installation.
1.  Start a new python file: `demoapi.py`
1.  Configure the boilerplate Flask api structure:
```python
import flask

app = flask.Flask(__name__)
app.config["DEBUG"] = True
@app.route('/', methods=['GET'])
def home():
    return "test"
app.run()
```


1.  Add an import for the crypto package `import jose`
1.  Set variables for API Audience and Tenant ID

```python
API_AUDIENCE = "<api_audience>"
TENANT_ID = "<tenant_id>"
```

1.  Add a new route to process the API request:

```python
@app.route('/api', methods=['GET'])
def apiresponse():
    return "" 
```

1. Retrieve public certs for your Tenant for Validation
`jsonurl = urlopen("https://login.microsoftonline.com/" +
                            TENANT_ID + "/discovery/v2.0/keys")`
							
1.  Get the Token from the http header:
`token = get_token_auth_header()`

```python
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
```

1.  Find the matching cert
```python
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
```

1.  Decode the JWT
```python
payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=API_AUDIENCE,
                    issuer="https://sts.windows.net/" + TENANT_ID + "/"
                )
```

1.  Return JWT details for clientside verification
`return payload.current_user`

### Step 6.  Configuring the Client UX to confirm the response

### Step 7.  Enhance the Web API with an OBO Flow

### Step 8.  Configure the Client UX to confirm the OBO flow success

### Step 9.  Enhance the Web API further


