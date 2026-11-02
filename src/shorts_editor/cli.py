import argparse
import json
from pathlib import Path
import sys
import threading
import webbrowser

from .demo import create_demo
from .models import FORMATS, template_project, ValidationError
from .render import render_project, capabilities
from .server import make_server
from .store import Store
from .jobspec import materialize_job


def main():
    parser=argparse.ArgumentParser(description="Standalone Shorts format editor")
    parser.add_argument("--data",default=str(Path.cwd()/"data"/"editor"),help="Local media/project directory")
    commands=parser.add_subparsers(dest="command",required=True)
    serve=commands.add_parser("serve",help="Start the local editor")
    serve.add_argument("--port",type=int,default=8765); serve.add_argument("--open",action="store_true")
    serve.add_argument("--no-demo",action="store_true",help="Deprecated: the editor no longer generates demo media on startup")
    serve.add_argument("--with-demo",action="store_true",help="Explicitly create synthetic test/demo media")
    commands.add_parser("demo",help="Create original sample assets and example project JSON files")
    commands.add_parser("formats",help="List format identifiers")
    render=commands.add_parser("render",help="Render a project without the browser")
    render.add_argument("project",help="Project JSON path or demo:story, demo:split, etc.")
    render.add_argument("--output",required=True,help="New MP4 output path")
    render.add_argument("--json",action="store_true",help="Emit one machine-readable result on stdout; progress goes to stderr")
    compose=commands.add_parser("compose",help="Fill a layout with local clips from a JSON job and export")
    compose.add_argument("job",help="JSON job with template, inputs and timing")
    compose.add_argument("--output",required=True,help="New MP4 output path")
    compose.add_argument("--json",action="store_true",help="Emit one machine-readable result on stdout; progress goes to stderr")
    args=parser.parse_args()
    try:
        if args.command=="formats": print(json.dumps(FORMATS,indent=2)); return
        if not all(capabilities().values()): raise RuntimeError("FFmpeg and ffprobe must both be installed and available on PATH.")
        store=Store(args.data)
        if args.command=="demo":
            create_demo(store); print(f"Original demo assets and JSON recipes: {store.root}"); return
        if args.command in ("render","compose"):
            if Path(args.output).exists(): raise ValidationError("Output already exists. Choose a new filename.")
            if args.command=="compose":
                job_path=Path(args.job).resolve()
                project=materialize_job(json.loads(job_path.read_text(encoding="utf-8")),store,job_path.parent)
            elif args.project.startswith("demo:"): project=template_project(args.project.split(":",1)[1],create_demo(store))
            else:
                project=json.loads(Path(args.project).read_text(encoding="utf-8")); project=project.get("project",project)
            machine=args.json
            manifest=render_project(project,store,args.output,lambda value,message: print(
                f"{value*100:5.1f}% {message}",file=sys.stderr if machine else sys.stdout,flush=True))
            output=Path(args.output).resolve()
            if machine:
                print(json.dumps({"schema_version":1,"status":"complete",
                    "outputs":{"video":str(output),"cover":str(output.with_suffix('.png')),
                               "captions":str(output.with_suffix('.srt')),
                               "project":str(output.with_suffix('.project.json')),
                               "manifest":str(output.with_suffix('.manifest.json'))},
                    "duration":manifest["duration"],"width":manifest["width"],"height":manifest["height"]}))
            else: print(f"Export ready: {output}")
            return
        if args.with_demo: create_demo(store)
        server=make_server(store,args.port); url=f"http://127.0.0.1:{server.server_port}"
        print(f"Shorts Studio: {url}\nLocal data: {store.root}\nPress Ctrl+C to stop.",flush=True)
        if args.open: threading.Timer(.6,lambda:webbrowser.open(url)).start()
        try: server.serve_forever(poll_interval=.3)
        except KeyboardInterrupt: pass
        finally: server.server_close(); server.jobs.close()
    except Exception as exc:
        if getattr(args,"json",False):
            print(json.dumps({"schema_version":1,"status":"failed","error":{"type":type(exc).__name__,"message":str(exc)}}))
        else: print(f"Editor error: {exc}",file=sys.stderr)
        raise SystemExit(1)


if __name__=="__main__": main()
