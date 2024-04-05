# Copyright 2023 Iguazio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import random
import string
import time
import traceback
import typing
import uuid

import igz_mgmt.constants

# lazy load namespace resolution
_running_namespace = None


def url_join(base, *parts):
    result = base

    if result[0] != "/":
        result = "/" + base

    for part in parts:
        if part[0] != "/":
            result += "/" + part
        else:
            result += part

    return result


class RetryUntilSuccessfulInProgressErrorMessage(Exception):
    def __init__(self, message, *, variables=None):
        super().__init__(message)
        self.variables = variables if variables else {}
        self.message = message


class RetryUntilSuccessfulFatalError(Exception):
    def __init__(self, message, *, caused_by_exc=None):
        super().__init__(message)
        self.message = message

        # the exception that caused the fatal error
        self.caused_by_exc = caused_by_exc


def create_linear_backoff(base=2, coefficient=2, stop_value=120):
    """Create a generator of linear backoff. Check out usage example in test_helpers.py."""
    x = 0
    comparison = min if coefficient >= 0 else max

    while True:
        next_value = comparison(base + x * coefficient, stop_value)
        yield next_value
        x += 1


def retry_until_successful(
    backoff: typing.Union[int, float],
    timeout: int,
    logger,
    verbose: bool,
    function,
    *args,
    **kwargs,
):
    """Runs function with given *args and **kwargs.

    Tries to run it until success or timeout reached.

    Args:
        backoff: can either be a:
            1. number (int / float) that will be used as interval.
            2. generator of waiting intervals. (support next()).
        timeout (int): Pass None if timeout is not wanted, number of seconds if it is.
        logger: A logger so we can log the failures.
        verbose (bool): Whether to log the failure on each retry.
        function: Function to run.
        **args: Functions args.
        **kwargs: Functions kwargs.

    Returns:
        Function result.
    """
    start_time = time.time()
    last_traceback = None
    last_exception = None
    function_name = function.__name__

    # Check if backoff is just a simple interval
    if isinstance(backoff, int) or isinstance(backoff, float):
        backoff = create_linear_backoff(base=backoff, coefficient=0)

    # If deadline was not provided or deadline not reached
    while timeout is None or time.time() < start_time + timeout:
        next_interval = next(backoff)
        try:
            # TODO: await if function is async (asyncio.iscoroutinefunction(function))
            results = function(*args, **kwargs)
            return results
        except RetryUntilSuccessfulFatalError as exc:
            if logger is not None and verbose:
                logger.debug_with(
                    "Fatal error occurred while running, stop retrying",
                    function_name=function_name,
                    exc=exc,
                )
            # raise the exception that caused the fatal error (if exists) or the fatal error itself
            raise exc.caused_by_exc or exc

        except Exception as exc:
            if logger is not None and verbose:
                log_kwargs = {
                    "next_try_in": next_interval,
                    "function_name": function_name,
                }
                if isinstance(exc, RetryUntilSuccessfulInProgressErrorMessage):
                    log_kwargs.update(exc.variables)

                logger.debug_with(
                    # sometimes the exception do not have a message, return the class name instead
                    str(exc) or repr(exc),
                    **log_kwargs,
                )

            last_exception = exc
            last_traceback = traceback.format_exc()

            # If next interval is within allowed time period - wait on interval, abort otherwise
            if timeout is None or time.time() + next_interval < start_time + timeout:
                time.sleep(next_interval)
            else:
                break

    if logger is not None:
        logger.warn_with(
            "Operation did not complete on time",
            function_name=function_name,
            timeout=timeout,
            exc=str(last_exception),
            tb=last_traceback,
        )

    raise Exception(
        f"failed to execute command by the given deadline."
        f" last_exception: {last_exception},"
        f" function_name: {function.__name__},"
        f" timeout: {timeout}"
    )


def random_string(length: int) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def get_endpoint(endpoint, default_scheme="http"):
    """Get the endpoint scheme and host."""
    if not endpoint:
        if running_in_k8s():
            endpoint = f"datanode-dashboard.{get_running_namespace()}.svc.cluster.local"

        if not endpoint:
            raise RuntimeError(
                "Endpoint must be passed when running externally to Kubernetes"
            )

    if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
        endpoint = f"{default_scheme}://{endpoint}"

    return endpoint.rstrip("/")


def running_in_k8s():
    """Some indicators that we're running in k8s."""
    return (
        env_is_set("KUBERNETES_SERVICE_HOST")
        and env_is_set("KUBERNETES_SERVICE_PORT")
        and os.path.isfile("/var/run/secrets/kubernetes.io/serviceaccount/token")
        and os.path.isfile("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
    )


def get_running_namespace():
    """Get the namespace we're running in."""
    global _running_namespace
    if _running_namespace:
        return _running_namespace
    if running_in_k8s():
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as f:
            _running_namespace = f.read().strip()
    return _running_namespace


def env_is_set(env_var):
    """Check if an environment variable is set and not empty."""
    return os.getenv(env_var) is not None and os.getenv(env_var) != ""


def get_highest_role(role1, role2):
    """Get the highest role between two roles."""
    if not (role1 and role2):
        return role1 or role2
    role_index = min(
        igz_mgmt.constants.ROLE_ORDER.index(role1),
        igz_mgmt.constants.ROLE_ORDER.index(role2),
    )
    return igz_mgmt.constants.ROLE_ORDER[role_index]


def is_uuid4(s):
    try:
        uuid.UUID(s, version=4)
        return True
    except ValueError:
        return False
