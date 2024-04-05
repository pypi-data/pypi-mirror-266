import os

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from .auth import get_auth_token, get_region

PLAYGROUND_ENV = os.getenv("PLAYGROUND_ENV")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "jsonschemas")
SUITE_SCHEMA_PATH = os.path.join(SCHEMA_PATH, "suiteschema.json")
RUN_SCHEMA_PATH = os.path.join(SCHEMA_PATH, "run_params_schema.json")

client_ = None


def be_host():
    region = get_region()
    if region == "eu-north-1":
        return "https://europebe.playgroundrl.com"
    if PLAYGROUND_ENV == "LOCAL":
        return "http://localhost:8000"
    if PLAYGROUND_ENV == "DEV":
        return "https://devbe.playgroundrl.com"

    return "https://prodbe.playgroundrl.com"


def fe_host():
    region = get_region()
    if region == "eu-north-1":
        return "https://eu.playgroundrl.com"
    if PLAYGROUND_ENV == "LOCAL":
        return "http://localhost:3000"
    if PLAYGROUND_ENV == "DEV":
        return "https://dev.playgroundrl.com"

    return "https://playgroundrl.com"


def get_client():
    global client_
    if client_ is None:

        transport = RequestsHTTPTransport(
            url=f"{be_host()}/graphql/",
            headers={"Authorization": get_auth_token()},
            verify=PLAYGROUND_ENV != "LOCAL",
        )
        client_ = Client(transport=transport, fetch_schema_from_transport=True)
    return client_


def list_rag_suites():
    query = gql(
        f"""
        query getRagSuites {{
            ragSuites {{
            id
            org
            path
            query
            }}
            }}
        """
    )
    response = get_client().execute(query)

    # TODO: Error check
    return response["ragSuites"]
