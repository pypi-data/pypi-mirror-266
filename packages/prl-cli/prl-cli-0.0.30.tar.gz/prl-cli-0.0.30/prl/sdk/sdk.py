from functools import wraps
from time import time
from typing import Callable

import attrs
import click
from openai import OpenAI
from prl.cli.suite import pull_suite, update_suite
from prl.sdk.run import get_run_url, start_run
from tqdm import tqdm

in_tokens = 0
out_tokens = 0


def parse_test_suite_id_from_url(test_suite_url: str) -> str:
    start_index = test_suite_url.find("test_suite_id=") + len("test_suite_id=")
    return test_suite_url[start_index:]


def run_evaluations(
    test_suite_url: str,
    generate_fn: Callable[[str], str],
    description="Ran automatically using the PRL SDK",
    maximum_threads=4,
    verbosity=1,
    model_under_test="sdk",
    **kwargs
):
    test_suite_id = parse_test_suite_id_from_url(test_suite_url)

    suite_data = pull_suite(test_suite_id, include_id=True)

    if verbosity == 0:
        iterator = suite_data["tests"]
    else:
        iterator = tqdm(suite_data["tests"])

    global in_tokens, out_tokens
    metadata = {}
    for test in iterator:
        start = time()
        test["fixed_output"] = generate_fn(test["input_under_test"], **kwargs)
        end = time()
        metadata[test["id"]] = {
            "in_tokens": in_tokens,
            "out_tokens": out_tokens,
            "duration_seconds": end - start,
        }
        in_tokens = 0
        out_tokens = 0

    update_suite(test_suite_id, suite_data)
    run_id = start_run(
        test_suite_id,
        {
            "use_fixed_output": True,
            "description": description,
            "maximum_threads": maximum_threads,
            "model_under_test": model_under_test,
            **kwargs,
        },
        metadata_map=metadata,
    )
    run_url = get_run_url(run_id)

    if verbosity >= 1:
        click.secho(
            "Successfully updated test suite with new fixed outputs and started a new run.",
            fg="green",
        )
        click.secho(run_url, bold=True)

    return run_id


def wrap_chatcompletion(func: Callable):
    @wraps(func)
    def wrapper(**kwargs):
        response = func(**kwargs)
        global in_tokens, out_tokens

        in_tokens += response.usage.prompt_tokens
        out_tokens += response.usage.completion_tokens

        return response

    return wrapper


# External Facing
def patch(client: OpenAI):
    client.chat.completions.create = wrap_chatcompletion(client.chat.completions.create)
    return client
