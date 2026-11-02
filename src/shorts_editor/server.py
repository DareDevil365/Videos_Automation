from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import tempfile
import threading
from urllib.parse import unquote, urlparse
import uuid

from .models import FORMATS, validate_project, template_project, ValidationError
from .render import render_project, preview, capabilities, RenderCancelled
from .store import Store, write_json, checked_id, MEDIA_EXT

MAX_UPLOAD=1024*1024*1024


def timestamp(): return datetime.now(timezone.utc).isoformat()


class Jobs:
    def __init__(self,store):
        self.store=store; self.lock=threading.RLock(); self.pool=ThreadPoolExecutor(max_workers=1)
        self.records={}; self.cancellations={}
        for file in (store.root/"jobs").glob("*/job.json"):
            record=json.loads(file.read_text(encoding="utf-8"))
            if record["status"] in ("queued","running"):
                record.update(status="interrupted",message="The editor stopped before this export finished. Start a new export when ready.")
                write_json(file,record)
            self.records[record["id"]]=record

    def save(self,record):
        write_json(self.store.root/"jobs"/record["id"]/"job.json",record)

    def all(self):
        with self.lock: return deepcopy(sorted(self.records.values(),key=lambda j:j["created_at"],reverse=True)[:50])

    def get(self,job_id):
        with self.lock:
            if job_id not in self.records: raise ValidationError("Export not found.")
            return deepcopy(self.records[job_id])

    def submit(self,project):
        project=validate_project(project); self.store.resolve_project_assets(project)
        from .composition import require_inputs
        require_inputs(project)
        with self.lock:
            if sum(j["status"] in ("queued","running") for j in self.records.values())>=4:
                raise ValidationError("The export queue is full. Let an export finish or cancel one first.")
            job_id=uuid.uuid4().hex
            record={"id":job_id,"name":project["name"],"format":project["format"],"created_at":timestamp(),
                    "status":"queued","progress":0,"message":"Waiting to export","project":project}
            self.records[job_id]=record; self.cancellations[job_id]=threading.Event(); self.save(record)
        self.pool.submit(self.work,job_id)
        return self.get(job_id)

    def cancel(self,job_id):
        with self.lock:
            if job_id not in self.records: raise ValidationError("Export not found.")
            if self.records[job_id]["status"] not in ("queued","running"): return self.get(job_id)
            self.cancellations[job_id].set()
            self.records[job_id]["message"]="Cancelling export…"; self.save(self.records[job_id])
        return self.get(job_id)

    def work(self,job_id):
        def update(value,message):
            with self.lock:
                self.records[job_id].update(progress=value,message=message); self.save(self.records[job_id])
        try:
            with self.lock:
                record=self.records[job_id]
                if self.cancellations[job_id].is_set(): raise RenderCancelled()
                record.update(status="running",message="Preparing scenes"); self.save(record)
            output=self.store.root/"jobs"/job_id/"video.mp4"
            render_project(record["project"],self.store,output,update,self.cancellations[job_id])
            with self.lock:
                record.update(status="complete",progress=1,message="Your video is ready",completed_at=timestamp(),
                              url=f"/media/jobs/{job_id}/video.mp4",cover=f"/media/jobs/{job_id}/video.png")
                self.save(record)
        except RenderCancelled:
            with self.lock: self.records[job_id].update(status="cancelled",message="Export cancelled"); self.save(self.records[job_id])
        except Exception as exc:
            with self.lock: self.records[job_id].update(status="failed",message=str(exc)); self.save(self.records[job_id])

    def close(self):
        for event in self.cancellations.values(): event.set()
        self.pool.shutdown(wait=True,cancel_futures=True)


