import json
import subprocess
import os

from docker import Client
from docker.tls import TLSConfig
from requests import ConnectionError

class DockerClientFactory(object):
    def get_client(self):
        # First, let's try to create a docker client without docker-machine
        client = self._create_basic_client()

        # If it failed, that means we're probably running on Windows or OS X.
        # Let's try to create a client with docker-machine
        if client is None:
            client = self._create_client_with_docker_machine()

        return client

    def _create_basic_client(self):
        try:
            client = Client()
            if not client.ping():
                return None

            return client
        except ConnectionError:
            return None

    def _create_client_with_docker_machine(self):
        config = json.loads(subprocess.check_output(["docker-machine", "inspect", "dev"]))

        if not config["HostOptions"]["EngineOptions"]["TlsVerify"]:
            raise Exception("TLS is required.")

        cert_path = config["HostOptions"]["AuthOptions"]["StorePath"]
        tls_config = TLSConfig(client_cert=(os.path.join(cert_path, 'cert.pem'),
                                            os.path.join(cert_path, 'key.pem')),
                               ca_cert=os.path.join(cert_path, 'ca.pem'),
                               verify=True,
                               assert_hostname=False)

        client = Client(base_url="https://{}:2376".format(config["Driver"]["IPAddress"]),
                        tls=tls_config)
        client.ping()
        return client
