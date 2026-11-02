"""Standalone process controls. No browser/AI API is used by this module."""
from pathlib import Path
import os
import subprocess
import sys
import threading


def command(root,mode,plan=None,stop_file=None):
    root=Path(root).resolve()
    executable=Path(sys.executable)
    if executable.stem.lower()=='pythonw':executable=executable.with_name('python.exe')
    args=[str(executable),str(root/'run_pipeline.py'),'--env-file',str(root/'.env')]
    if mode in ('batch-run','batch-status'):
        args.append(mode)
        if plan:args+=['--plan',str(Path(plan).resolve())]
        if mode=='batch-run' and stop_file:args+=['--stop-file',str(stop_file)]
    elif mode=='generation-setup':args+=['generation-setup','--browser','brave']
    elif mode=='doctor':args+=['doctor']
    else:raise ValueError('Unknown standalone operation')
    return args


class Controls:
    def __init__(self,root):
        self.root=Path(root).resolve();self.process=None;self.lock=threading.Lock()
        self.stop_file=self.root/'data/pipeline/control/pause-after-video'
        self.mode=None

    @property
    def running(self):return self.process is not None and self.process.poll() is None

    def start(self,mode,plan=None):
        with self.lock:
            if self.running:raise RuntimeError('A control-panel task is already running')
            self.stop_file.parent.mkdir(parents=True,exist_ok=True)
            self.stop_file.unlink(missing_ok=True)
            flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
            self.process=subprocess.Popen(command(self.root,mode,plan,self.stop_file),cwd=self.root,
                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',
                creationflags=flags)
            self.mode=mode;return self.process

    def request_stop(self):
        if not self.running:return 'No task is running.'
        if self.mode!='batch-run':
            return 'Close the dedicated setup browser to finish saving its session. No generation queue is active.' if self.mode=='generation-setup' else 'The status/setup check is finishing; no video queue is active.'
        self.stop_file.write_text('Pause after the current video. Do not start another job.\n',encoding='utf-8')
        return 'Pause requested. The current video may finish; the next video will not start.'
