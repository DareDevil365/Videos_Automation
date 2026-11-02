"""Owner-launched native control panel; never starts work on its own."""
from pathlib import Path
import json
import os
import queue
import sys
import threading
from datetime import datetime,timezone,timedelta
import uuid
import tkinter as tk
from tkinter import ttk,filedialog,messagebox

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from yt_pipeline.control import Controls
from yt_pipeline.core import redact


def main():
    window=tk.Tk();window.title('YouTube Pipeline - Local Controls');window.geometry('860x570')
    window.minsize(680,430)
    controls=Controls(ROOT);events=queue.Queue()
    frame=ttk.Frame(window,padding=18);frame.pack(fill='both',expand=True)
    ttk.Label(frame,text='YouTube Pipeline',font=('Segoe UI',18,'bold')).pack(anchor='w')
    ttk.Label(frame,text='Runs on this PC. Runtime AI: Gemini + local speech. No ChatGPT connection.').pack(anchor='w',pady=(4,16))
    from yt_pipeline.batches import default_plan
    from shorts_editor.store import write_json
    starter=ROOT/'Resources/Plans/playbook-starter.json'
    if not starter.exists():write_json(starter,default_plan(ROOT/'Resources'))
    plan=tk.StringVar(value=str(starter))
    line=ttk.Frame(frame);line.pack(fill='x')
    ttk.Label(line,text='Production plan:').pack(side='left',padx=(0,8))
    ttk.Entry(line,textvariable=plan).pack(side='left',fill='x',expand=True)
    def choose():
        path=filedialog.askopenfilename(initialdir=str(ROOT/'Resources'),filetypes=[('Production plans','*.json')])
        if path:plan.set(path)
    ttk.Button(line,text='Choose...',command=choose).pack(side='left',padx=(8,0))
    def new_plan():
        from yt_pipeline.batches import default_plan
        from shorts_editor.store import write_json
        value=default_plan(ROOT/'Resources')
        value['id']='batch-'+datetime.now(timezone(timedelta(hours=5,minutes=30))).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]
        path=ROOT/'Resources/Plans'/(value['id']+'.json')
        write_json(path,value);plan.set(str(path))
        status.set('New playbook plan saved. Configure permitted music/visual inputs; Start checks prerequisites before generation.')
    ttk.Button(line,text='New plan',command=new_plan).pack(side='left',padx=(8,0))
    status=tk.StringVar(value='Stopped. Nothing runs until you press Start.')
    buttons=ttk.Frame(frame);buttons.pack(fill='x',pady=14)
    log=tk.Text(frame,wrap='word',font=('Consolas',9),height=18,state='disabled')
    def append(value):
        log.configure(state='normal');log.insert('end',redact(value)+'\n');log.see('end');log.configure(state='disabled')
    def start(mode):
        try:process=controls.start(mode,plan.get() if mode.startswith('batch') else None)
        except Exception as exc:messagebox.showerror('Could not start',str(exc));return
        status.set('Running '+mode+'.');append('Started '+mode+'.')
        def read():
            try:
                for line in process.stdout:
                    # Logs are status JSON, not prompts to ChatGPT. Redact before displaying.
                    value=line.strip()
                    try:
                        event=json.loads(value);result=event.get('result',{})
                        if isinstance(result,dict) and result.get('items'):
                            value='Batch '+result.get('status','')+' | '+' | '.join(r['id']+': '+r['status'] for r in result['items'])
                        elif event.get('error'):value=event['error'].get('message',value)
                    except (ValueError,TypeError,KeyError):pass
                    events.put(('log',value))
                code=process.wait();events.put(('done',f'Task finished (exit {code}).'))
            except Exception as exc:events.put(('done','Process output interrupted: '+str(exc)))
        threading.Thread(target=read,daemon=True).start()
    ttk.Button(buttons,text='Start batch',command=lambda:start('batch-run')).pack(side='left',padx=(0,8))
    ttk.Button(buttons,text='Pause after this video',command=lambda:status.set(controls.request_stop())).pack(side='left',padx=(0,8))
    def show_status():
        if controls.running:
            from yt_pipeline.batches import batch_status
            from yt_pipeline.core import Workspace
            try:
                value=batch_status(Workspace(ROOT/'data/pipeline'),plan.get())
                append(json.dumps({'status':value['status'],'items':[{k:r.get(k) for k in ('id','status','stage','message')} for r in value['items']]},ensure_ascii=False))
            except Exception as exc:append(str(exc))
        else:start('batch-status')
    ttk.Button(buttons,text='Check status',command=show_status).pack(side='left',padx=(0,8))
    ttk.Button(buttons,text='Check setup',command=lambda:start('doctor')).pack(side='left')
    extra=ttk.Frame(frame);extra.pack(fill='x',pady=(0,10))
    ttk.Button(extra,text='Brave: one-time Google sign-in',command=lambda:start('generation-setup')).pack(side='left')
    def folder():
        path=ROOT/'Resources/Productions';path.mkdir(parents=True,exist_ok=True)
        if os.name=='nt':os.startfile(path)
    ttk.Button(extra,text='Open produced videos',command=folder).pack(side='left',padx=8)
    ttk.Label(frame,textvariable=status,wraplength=780).pack(anchor='w',pady=(0,8))
    log.pack(fill='both',expand=True)
    ttk.Label(frame,text='Pause stops before the next video. Close the dedicated Brave window to end browser setup.').pack(anchor='w',pady=(8,0))
    def poll():
        while not events.empty():
            kind,value=events.get();append(value)
            if kind=='done':status.set(value)
        window.after(150,poll)
    def close():
        if controls.running:
            controls.request_stop();status.set('Pause requested. Keep this window open until the current task finishes.');return
        window.destroy()
    window.protocol('WM_DELETE_WINDOW',close);poll();window.mainloop()


if __name__=='__main__':main()
