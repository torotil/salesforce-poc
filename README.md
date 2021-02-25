# Salesforce integration POC

Proof of concept implementation for a simple Salesforce integration that runs offline using the
JWT bearer token flow.

## Prerequisites

1. Create a new app in salesforce and copy its consumer key and secret into a copy of `config.yaml.example`.
2. Create a RSA key as described in this blogpost https://mannharleen.github.io/2020-03-03-salesforce-jwt/.
   The examples below assume that your private key is stored in `salesforce.key`. 

## Usage

### First time authentication

The first time you need to authenticate using your browser:

```bash
sf-poc oauth2 request-authorization-code
```

Open the link in your browser. Once you have authorized the app copy the code and execute:

```bash
sf-poc oauth2 request-token AUTHORIZATION_CODE
```

After this you can proceed by getting a bearer token.

### Getting a bearer token

```bash
sf-poc oauth2 get-token salesforce.key USER_EMAIL > token.json
```

### Using the client

Once you have a valid token you can start an interactive python shell by running

```bash
sf-poc client
```

The client is authenticated already and uses the [requests]() library to do requests.

Example for looking up a contact by email and getting all its details (assuming there is
exactly one such contact).

```python
response = client.get("query", {"q": "SELECT Id FROM Contact WHERE Email = 'test@example.com'")
response = self.get(path=response.json()["records"][0]["attributes"]["url"])
print(response.json())
```
