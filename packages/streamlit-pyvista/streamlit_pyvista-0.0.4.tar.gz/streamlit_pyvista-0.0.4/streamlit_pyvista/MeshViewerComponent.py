import os
import time
import logging

import streamlit.components.v1 as components
import requests
import json
import subprocess
import threading

from .utils import is_localhost

root_logger = logging.getLogger("solidipes")
root_logger.propagate = True
root_logger.setLevel(logging.DEBUG)
if "FULL_SOLIDIPES_LOG" not in os.environ:
    root_logger.setLevel(logging.INFO)


class MeshViewerComponent:
    """Streamlit component to display 3d mesh using pyvista and it's Trame backend"""

    def __init__(self, mesh_path: str = None, sequence_size=1, server_url="http://127.0.0.1:8080",
                 setup_endpoint="/init_connection"):

        # Transform the path given as arg to a absolute path to be able to pass it to the server without trouble
        if not os.path.isabs(mesh_path):
            mesh_path = os.getcwd() + "/" + mesh_path

        # Set class attributes and check that files given as input exist all
        self.check_valid_input_files(mesh_path, sequence_size)

        self.mesh_path = mesh_path
        self.sequence_size = sequence_size

        self.width = 1200
        self.height = 900

        self.server_url = server_url
        self.server_timeout = 2
        self.max_retries = 3

        # Set all attribute related to the dynamic endpoints settings.
        # Set the default required endpoints,
        # select mesh is used to ask the server to show a specific mesh and host is the host of the data rendering
        self.required_endpoints = ["select_mesh", "host"]
        # Dict that will contained value received for our endpoints. Init connection is the default endpoint to
        # request the server to give use all it's required endpoints
        self.endpoints = {
            "init_connection": setup_endpoint,
            "host":self.server_url
        }
        # If the default server url is on localhost we launch the server locally
        if is_localhost(self.server_url):
            self.setup_server()

        # Set up the endpoints
        self.setup_endpoints()

        self.set_mesh()
        root_logger.info("MeshViewer Created")


    def check_valid_input_files(self, path, sequence_size=1):
        """ Take a path and a sequence_size and check that each file of the sequence exists.
        If it does not it outputs an error message """
        if sequence_size != 1:
            for i in range(sequence_size):
                tmp_path = path % i
                if not os.path.exists(tmp_path):
                    root_logger.error(f"The file '{tmp_path}' does not exist.")
        elif not os.path.exists(path):
            root_logger.error(f"The file '{path}' does not exist.")


    def is_server_alive(self, server):
        """ Try to make a request to the server and see if it responds to determine if he is alive """
        try:
            requests.get(server)
            return True
        except Exception:
            return False

    def setup_server(self):
        """ Launch a local server using python subprocess on another thread. If a Trame server isn't already running """
        if self.is_server_alive(self.server_url):
            return
        trame_viewer_thread = threading.Thread(target=self.run_trame_viewer)
        trame_viewer_thread.start()
        root_logger.info("MeshViewer Created")

    def setup_endpoints(self):
        """ Fill the endpoints dictionary with the info received from the server """
        # If the server was launched locally, we need to wait for it to be up
        self.wait_for_server_alive()
        res = requests.get(self.server_url + self.endpoints["init_connection"])
        try:
            json_res = res.json()
        except json.JSONDecodeError as e:
            root_logger.error("Invalid server response")
            return

        # Check that all necessary endpoints where given in the request and fill the endpoints Dict
        for endpoint in self.required_endpoints:
            if endpoint not in json_res:
                root_logger.error(f"ERROR, the endpoint {endpoint} was not specified by the server")
                continue
            self.endpoints[endpoint] = json_res[endpoint]

    def run_trame_viewer(self):
        """ Launche a Trame server using python subprocess """
        try:
            subprocess.run(["python3", os.path.dirname(os.path.abspath(__file__)) + "/trame_viewer.py", "--server"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           check=True)  # stdout=subprocess.DEVNULL,  stderr=subprocess.DEVNULL,
        except subprocess.CalledProcessError as e:
            root_logger.error("It seems like the server crashed")

    def wait_for_server_alive(self):
        """ Try to ping the server to see if it is up  """
        init_time = time.time()
        attempt = 0
        while not self.is_server_alive(self.endpoints["host"]) and attempt <= self.max_retries:
            if time.time() - init_time >= self.server_timeout:
                init_time = time.time()
                self.setup_server()
                attempt += 1

    def set_mesh(self):
        """ Set the mesh viewed on the server by making a request """
        url = self.endpoints["host"] + self.endpoints["select_mesh"]
        data = {
            "mesh_path": self.mesh_path,
            "nbr_frames": self.sequence_size,
            "width": self.width,
            "height": self.height
        }
        headers = {"Content-Type": "application/json"}

        # Check in the response if any action is necessary such as make the iframe bigger
        response = requests.get(url, data=json.dumps(data), headers=headers, timeout=2000)
        resp_body = response.json()
        if "request_space" in resp_body:
            self.height = resp_body["request_space"]

    def show(self):
        """ Render the streamlit component """
        components.iframe("http://127.0.0.1:8080/index.html", height=self.height)  # , scrolling=True
