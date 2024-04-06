from IPython.display import display, HTML
from IPython.core.magic import (
    Magics,
    magics_class,
    line_cell_magic,
)
from IPython import get_ipython

import json
import base64
import pickle
import time
from requests import HTTPError

from ..agent_client.agent_client import AGClient
from ..utils.error_print import eprint
from .errors import AGRuntimeError
from ..config.config import config

@magics_class
class AGMagic(Magics):
    """
    Provides %%ag cell magic and private python code execution on Antigranular server
    """

    session_id: str
    # user_name: str
    ag_server: AGClient

    @classmethod
    def load_oblv_client(cls, ag_server, session_id):
        cls.ag_server = ag_server
        cls.session_id = session_id
        # cls.user_name = user_name

    @line_cell_magic
    def ag(self, line, cell=None):
        """
        Executes the provided code on the Antigranular server.

        Parameters:
            line (str): The code in a single line.
            cell (str): The code in a cell format.

        Returns:
            None
        """
        if cell is None:
            print("Please call ag as a cell magic using '%%ag'")
            return
        else:
            try:
                self.execute(cell)
            # except any exception
            except KeyboardInterrupt:
                res = self.interrupt_kernel()
                if res["status"] == "ok":
                    # return interrupt message
                    eprint("Kernel interrupted successfully")
                else:
                    eprint("Error while interrupting kernel")
                    eprint(res)

    def execute(self, code: str):
        """
        Executes the code on the Antigranular server.

        Parameters:
            code (str): The code to be executed.

        Returns:
            None
        """
        try:
            res = self.ag_server.post(
                f"{self.ag_server.url}:{self.ag_server.port}/sessions/execute",
                json={"session_id": self.session_id, "code": code},
            )
        except Exception as err:
            raise ConnectionError(f"Error calling /execute: {str(err)}")
        else:
            if res.status_code != 200:
                raise HTTPError(
                    f"Error while requesting AG server to execute the code, HTTP status code: {res.status_code}, message: {res.text}"
                )
            res_body_dict = json.loads(res.text)
            self.get_output(res_body_dict.get('message_id'))

    def interrupt_kernel(self) -> dict:
        try:
            res = self.ag_server.post(
                f"{self.ag_server.url}:{self.ag_server.port}/sessions/interrupt-kernel",
                json={"session_id": self.session_id},
            )
        except Exception as err:
            raise ConnectionError(
                f"Error calling /sessions/interrupt-kernel: {str(err)}"
            )
        else:
            if res.status_code != 200:
                raise HTTPError(
                    f"Error while requesting AG server to interrupt the kernel, HTTP status code: {res.status_code}, message: {res.text}"
                )
            return json.loads(res.text)

    def get_output(self, message_id):
        """
        Retrieves the code execution output from the Antigranular server.
        """
        count = 1

        while True:
            if count > int(config.AG_EXEC_TIMEOUT):
                eprint("Error : AG execution timeout.")
                break
            try:
                res = self.ag_server.get(
                    f"{self.ag_server.url}:{self.ag_server.port}/sessions/output",
                    params={"session_id": self.session_id},
                )
            except Exception as err:
                raise ConnectionError(
                    f"Error during code execution on AG Server: {str(err)}"
                )
            if res.status_code != 200:
                raise HTTPError(
                    f"Error while requesting AG server for output, HTTP status code: {res.status_code}, message: {res.text}"
                )
            kernel_messages = json.loads(res.text)["output_list"]
            for message in kernel_messages:
                if message.get("parent_header", {}).get("msg_id") == message_id:
                    if message["msg_type"] == "status":
                        if message["content"]["execution_state"] == "idle":
                            return
                    elif message["msg_type"] == "stream":
                        if message["content"]["name"] == "stdout":
                            print(message["content"]["text"])
                        elif message["content"]["name"] == "stderr":
                            eprint(message["content"]["text"])

                    elif message["msg_type"] == "error":
                        tb_str = ""
                        for tb in message["content"]["traceback"]:
                            tb_str += tb

                        print(tb_str)
                        raise AGRuntimeError(
                            etype=str(message["content"]["evalue"]),
                            evalue="RuntimeError",
                            msg=tb_str,
                        )

                    elif message["msg_type"] == "ag_export_value":
                        try:
                            user_ns = get_ipython().user_ns
                            data = message["content"]
                            for name, value in data.items():
                                user_ns[name] = pickle.loads(base64.b64decode(value))
                                print(
                                    "Setting up exported variable in local environment:",
                                    name,
                                )

                        except Exception as err:
                            raise ValueError(
                                f"Error while parsing export values message: {str(err)}"
                            )
            time.sleep(1)
            count += 1

    @staticmethod
    def load_ag_magic():
        """
        Loads the AGMagic class as a magic in the IPython session.
        """
        ipython = get_ipython()
        if ipython is None:
            raise RuntimeError(
                "This function can only be called from an IPython session"
            )
        ipython.register_magics(AGMagic)
        print(
            "Cell magic '%%ag' registered successfully, use `%%ag` in a notebook cell to execute your python code on Antigranular private python server"
        )
