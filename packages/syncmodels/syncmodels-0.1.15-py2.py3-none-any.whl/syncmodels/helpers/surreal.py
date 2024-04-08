"""
SurrealDB helpers
"""

import atexit
import base64
import re
import os
import signal
import sys

from subprocess import Popen, PIPE, TimeoutExpired


def to64(x):
    x = f"{x}"
    x = bytes(x, "utf-8")
    x = base64.b64encode(x)
    x = x.decode("utf-8")
    x = x.replace("=", "_")

    # y = from64(x)
    return x


def from64(x):
    x = x.replace("_", "=")
    x = base64.b64decode(x)
    x = x.decode("utf-8")
    return x


class SurrealServer:
    """A helper to launch a local surrealDB server"""

    def __init__(self, path, bind="0.0.0.0:9000", daemon=False):
        self.path = path
        self.bind = bind
        self.daemon = daemon
        self.proc = None
        self.pid = None

    def cmd(self):
        return [
            "surreal",
            "start",
            "--bind",
            f"{self.bind}",
            "--user",
            "root",
            "--pass",
            "root",
            f"file://{self.path}",
        ]

    def start(self):
        """starts surreal process and register a callback is anything goes wrong"""
        os.makedirs(self.path, exist_ok=True)

        extra = {}
        self.pid = os.getpid()

        def launch():

            # launch server
            self.proc = Popen(
                self.cmd(),
                stdout=PIPE,
                stderr=PIPE,
                **extra,
            )
            # give sometime to communicate with process
            # so server will be ready or we get some error feedback
            try:
                stdout, stderr = self.proc.communicate(timeout=0.5)
                print(stdout)
                print(stderr)
                return False
                # raise RuntimeError()  # something was wrong

            except TimeoutExpired:
                pass

            # print(f"Server pid: {self.pid}")
            if self.daemon:
                # with open(f"{self.url}/pid", "w", encoding="utf-8") as f:
                # f.write(f"{self.pid}")
                pass
            else:
                # stop process when parent process may die
                atexit.register(self.stop)

        if self.daemon:
            try:
                print("forking process ...")
                pid = os.fork()
                self.pid = os.getpid()

                if pid:
                    pass
                else:
                    print(f"child launch server")
                    launch()
                    # detach
                    print(f"child detach fds")
                    sys.stdin.close()
                    sys.stdout.close()
                    sys.stderr.close()
            except OSError as why:
                print(why)
                os._exit(1)
        else:
            launch()

        return True

    def stop(self):
        """stops child process and unregister callback"""
        if self.daemon:
            # find process that match the launching arguments
            cmd = "\0".join(self.cmd())
            for root, folders, _ in os.walk("/proc"):
                for pid in folders:
                    if re.match(r"\d+", pid):
                        try:
                            cmdline = open(
                                f"{root}/{pid}/cmdline", "r", encoding="utf-8"
                            ).read()
                            if cmd in cmdline:
                                print(f"Stopping: {pid} : {' '.join(self.cmd())}")
                                os.kill(int(pid), signal.SIGTERM)
                                return True
                        except Exception:
                            pass
            else:
                cmd = " ".join(self.cmd())
                print(f"can't find a surreal server such: '{cmd}'")
                return False
        else:
            self.proc.terminate()
            atexit.unregister(self.stop)
        return True