def make_server(store,port=8765):
    from yt_pipeline.dashboard import Production
    from yt_pipeline.core import Held
    production=Production(store.root.parent/"pipeline")
    web=Path(__file__).parent/"web"; token=secrets.token_urlsafe(32); jobs=Jobs(store)
    preview_lock=threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        server_version="ShortsEditor/0.1"

        def log_message(self,fmt,*args): pass

        def trusted(self,mutation=False):
            allowed={f"127.0.0.1:{self.server.server_port}",f"localhost:{self.server.server_port}"}
            if self.headers.get("Host") not in allowed: return False
            origin=self.headers.get("Origin")
            if origin and origin not in {"http://"+h for h in allowed}: return False
            if self.headers.get("Sec-Fetch-Site")=="cross-site": return False
            return not mutation or secrets.compare_digest(self.headers.get("X-Editor-Token",""),token)

        def respond(self,data,status=200):
            payload=json.dumps(data,ensure_ascii=False).encode()
            self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Content-Length",str(len(payload))); self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff"); self.end_headers(); self.wfile.write(payload)

        def read_json(self):
            length=int(self.headers.get("Content-Length","0"))
            if not 0<length<=2_000_000: raise ValidationError("Project request is empty or too large.")
            return json.loads(self.rfile.read(length))

        def file(self,path,download=False):
            path=Path(path)
            if not path.is_file(): self.respond({"error":"File not found"},404); return
            size=path.stat().st_size; start=0; end=size-1; partial=False
            header=self.headers.get("Range")
            if header:
                match=re.fullmatch(r"bytes=(\d*)-(\d*)",header)
                if not match or not any(match.groups()):
                    self.send_error(416); return
                if match[1]: start=int(match[1]); end=min(end,int(match[2])) if match[2] else end
                else: start=max(0,size-int(match[2]))
                if start>=size or start>end:
                    self.send_response(416); self.send_header("Content-Range",f"bytes */{size}"); self.end_headers(); return
                partial=True
            self.send_response(206 if partial else 200)
            self.send_header("Content-Type",mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            self.send_header("Content-Length",str(end-start+1)); self.send_header("Accept-Ranges","bytes")
            self.send_header("X-Content-Type-Options","nosniff")
            if partial: self.send_header("Content-Range",f"bytes {start}-{end}/{size}")
            if download: self.send_header("Content-Disposition",f'attachment; filename="{path.name}"')
            self.end_headers()
            with path.open("rb") as stream:
                stream.seek(start); remaining=end-start+1
                while remaining:
                    block=stream.read(min(256*1024,remaining))
                    if not block: break
                    self.wfile.write(block); remaining-=len(block)

        def do_GET(self):
            if not self.trusted(): self.respond({"error":"Local requests only"},403); return
            route=urlparse(self.path).path
            try:
                if route=="/api/production":self.respond(production.status())
                elif route=="/api/production-example":self.file(web/"education-request.json")
                elif route=="/production":self.file(web/"production.html")
                elif route in ("/production.css","/production.js"):self.file(web/route.lstrip("/"))
                elif re.fullmatch(r"/production/files/[0-9a-f]{32}/(video|cover|captions|package)",route):
                    parts=route.split('/');self.file(production.output(parts[3],parts[4]),download=parts[4] in ('captions','package'))
                elif route=="/api/bootstrap":
                    demo_file=store.root/"demo.json"
                    self.respond({"token":token,"formats":FORMATS,"assets":store.list_assets(),"projects":store.list_projects(),
                                  "jobs":jobs.all(),"capabilities":capabilities(),
                                  "demo":json.loads(demo_file.read_text()) if demo_file.exists() else {}})
                elif route=="/api/jobs": self.respond(jobs.all())
                elif route.startswith("/api/templates/"):
                    demo_file=store.root/"demo.json"
                    self.respond(template_project(route.split("/")[-1],json.loads(demo_file.read_text()) if demo_file.exists() else {}))
                elif route.startswith("/api/projects/"): self.respond(store.project(route.split("/")[-1]))
                elif route.startswith("/api/jobs/"): self.respond(jobs.get(checked_id(route.split("/")[-1])))
                elif route.startswith("/media/assets/"):
                    self.file(store.asset(route.split("/")[-1])["path"])
                elif re.fullmatch(r"/media/previews/[0-9a-f]{64}\.png",route): self.file(store.root/"previews"/route.split("/")[-1])
                elif re.fullmatch(r"/media/jobs/[0-9a-f]{32}/video\.(mp4|png|srt|manifest\.json|project\.json)",route):
                    parts=route.split("/"); record=jobs.get(parts[3])
                    if record["status"]!="complete": raise ValidationError("Export is not ready yet.")
                    self.file(store.root/"jobs"/parts[3]/parts[4],download=parts[4].endswith((".json",".srt")))
                elif route in ("/","/index.html","/studio.css","/studio.js"):
                    self.file(web/("studio.html" if route in ("/","/index.html") else route.lstrip("/")))
                elif route in ("/legacy","/style.css","/app.js"):
                    self.file(web/("index.html" if route=="/legacy" else route.lstrip("/")))
                else: self.respond({"error":"Not found"},404)
            except (ValidationError,ValueError,KeyError) as exc: self.respond({"error":str(exc)},400)
            except (BrokenPipeError,ConnectionResetError): pass
            except Exception as exc: self.respond({"error":str(exc)},500)

        def do_POST(self):
            if not self.trusted(True):
                # Drain a small rejected body so Windows can deliver the HTTP error
                # before closing, rather than resetting a socket with unread data.
                try: length=int(self.headers.get("Content-Length","0"))
                except ValueError: length=0
                if 0<length<=2_000_000: self.rfile.read(length)
                self.respond({"error":"Invalid local session. Reload this editor tab."},403); return
            route=urlparse(self.path).path
            try:
                if route=="/api/production":self.respond(production.action(self.read_json()),202)
                elif route=="/api/assets":
                    length=int(self.headers.get("Content-Length","0"))
                    if not 0<length<=MAX_UPLOAD: raise ValidationError("Import files up to 1 GB each.")
                    name=Path(unquote(self.headers.get("X-Filename","media"))).name
                    suffix=Path(name).suffix.lower()
                    if suffix not in MEDIA_EXT: raise ValidationError("Choose an image, video, GIF, or audio file.")
                    temporary=store.root/"assets"/(uuid.uuid4().hex+suffix)
                    try:
                        with temporary.open("wb") as output:
                            remaining=length
                            while remaining:
                                chunk=self.rfile.read(min(1024*1024,remaining))
                                if not chunk: raise ValidationError("Import interrupted. Try again.")
                                output.write(chunk); remaining-=len(chunk)
                        self.respond(store.register(temporary,name))
                    finally:
                        temporary.unlink(missing_ok=True)
                elif route=="/api/projects":
                    body=self.read_json(); self.respond(store.save_project(body["project"],body.get("id")))
                elif route=="/api/preview":
                    body=self.read_json()
                    with preview_lock: path=preview(body["project"],store,int(body.get("scene",0)),body.get("at"))
                    self.respond({"url":"/media/previews/"+path.name})
                elif route=="/api/renders": self.respond(jobs.submit(self.read_json()["project"]),202)
                elif re.fullmatch(r"/api/jobs/[0-9a-f]{32}/cancel",route): self.respond(jobs.cancel(route.split("/")[3]))
                else: self.respond({"error":"Not found"},404)
            except Held as exc:self.respond({"error":str(exc),"code":exc.code},409)
            except (ValidationError,ValueError,KeyError,TypeError) as exc: self.respond({"error":str(exc)},400)
            except (BrokenPipeError,ConnectionResetError): pass
            except Exception as exc: self.respond({"error":str(exc)},500)

    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    server.jobs=jobs
    original_close=jobs.close
    def close():
        original_close();production.close()
    jobs.close=close
    server.production=production
    return server
