import json
import os
import sys
import time

import boto3
import click

PRL_PATH = os.path.expanduser("~/.prl")
CREDS_PATH = os.path.join(PRL_PATH, "creds.json")
PLAYGROUND_ENV = os.getenv("PLAYGROUND_ENV")

DEFAULT_REGION = "us-east-1"


def get_client_id(in_europe: bool, using_api_key: bool):
    if using_api_key:
        if in_europe:
            return "6cv1hchrihac7dtsmjac1dukn6"
        elif PLAYGROUND_ENV in ["LOCAL", "DEV"]:
            return "7scu563gabte768gtml5v5uids"
        else:
            # Normal Prod user pool
            return "6t1s1a2g43ggqkn8timajdl0nn"
    else:
        if in_europe:
            return "4asi3qr1jga1l1kvc6cqpqdsad"
        elif PLAYGROUND_ENV in ["LOCAL", "DEV"]:
            return "59blf1klr2lejsd3uanpk3b0r4"
        else:
            # Normal Prod user pool
            return "7r5tn1kic6i262mv86g6etn3oj"


def get_region():
    if "PRL_REGION" in os.environ:
        return os.environ["PRL_REGION"]

    if os.path.exists(CREDS_PATH):
        with open(CREDS_PATH, "r") as f:
            auth_dict = json.load(f)

        if "region" in auth_dict:
            return auth_dict["region"]

    return DEFAULT_REGION


def get_auth_token():
    if not os.path.exists(CREDS_PATH):
        auth_dict = {}
    else:
        with open(CREDS_PATH, "r") as f:
            auth_dict = json.load(f)

    if "PRL_REGION" in os.environ:
        region_name = os.environ["PRL_REGION"]
    elif "region" in auth_dict:
        region_name = auth_dict["region"]
    else:
        region_name = DEFAULT_REGION

    client = boto3.client("cognito-idp", region_name=region_name)

    if "access_expiry" not in auth_dict or time.time() > auth_dict["access_expiry"]:
        # API Key is specified in environment
        if "PRL_API_KEY" in os.environ:
            refresh_token = os.environ["PRL_API_KEY"]
            client_id = get_client_id(region_name == "eu-north-1", True)
        # We're using the prl login workflow.
        elif "refresh_token" in auth_dict:
            refresh_token = auth_dict["refresh_token"]
            client_id = auth_dict["client_id"]
        # No refresh token, so not logged in
        else:
            click.echo("Not authenticated. Run the command: prl login.")

        # If enough time has elapsed, we need to refresh the token
        try:
            response = client.initiate_auth(
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={"REFRESH_TOKEN": refresh_token},
                ClientId=client_id,
            )
        except Exception as e:
            click.echo(
                "Either your session has expired or an invalid API Key was provided. Run prl login, or update your PRL_API_KEY environment variable."
            )
            sys.exit()

        auth_dict = {
            **auth_dict,
            "access_token": response["AuthenticationResult"]["AccessToken"],
            "id_token": response["AuthenticationResult"]["IdToken"],
            "access_expiry": int(
                time.time() + response["AuthenticationResult"]["ExpiresIn"] - 10
            ),
        }
        auth_json = json.dumps(auth_dict, indent="\t")

        if not os.path.exists(PRL_PATH):
            os.makedirs(PRL_PATH, mode=0o770)

        # Store the new access token
        with open(CREDS_PATH, "w") as f:
            os.chmod(CREDS_PATH, mode=0o770)
            f.write(auth_json)

    return auth_dict["access_token"]
