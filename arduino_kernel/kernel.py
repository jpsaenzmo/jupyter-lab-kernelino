from ipykernel.kernelbase import Kernel
import json
import os
import subprocess
import sys
import urllib
from urllib.request import urlopen

from requests.compat import urljoin

from notebook.notebookapp import list_running_servers

from .board import Board, BoardError

SKETCH_FOLDER = ".arduino/sketch"


class ArduinoKernel(Kernel):
    implementation = "Arduino"
    implementation_version = "1.0"
    language = "no-op"
    language_version = "0.1"
    language_info = {
        "name": "Any text",
        "mimetype": "text/plain",
        "file_extension": ".ino",
    }
    banner = "Arduino kernel"

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_bash()

    def _start_bash(self):
        from pexpect import replwrap
        import signal

        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)

        try:
            os.makedirs(SKETCH_FOLDER)
        except FileExistsError:
            pass

    def do_execute(
        self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        from pexpect import EOF

        # Empty cell
        if not code.strip():
            return {
                "status": "OK",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }
        # Non-empty cell
        interrupted = False
        try:
            try:
                os.makedirs(SKETCH_FOLDER)
            except FileExistsError:
                pass
            if code == "arduino-cli board list":
                try:
                    sp = subprocess.check_output(
                        "arduino-cli board list", stderr=subprocess.STDOUT, shell=False
                    )
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(
                        "command '{}' return with error (code {}): {}".format(
                            e.cmd, e.returncode, e.output
                        )
                    )
                output = sp.decode(sys.stdout.encoding)
            else:
                oper = code.split("\n")[0]
                command = ''
                if oper.split(":")[0] == "port":
                    port = oper.split(":")[1]
                    fqbn = code.split("\n")[1]
                    fqbn = fqbn.split(":")[1]
                    codes = code.split("\n", 2)[2]
                    command = (
                        "arduino-cli upload -p "
                        + port
                        + " --fqbn "
                        + fqbn
                        + " "
                        + SKETCH_FOLDER
                    )
                elif oper.split(":")[0] == "board":
                    fqbn = code.split("\n")[0]
                    fqbn = fqbn.split(":")[1]
                    codes = code.split("\n", 1)[1]
                    command = "arduino-cli compile -b " + fqbn + " " + SKETCH_FOLDER
                f = open(SKETCH_FOLDER + "/sketch.ino", "w+")
                f.write(codes.rstrip())
                f.close()
                try:
                    sp = subprocess.check_output(
                        command,
                        stderr=subprocess.STDOUT,
                        shell=True,
                    )
                except subprocess.CalledProcessError as e:
                    errorTxt = "Command '{}' return with error (code {}): {}".format(
                        e.cmd, e.returncode, e.output
                    )
                    stream_content = {"name": "stdout", "text": errorTxt}
                    self.send_response(self.iopub_socket, "stream", stream_content)
                    return {"status": "abort", "execution_count": self.execution_count}
                output = sp.decode(sys.stdout.encoding)
        except KeyboardInterrupt:
            interrupted = True
            clean_sketches()
        # Restarting Bash
        except EOF:
            output = self.bash_wrapper.child.before + "Restarting Bash"
        # If expecting output
        if not silent:
            stream_content = {"name": "stdout", "text": output}
            self.send_response(self.iopub_socket, "stream", stream_content)
        # If interrupted
        if interrupted:
            clean_sketches()
            return {"status": "abort", "execution_count": self.execution_count}
        # If everything is OK
        else:
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }

    def clean_sketches():
        if os.path.isfile("./" + SKETCH_FOLDER + "/sketch.ino"):
            filelist = os.listdir("./" + SKETCH_FOLDER)
            for f in filelist:
                os.remove(os.path.join(mydir, f))
