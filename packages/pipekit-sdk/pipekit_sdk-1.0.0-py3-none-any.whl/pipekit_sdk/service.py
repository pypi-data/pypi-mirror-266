import json
import os

# pylint: disable-next=import-error
import requests

# pylint: disable-next=import-error
from hera.workflows import Workflow

# pylint: disable-next=import-error
from hera.workflows.models import WorkflowCreateRequest
from pipekit_sdk.helpers import is_valid_uuid


class PipekitService:
    """
    PipekitService is a wrapper around the Pipekit API.
    It provides a simple interface to interact with Pipekit.
    """

    def __init__(
        self, username="", password="", token="", pipekit_url="https://api.pipekit.io"
    ):
        self.username = username
        self.password = password

        pipekit_url = os.getenv("PIPEKIT_URL", pipekit_url)
        if pipekit_url.endswith("/"):
            pipekit_url = pipekit_url[:-1]

        self.id_url = pipekit_url
        self.users_url = pipekit_url
        self.ui_url = pipekit_url

        if token != "":
            self.access_token = token
            return

        self.__login()

    def __login(self):
        login_request = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
        }

        if "@" in self.username:
            login_request["email"] = self.username
            login_request["username"] = ""

        login_url = f"{self.id_url}/api/id/v1/oauth/token"
        login_response = requests.post(
            login_url,
            data=json.dumps(login_request),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if login_response.status_code // 100 != 2:
            raise Exception(f"Login failed: {login_response.text}")

        self.access_token = login_response.json()["access_token"]

    def get_token(self):
        """
        get_token returns the access token used to authenticate with Pipekit.
        """

        return self.access_token

    def list_clusters(self):
        """
        list_clusters returns a list of clusters.
        """

        clusters_url = f"{self.users_url}/api/users/v1/clusters"
        clusters_response = requests.get(
            clusters_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=10,
        )

        if clusters_response.status_code // 100 != 2:
            raise Exception(f"List clusters failed: {clusters_response.text}")

        return clusters_response.json()

    def list_pipes(self, cluster_uuid=""):
        """
        list_pipes returns a list of pipes.
        """

        page = 1
        limit = 20

        pipes = []
        while True:
            pipes_url = f"{self.users_url}/api/users/v1"
            if cluster_uuid != "":
                pipes_url += f"/clusters/{cluster_uuid}"
            pipes_url += f"/pipes?page={page}&limit={limit}"

            pipes_response = requests.get(
                pipes_url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10,
            )

            if pipes_response.status_code // 100 != 2:
                raise Exception(f"List pipes failed: {pipes_response.text}")

            pipes_page = pipes_response.json()["items"]
            if len(pipes_page) == 0:
                break

            pipes.append(pipes_page)

            if len(pipes_page) < limit:
                break

            page += 1

        return pipes

    def get_pipe(self, pipe_uuid):
        """
        get_pipe returns a pipe.
        """

        pipe_url = f"{self.users_url}/api/users/v1/pipes/{pipe_uuid}"
        pipe_response = requests.get(
            pipe_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=10,
        )

        if pipe_response.status_code // 100 != 2:
            raise Exception(f"Get pipe failed: {pipe_response.text}")

        return pipe_response.json()

    def list_runs_by_cluster(self, cluster_uuid, status=""):
        """
        list_runs_by_cluster returns a list of runs for a cluster.
        """

        page = 1
        limit = 20

        base_url = f"{self.users_url}/api/users/v1/clusters/{cluster_uuid}/runs"
        runs = []
        while True:
            runs_url = f"{base_url}?page={page}&limit={limit}&status={status}"

            runs_response = requests.get(
                runs_url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10,
            )

            if runs_response.status_code // 100 != 2:
                raise Exception(f"List runs failed: {runs_response.text}")

            runs_page = runs_response.json()["items"]
            if len(runs_page) == 0:
                break

            runs.append(runs_page)

            if len(runs_page) < limit:
                break

            page += 1

        return runs

    def list_runs_by_pipe(self, pipe_uuid, status=""):
        """
        list_runs_by_pipe returns a list of runs for a pipe.
        """

        page = 1
        limit = 20

        base_url = f"{self.users_url}/api/users/v1/pipes/{pipe_uuid}/runs"
        runs = []
        while True:
            runs_url = f"{base_url}?page={page}&limit={limit}&status={status}"

            runs_response = requests.get(
                runs_url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10,
            )

            if runs_response.status_code // 100 != 2:
                raise Exception(f"List runs failed: {runs_response.text}")

            runs_page = runs_response.json()["items"]
            if len(runs_page) == 0:
                break

            runs.append(runs_page)

            if len(runs_page) < limit:
                break

            page += 1

        return runs

    def get_run(self, run_uuid):
        """
        get_run returns a run.
        """

        run_url = f"{self.users_url}/api/users/v1/runs/{run_uuid}"
        run_response = requests.get(
            run_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=10,
        )

        if run_response.status_code // 100 != 2:
            raise Exception(f"Get run failed: {run_response.text}")

        return run_response.json()

    def get_cluster(self, cluster_uuid):
        """
        get_cluster returns a cluster.
        """

        cluster_url = f"{self.users_url}/api/users/v1/clusters/{cluster_uuid}"
        cluster_response = requests.get(
            cluster_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=10,
        )

        if cluster_response.status_code // 100 != 2:
            raise Exception(f"Get cluster failed: {cluster_response.text}")

        return cluster_response.json()

    def get_cluster_by_name(self, cluster_name):
        """
        get_cluster_by_name returns a cluster by name.
        """

        clusters = self.list_clusters()
        for cluster in clusters:
            if cluster["name"] == cluster_name:
                return cluster

        return None

    def submit(self, workflow: Workflow, cluster, pipe_name=""):
        """
        submit submits a workflow to a cluster.
        """

        if not is_valid_uuid(cluster):
            cluster = self.get_cluster_by_name(cluster)["uuid"]

        submit_url = f"{self.users_url}/api/users/v1/clusters/{cluster}/workflows"
        if pipe_name != "":
            submit_url += f"?pipe-name={pipe_name}"

        workflow = WorkflowCreateRequest(workflow=workflow.build()).workflow
        submit_response = requests.post(
            submit_url,
            data=workflow.json(
                exclude_none=True,
                by_alias=True,
                exclude_unset=True,
                exclude_defaults=True,
            ),
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )

        if submit_response.status_code // 100 != 2:
            raise Exception(f"Submit failed: {submit_response.text}")

        return submit_response.json()

    def __apply_run_action(self, run_uuid, action):
        action_url = f"{self.users_url}/api/users/v1/runs/{run_uuid}/workflows/{action}"
        action_response = requests.put(
            action_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )

        if action_response.status_code // 100 != 2:
            raise Exception(f"Action failed: {action_response.text}")

        return action_response.json()

    def restart(self, run_uuid):
        """
        restart restarts a run.
        """

        return self.__apply_run_action(run_uuid, "restart")

    def stop(self, run_uuid):
        """
        stop stops a run.
        """

        return self.__apply_run_action(run_uuid, "stop")

    def terminate(self, run_uuid):
        """
        terminate terminates a run.
        """

        return self.__apply_run_action(run_uuid, "terminate")

    def __get_run_container_logs(self, run_uuid, pod_name="", container_name=""):
        logs_url = f"{self.users_url}/api/users/v1/runs/{run_uuid}/container_logs?pod-name={pod_name}&container-name={container_name}"

        logs_response = requests.get(
            logs_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=10,
        )

        if logs_response.status_code // 100 != 2:
            raise Exception(f"Get logs failed: {logs_response.text}")

        return logs_response.json()

    def __get_logs_stream(
        self, run_uuid, pod_name="", container_name="", last_event_id=""
    ):
        logs_url = f"{self.users_url}/api/users/v1/runs/{run_uuid}/container_logs_stream?pod-name={pod_name}&container-name={container_name}"

        logs_response = requests.get(
            logs_url,
            stream=True,
            timeout=None,  # nosec B113
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "last-event-id": last_event_id,
            },
        )

        if logs_response.status_code // 100 != 2:
            raise Exception(f"Get logs stream failed: {logs_response.text}")

        return logs_response

    def get_logs(self, run_uuid, pod_name="", container_name=""):
        """
        get_logs returns pod logs for a given run.
        """

        return self.__get_run_container_logs(run_uuid, pod_name, container_name)

    def follow_logs(self, run_uuid, pod_name="", container_name=""):
        """
        follow_logs returns a generator that yields pod logs for a given run.
        """

        data_msg_prefix = "data: "
        id_msg_prefix = "id: "
        ping_msg = "ping"
        close_msg = "close"
        last_event_id = ""

        while True:
            try:
                logs_stream = self.__get_logs_stream(
                    run_uuid, pod_name, container_name, last_event_id
                )
                for line in logs_stream.iter_lines(delimiter="\n", decode_unicode=True):
                    line = line.strip()

                    if line == "":
                        continue

                    if line.startswith(data_msg_prefix):
                        # strip the prefix
                        line = line[len(data_msg_prefix) :]
                    elif line.startswith(id_msg_prefix):
                        last_event_id = line[len(id_msg_prefix) :]
                        continue
                    else:
                        print(f"unknown message: {line}")
                        continue

                    if line == ping_msg:
                        # pong
                        continue
                    elif line == close_msg:
                        # bye
                        return
                    else:
                        yield json.loads(line)

            except requests.exceptions.Timeout:
                pass  # we'll ignore timeout errors and reconnect

    def __print_log_message(self, line):
        print(f"[{line['podName']}][{line['containerName']}] {line['output']}")

    def print_logs(self, run_uuid, pod_name="", container_name="", follow=True):
        """
        print_logs prints pod logs for a given run.
        """

        if follow:
            for line in self.follow_logs(
                run_uuid, pod_name=pod_name, container_name=container_name
            ):
                self.__print_log_message(line)

        for line in self.get_logs(
            run_uuid, pod_name=pod_name, container_name=container_name
        ):
            self.__print_log_message(line)
