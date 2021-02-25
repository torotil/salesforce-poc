"""Define commands for the cli tool."""

import datetime
import json
import time
import urllib.parse

import click
import IPython.terminal.embed
import jwt
import requests
import yaml

from salesforce_poc.client import Client


@click.group()
def cli():
    pass


@cli.group()
@click.option("--config-yaml", type=click.File("r"), default="config.yaml")
@click.pass_context
def oauth2(ctx, config_yaml):
    """OAuth2 authentication sub-commands."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = yaml.full_load(config_yaml)
    subdomain = "test" if ctx.obj.get("test", False) else "login"
    ctx.obj["login_host"] = f"{subdomain}.salesforce.com"


@oauth2.command()
@click.pass_context
def request_authorization_code(ctx, test=False):
    """Send a OAuth2 authorization code request."""
    params = {
        "client_id": ctx.obj["config"]["client_id"],
        "redirect_uri": ctx.obj["config"]["redirect_uri"],
        "response_type": "code",
    }
    click.echo("Please go to the following URL and then authenticate the app.")
    click.echo("")
    url = "https://" + ctx.obj["login_host"] + "/services/oauth2/authorize?"
    click.echo(url + urllib.parse.urlencode(params))
    click.echo("")
    click.echo(
        "Once you have been redirected back please copy&paste the authorization code provided."
    )


@oauth2.command()
@click.argument("authorization_code")
@click.pass_context
def request_token(ctx, authorization_code, test=False):
    """Authorize using the authentication code."""
    params = {
        "client_id": ctx.obj["config"]["client_id"],
        "client_secret": ctx.obj["config"]["client_secret"],
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": ctx.obj["config"]["redirect_uri"],
    }
    url = "https://" + ctx.obj["login_host"] + "/services/oauth2/token"
    response = requests.get(url, params=params)
    click.echo(response)


@oauth2.command()
@click.argument("key_file", type=click.File("r"))
@click.argument("user")
@click.pass_context
def get_token(ctx, key_file, user, test=False):
    private_key = key_file.read()
    claim = {
        "iss": ctx.obj["config"]["client_id"],
        "exp": int(time.time()) + 300,
        "aud": ctx.obj["login_host"],
        "sub": user,
    }
    assertion = jwt.encode(claim, private_key, algorithm="RS256", headers={"alg": "RS256"})
    response = requests.post(
        "https://" + ctx.obj["login_host"] + "/services/oauth2/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        },
    )
    click.echo(response.text)


@cli.command()
@click.option("--token-file", type=click.File("r"), default="token.json")
def client(token_file):
    """Enter an interactive shell to work with the client."""
    token_response = json.load(token_file)
    client = Client(token_response["instance_url"], token_response["access_token"])
    IPython.terminal.embed.embed()
