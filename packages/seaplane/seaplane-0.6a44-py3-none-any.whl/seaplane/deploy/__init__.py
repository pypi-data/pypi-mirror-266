import json
import os
import shutil
import threading
from typing import Any, Dict, List
from urllib.parse import urlparse

from seaplane.config import config
from seaplane.logs import log
from seaplane.pipes import App, Flow, _DEFAULT_CPU, _DEFAULT_MEM
from seaplane.pipes.debug_schema import write_debug_schema

from .utils import (
    add_secrets,
    create_flow,
    create_store,
    create_stream,
    delete_flow,
    delete_store,
    delete_stream,
    has_store,
    set_key,
    upload_project,
)

"""
Tools for taking a fully constructed Dag / Task complex and deploying it
into the Seaplane infrastructure.

Call `deploy(app, project_directory_name)` to push your application to Seaplane.
"""


SP_UTIL_STORES = ["_SP_REQUEST_", "_SP_RESPONSE_", "_SP_COLLECT_"]
SP_APP_STORE = "_SP_APP_STORE"


class ProcessorInfo:
    """Information about the docker container to run applications"""

    def __init__(self, runner_image: str, runner_args: List[str]):
        self.runner_image = runner_image
        self.runner_args = runner_args


def flow_into_config(flow: Flow, processor_info: ProcessorInfo) -> Dict[str, Any]:
    """Produces JSON.dump-able flow configuration suitable for running the given task"""

    ret: Dict[str, Any] = {
        "processor": {
            "docker": {
                "image": processor_info.runner_image,
                "args": processor_info.runner_args,
            },
        },
        "output": {
            "switch": {
                "cases": [
                    {
                        "check": 'meta("_seaplane_drop") == "True"',
                        "output": {"drop": {}},
                    },
                    {
                        "check": 'meta("_seaplane_drop") != "True"',
                        "output": {
                            "carrier": {
                                "subject": flow.subject.subject_string,
                            }
                        },
                    },
                ]
            }
        },
        "replicas": flow.replicas,
    }

    if len(flow.subscriptions) == 0:
        log.logger.warning(
            f"task {flow.instance_name} does not appear to consume any input, it may not run"
        )

    broker: List[Dict[str, Any]] = []
    for ix, src in enumerate(sorted(flow.subscriptions, key=lambda s: s.filter)):
        # this durable scheme means we're committed to destroying
        # the consumers associated with these flows on redeploy.
        # Future fancy hot-swap / live-update schemes may need
        # to use different durable names

        # using the index of the broker arm is fine for the durable
        # name as carrier generates a durable from this value and
        # the flow name for all pull consumers (which this is)
        durable = str(ix)
        broker.append(
            {
                "carrier": {
                    "ack_wait": f"{flow.ack_wait_secs}s",
                    "bind": True,
                    "deliver": src.deliver,
                    "durable": durable,
                    "stream": src.stream(),
                    "subject": src.filter,
                },
            }
        )

    ret["input"] = {"broker": broker}

    requests: Dict[str, Any] = {}
    if flow.cpu != _DEFAULT_CPU:
        requests["cpu"] = flow.cpu
    if flow.mem != _DEFAULT_MEM:
        requests["memory"] = flow.mem
    if requests:
        ret["processor"]["resources"] = {"requests": requests}

    return ret


def deploy(app: App, project_directory_name: str) -> None:
    """
    Runs a complete deploy of a given app.

    project_directory_name is the name of the directory, a peer to the
    pyproject.toml, that contains

    pyproject = toml.loads(open("pyproject.toml", "r").read())
    project_directory_name = pyproject["tool"]["poetry"]["name"]

    Will delete and recreate a "build" directory

    """
    shutil.rmtree("build/", ignore_errors=True)
    os.makedirs("build")

    project_url = upload_project(project_directory_name)
    processor_info = ProcessorInfo(config.runner_image, [project_url])

    for bucket in app.buckets:
        delete_stream(bucket.notify_subscription.stream())
        create_stream(bucket.notify_subscription.stream())

    # Delete all stores before continuing
    threads = []
    for base_store_name in SP_UTIL_STORES:
        store_name = base_store_name + app.name
        thread = threading.Thread(target=delete_store, args=(store_name,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Create stores
    create_threads = []
    for base_store_name in SP_UTIL_STORES:
        store_name = base_store_name + app.name
        # create_store(store_name, store_config={"replicas": 1})
        thread = threading.Thread(target=create_store, args=(store_name, {"replicas": 1}))
        create_threads.append(thread)
        thread.start()

    # All streams need to be created before any flows,
    # because we may create subscribers to flows before
    # we create publishers.
    threads = []
    for dag in app.dag_registry.values():
        thread = threading.Thread(target=delete_stream, args=(dag.name,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    for dag in app.dag_registry.values():
        thread = threading.Thread(target=create_stream, args=(dag.name,))
        create_threads.append(thread)
        thread.start()

    # Join store and stream creates
    for thread in create_threads:
        thread.join()

    threads = []
    for dag in app.dag_registry.values():
        for task in dag.flow_registry.values():
            thread = threading.Thread(target=delete_flow, args=(task.instance_name,))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    threads = []
    for dag in app.dag_registry.values():
        for task in dag.flow_registry.values():
            new_flow_config = flow_into_config(task, processor_info)
            thread = threading.Thread(
                target=create_flow,
                args=(
                    task.instance_name,
                    new_flow_config,
                ),
            )
            threads.append(thread)
            thread.start()

            secrets = {
                "INSTANCE_NAME": task.instance_name,
                "SEAPLANE_API_KEY": config.get_api_key(),
            }
            thread = threading.Thread(
                target=add_secrets,
                args=(
                    task.instance_name,
                    secrets,
                ),
            )
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    if not has_store(SP_APP_STORE):
        create_store(SP_APP_STORE)

    set_key(SP_APP_STORE, app.name, json.dumps(app.represention()))

    log.logger.info(
        "to write to the application endpoint,\n"
        f"post to https://{urlparse(config.carrier_endpoint).netloc}"
        f"/v1/endpoints/{app.input().endpoint}/request\n"
        "or run: seaplane request -d <data>"
    )

    write_debug_schema(app)


def destroy(app: App) -> None:
    # Destroy all flows before we destroy streams and stores
    threads = []
    for dag in app.dag_registry.values():
        for task in dag.flow_registry.values():
            thread = threading.Thread(target=delete_flow, args=(task.instance_name,))
            threads.append(thread)
            thread.start()
    for thread in threads:
        thread.join()

    # Now destroy all streams and stores and then we're done
    threads = []
    for dag in app.dag_registry.values():
        thread = threading.Thread(target=delete_stream, args=(dag.name,))
        threads.append(thread)
        thread.start()

    for base_store_name in SP_UTIL_STORES:
        store_name = base_store_name + app.name
        thread = threading.Thread(target=delete_store, args=(store_name,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
