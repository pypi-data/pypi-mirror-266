import json
import os
import time

import boto3
import click
from prl.sdk.auth import CREDS_PATH, PRL_PATH, get_client_id


@click.command(name="login")
def login_command():
    """
    Authenticate with PlaygroundRL CLI
    """
    in_eu = click.confirm("Are you located in Europe?")
    region = "eu-north-1" if in_eu else "us-east-1"
    username = click.prompt("email")
    password = click.prompt("password", hide_input=True)

    client_id = get_client_id(in_eu, False)

    client = boto3.client("cognito-idp", region_name=region)

    # TODO: Error handling
    response = client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientId=client_id,
    )

    auth_dict = {
        "refresh_token": response["AuthenticationResult"]["RefreshToken"],
        "access_token": response["AuthenticationResult"]["AccessToken"],
        "id_token": response["AuthenticationResult"]["IdToken"],
        "client_id": client_id,
        "region": region,
        "access_expiry": int(
            time.time() + response["AuthenticationResult"]["ExpiresIn"] - 10
        ),
    }
    auth_json = json.dumps(auth_dict, indent="\t")

    if not os.path.exists(PRL_PATH):
        os.makedirs(PRL_PATH)
        os.chmod(PRL_PATH, mode=0o770)

    with open(CREDS_PATH, "w") as f:
        os.chmod(CREDS_PATH, mode=0o770)
        f.write(auth_json)
