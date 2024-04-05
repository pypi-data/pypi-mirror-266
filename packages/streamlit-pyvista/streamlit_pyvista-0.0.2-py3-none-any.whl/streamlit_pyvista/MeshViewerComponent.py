import os
import time

import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import subprocess
import threading

from .utils import is_localhost


class MeshViewerComponent:

    def __init__(self, mesh_path: str = None, sequence_size=1, server_url="http://127.0.0.1:8080",
                 setup_endpoint="/init_connection"):
        if not os.path.isabs(mesh_path):
            mesh_path = os.getcwd() + "/" + mesh_path

        if sequence_size != 1:
            self.mesh_array = []
            for i in range(sequence_size):
                path = mesh_path % i
                if not os.path.exists(path):
                    raise FileNotFoundError(f"The file '{path}' does not exist.")
        elif not os.path.exists(mesh_path):
            raise FileNotFoundError(f"The file '{mesh_path}' does not exist.")

        self.server_url = server_url
        self.sequence_size = sequence_size
        self.mesh_path = mesh_path
        self.width = 1200
        self.height = 900
        self.server_timeout = 2
        self.required_endpoints = ["select_mesh", "host"]
        self.endpoints = {
            "init_connection": setup_endpoint
        }
        if is_localhost(self.server_url):
            self.setup_server()
        self.setup_endpoints()
        self.set_mesh()

    def is_server_alive(self):
        try:
            requests.get(self.server_url)
            return True
        except Exception as e:
            return False

    def setup_server(self):
        if self.is_server_alive():
            return
        trame_viewer_thread = threading.Thread(target=self.run_trame_viewer)
        trame_viewer_thread.start()
        print("Started new server")

    def setup_endpoints(self):
        self.wait_for_server_alive()
        res = requests.get(self.server_url + self.endpoints["init_connection"])
        try:
            json_res = res.json()
        except json.JSONDecodeError as e:
            print("ERROR " + e.msg)
            return

        for endpoint in self.required_endpoints:
            if endpoint not in json_res:
                print(f"ERROR, the endpoint {endpoint} was not specified by the server")
                return
            self.endpoints[endpoint] = json_res[endpoint]

    def run_trame_viewer(self):
        try:
            pass
            subprocess.run(["python3", os.path.dirname(os.path.abspath(__file__)) + "/trame_viewer.py"],
                           check=True)  # stdout=subprocess.DEVNULL,  stderr=subprocess.DEVNULL,
        except subprocess.CalledProcessError as e:
            print("Error:", e)

    def wait_for_server_alive(self):
        init_time = time.time()
        while not self.is_server_alive():
            if time.time() - init_time >= self.server_timeout:
                init_time = time.time()
                self.setup_server()

    def set_mesh(self):
        self.wait_for_server_alive()
        url = self.endpoints["host"] + self.endpoints["select_mesh"]
        data = {
            "mesh_path": self.mesh_path,
            "nbr_frames": self.sequence_size,
            "width": self.width,
            "height": self.height
        }
        print(f"MESH LOADED IS {self.mesh_path}")
        headers = {"Content-Type": "application/json"}
        print("send request")
        response = requests.get(url, data=json.dumps(data), headers=headers, timeout=2000)
        resp_body = response.json()
        if "request_space" in resp_body:
            self.height = resp_body["request_space"]

    def show(self):
        components.iframe("http://127.0.0.1:8080/index.html", height=self.height)  # , scrolling=True
