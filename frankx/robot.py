import base64
import json
import hashlib
from http.client import HTTPSConnection
import ssl
from time import sleep
import threading

from _frankx import Robot as _Robot
from .gripper import Gripper as _Gripper


class MyThread(threading.Thread):
    def __init__(self, rb, ar):
        super().__init__()
        self._stop_event = threading.Event()
        self.rb = rb
        self.ar = ar
        self.flag = False

    def check_state(self):
        
        if self._stop_event.is_set():
            self.rb.stop()
            self.flag = True

        elif not self._stop_event.is_set() and not self.flag:
            threading.Timer(0.5, self.check_state).start()

    def run(self):

        self.check_state()
        self.rb.move(self.ar[0])

    def stop(self):

        self._stop_event.set()


class Robot(_Robot):
    def __init__(
        self,
        fci_ip,
        dynamic_rel=1.0,
        user=None,
        password=None,
        repeat_on_error=False,
        stop_at_python_signal=True,
    ):
        super().__init__(
            fci_ip,
            dynamic_rel=dynamic_rel,
            repeat_on_error=repeat_on_error,
            stop_at_python_signal=stop_at_python_signal,
        )
        self.hostname = fci_ip
        self.user = user
        self.password = password

        self.client = None
        self.token = None

    @staticmethod
    def _encode_password(user, password):
        bs = ",".join(
            [
                str(b)
                for b in hashlib.sha256(
                    (password + "#" + user + "@franka").encode("utf-8")
                ).digest()
            ]
        )
        return base64.encodebytes(bs.encode("utf-8")).decode("utf-8")

    def __enter__(self):
        self.client = HTTPSConnection(
            self.hostname, timeout=12, context=ssl._create_unverified_context()
        )  # [s]
        self.client.connect()
        self.client.request(
            "POST",
            "/admin/api/login",
            body=json.dumps(
                {
                    "login": self.user,
                    "password": self._encode_password(self.user, self.password),
                }
            ),
            headers={"content-type": "application/json"},
        )
        self.token = self.client.getresponse().read().decode("utf8")
        return self

    def __exit__(self, type, value, traceback):
        self.client.close()

    def start_task(self, task):
        self.client.request(
            "POST",
            "/desk/api/execution",
            body=f"id={task}",
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "Cookie": f"authorization={self.token}",
            },
        )
        return self.client.getresponse().read()

    def unlock_brakes(self):
        self.client.request(
            "POST",
            "/desk/api/robot/open-brakes",
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "Cookie": f"authorization={self.token}",
            },
        )
        return self.client.getresponse().read()

    def lock_brakes(self):
        self.client.request(
            "POST",
            "/desk/api/robot/close-brakes",
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "Cookie": f"authorization={self.token}",
            },
        )
        return self.client.getresponse().read()

    def move_async(self, *args) -> threading.Thread:
        # p = Thread(target=self.move, args=tuple(args), daemon=True)
        # p.start()
        #
        p = MyThread(self, args)
        p.start()
        sleep(0.001)  # Sleep one control cycle
        return p

    def get_gripper(self):
        return _Gripper(self.fci_ip)
