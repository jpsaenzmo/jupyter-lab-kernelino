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

SKETCH_FOLDER = '.sketch'

class ArduinoKernel(Kernel):
    implementation = 'Arduino'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'Any text',
        'mimetype': 'text/plain',
        'file_extension': '.ino',
    }
    banner = "Arduino kernel"

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_bash()

    def _start_bash(self):
        from pexpect import replwrap
        import signal

        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)

        # req = urllib.request.Request(url, headers=head)
        # sessions = json.load(urlopen(req).read())
        # for sess in sessions:
        #    if sess['kernel']['id'] == kernel_id:
        #        print(sess['notebook']['name'])
        #        break
        try:
            os.makedirs(SKETCH_FOLDER)
        except FileExistsError:
            pass
        # try:
        # self.bash_wrapper = replwrap.bash()
        # finally:
        # signal.signal(signal.SIGINT, sig)

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        from pexpect import EOF
        # Empty cell
        if not code.strip():
            return {
                'status': 'OK',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}
            }
        # Non-empty cell
        interrupted = False
        try:
            try:
                os.makedirs(SKETCH_FOLDER)
            except FileExistsError:
                pass
            if code == 'arduino-cli board list':
                try:
                    sp = subprocess.check_output(
                        'arduino-cli board list', stderr=subprocess.STDOUT, shell=False)
                except subprocess.CalledProcessError as e:
                    raise RuntimeError("command '{}' return with error (code {}): {}".format(
                        e.cmd, e.returncode, e.output))
                output = sp.decode(sys.stdout.encoding)
            else:
                f = open(SKETCH_FOLDER+'/sketch.ino', 'w+')
                f.write(code.rstrip())
                f.close()
                try:
                    sp = subprocess.check_output(
                        'arduino-cli compile -b arduino:avr:yun sketch', stderr=subprocess.STDOUT, shell=True)
                except subprocess.CalledProcessError as e:
                    raise RuntimeError("command '{}' return with error (code {}): {}".format(
                        e.cmd, e.returncode, e.output))
                output = sp.decode(sys.stdout.encoding)
        except KeyboardInterrupt:
            # self.bash_wrapper.child.sendintr()
            interrupted = True
            clean_sketches()
            # self.bash_wrapper._expect_prompt()
            # output = self.bash_wrapper.child.before
            output = 'Mundo'
        # Restarting Bash
        except EOF:
            # output = self.bash_wrapper.child.before + 'Restarting Bash'
            # self._start_bash()
            output = 'Cruel'
        # If expecting output
        if not silent:
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)
        # If interrupted
        if interrupted:
            clean_sketches()
            return {'status': 'abort', 'execution_count': self.execution_count}
        # If something has errored out

        # try:
            # exitcode = int(self.bash_wrapper.run_command('echo $?').rstrip())
        # except Exception:
            # exitcode = 1

        # if exitcode:
            # error_content = {'execution_count': self.execution_count, 'ename': '', 'evalue': str(exitcode), 'traceback': []}
            # self.send_response(self.iopub_socket, 'error', error_content)
            # error_content['status'] = 'error'
            # return error_content
        # If everything is OK
        else:
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}

    def clean_sketches():
        if os.path.isfile('./'+SKETCH_FOLDER+'/sketch.ino'):
            filelist = os.listdir('./'+SKETCH_FOLDER)
            for f in filelist:
                os.remove(os.path.join(mydir, f))