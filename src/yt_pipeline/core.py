from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import time
import uuid

from shorts_editor.store import write_json


STAGES = ("research", "script", "voice", "visuals", "direct", "render", "quality", "package")


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""): result.update(chunk)
    return result.hexdigest()


class Held(Exception):
    def __init__(self, code, message, retry_after=None):
        super().__init__(message)
        self.code, self.retry_after = code, retry_after


def redact(message):
    value = str(message)
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "YOUTUBE_API_KEY", "PEXELS_API_KEY", "OPENAI_API_KEY"):
        secret = os.environ.get(key)
        if secret: value = value.replace(secret, "[redacted]")
    for name,secret in os.environ.items():
        if secret and re.fullmatch(r"(?:GEMINI|GOOGLE|OPENAI)_API_KEY(?:_[A-Z0-9_]+)?",name):value=value.replace(secret,"[redacted]")
    value = re.sub(r"sk-[A-Za-z0-9_-]{16,}","[redacted]",value)
    value = re.sub(r"AIza[\w-]{20,}", "[redacted]", value)
    value = re.sub(r"AQ\.[A-Za-z0-9_-]{20,}", "[redacted]", value)
    return value[:1800]


def default_config():
    common = {"language":"en-US", "audience":"US-first English", "paused":False,
              "daily_cap":4, "youtube_channel_id":"", "publication_mode":"disabled",
              "auto_private_upload":False, "feed_urls":[], "source_urls":[], "research_queries":[], "footage_ids":[], "music_id":""}
    return {"version":1, "text_provider":"gemini", "openai":{"model":"", "api_usage_enabled":False, "key_env":"OPENAI_API_KEY", "requests_per_day":10, "max_output_tokens":8192}, "gemini":{"model":"gemini-3.5-flash-lite", "free_tier_confirmed":False,
                                   "requests_per_day":30, "enforce_local_budget":True, "max_output_tokens":4096},
            "voice":{"model":"voices/en_US-ljspeech-high.onnx", "commercial_use_checked":False,
                     "license_evidence":[], "length_scale":1.0},
            "channels":{"entertainment":{**common,"name":"Entertainment","style":"Fictional chat stories with a clear payoff", "format":"chat"},
                        "education":{**common,"name":"Education","style":"Relatable productivity, studying, confidence, jobs, realistic earning skills and useful/free AI tools; one practical takeaway in plain language", "format":"lesson","media_mode":"stock"}}}


class Workspace:
    def __init__(self, root="data/pipeline"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        for name in ("jobs","voices","assets","cache","credentials","reports"):
            (self.root/name).mkdir(exist_ok=True)
        self.db_path = self.root/"pipeline.sqlite3"
        self.config_path = self.root/"config.json"
        if not self.config_path.exists(): write_json(self.config_path, default_config())
        with self.connect() as db:
            db.executescript("""
              CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, channel TEXT NOT NULL, request TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued', stage TEXT NOT NULL DEFAULT 'research',
                artifacts TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                lease_owner TEXT, lease_until REAL, retry_at REAL, error_code TEXT, message TEXT,
                version TEXT NOT NULL, script_hash TEXT, approval_hash TEXT, video_id TEXT);
              CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, job_id TEXT, at TEXT, kind TEXT, data TEXT);
              CREATE TABLE IF NOT EXISTS assets (id TEXT PRIMARY KEY, data TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS usage (day TEXT, provider TEXT, calls INTEGER, PRIMARY KEY(day,provider));
              CREATE TABLE IF NOT EXISTS uploads (job_id TEXT PRIMARY KEY, data TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS observations (id INTEGER PRIMARY KEY, job_id TEXT, window TEXT, at TEXT, data TEXT,
                UNIQUE(job_id,window));
              CREATE TABLE IF NOT EXISTS alerts (key TEXT PRIMARY KEY, job_id TEXT, at TEXT, message TEXT, acknowledged INTEGER DEFAULT 0);
              CREATE TABLE IF NOT EXISTS worker_locks (name TEXT PRIMARY KEY, owner TEXT, expires REAL);
              CREATE TABLE IF NOT EXISTS public_snapshots (video_id TEXT, at TEXT, data TEXT, PRIMARY KEY(video_id,at));
              CREATE TABLE IF NOT EXISTS provider_cooldowns (provider TEXT PRIMARY KEY, until REAL, failures INTEGER);
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=20)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally: db.close()

    def config(self):
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def save_config(self, value):
        write_json(self.config_path, value)

    def resolve(self, value):
        path = Path(value)
        return path.resolve() if path.is_absolute() else (self.root/path).resolve()

    def job_dir(self, job_id):
        if not re.fullmatch(r"[a-f0-9]{32}", job_id): raise ValueError("Invalid job ID")
        path = self.root/"jobs"/job_id
        path.mkdir(exist_ok=True)
        return path

    def event(self, job_id, kind, data):
        with self.connect() as db:
            db.execute("INSERT INTO events(job_id,at,kind,data) VALUES(?,?,?,?)", (job_id,now(),kind,json.dumps(data)))

    def alert(self, key, job_id, message):
        with self.connect() as db:
            db.execute("INSERT OR IGNORE INTO alerts(key,job_id,at,message) VALUES(?,?,?,?)", (key,job_id,now(),redact(message)))

    def create(self, channel, request):
        if channel not in self.config()["channels"]: raise ValueError("Unknown channel profile")
        if not isinstance(request,dict): raise ValueError("Job request must be an object")
        job_id = uuid.uuid4().hex
        request = json.loads(json.dumps(request))
        with self.connect() as db:
            db.execute("INSERT INTO jobs(id,channel,request,created_at,updated_at,version) VALUES(?,?,?,?,?,?)",
                       (job_id,channel,json.dumps(request),now(),now(),digest(request)))
        write_json(self.job_dir(job_id)/"request.json", request)
        self.event(job_id,"created",{"channel":channel})
        return self.get(job_id)

    def get(self, job_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone()
        if row is None: raise ValueError("Job not found")
        result = dict(row)
        for key in ("request","artifacts"): result[key] = json.loads(result[key])
        return result

    def jobs(self, limit=100):
        with self.connect() as db:
            ids = [r[0] for r in db.execute("SELECT id FROM jobs ORDER BY created_at DESC LIMIT ?",(limit,))]
        return [self.get(job_id) for job_id in ids]

    def update(self, job_id, **values):
        allowed={"status","stage","artifacts","lease_owner","lease_until","retry_at","error_code","message","script_hash","approval_hash","video_id"}
        if not values.keys() <= allowed: raise ValueError("Invalid job update")
        values["updated_at"] = now()
        if "artifacts" in values: values["artifacts"] = json.dumps(values["artifacts"])
        with self.connect() as db:
            db.execute("UPDATE jobs SET "+",".join(k+"=?" for k in values)+" WHERE id=?",[*values.values(),job_id])

    def claim(self, job_id, owner, seconds=180):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT status,lease_owner,lease_until FROM jobs WHERE id=?",(job_id,)).fetchone()
            if row is None: raise ValueError("Job not found")
            if row["lease_until"] and row["lease_until"]>time.time() and row["lease_owner"]!=owner:
                raise Held("job_busy","This job is already being worked on.")
            if row["status"] in ("ready","published","cancelled","uploaded_private","scheduled","processing"): return False
            db.execute("UPDATE jobs SET status='running',lease_owner=?,lease_until=?,updated_at=? WHERE id=?",(owner,time.time()+seconds,now(),job_id))
        return True

    def heartbeat(self, job_id, owner):
        with self.connect() as db:
            cursor=db.execute("UPDATE jobs SET lease_until=? WHERE id=? AND lease_owner=? AND status='running'",(time.time()+180,job_id,owner))
        return cursor.rowcount==1

    def reserve_call(self, provider, cap):
        self.reserve_calls([(provider,cap)])

    def reserve_calls(self, limits):
        """Atomically account for aggregate and independent-project budgets."""
        day=datetime.now(timezone.utc).date().isoformat()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for provider,cap in limits:
                row=db.execute("SELECT calls FROM usage WHERE day=? AND provider=?",(day,provider)).fetchone()
                if cap is not None and row and row[0]>=cap:
                    current=datetime.now(timezone.utc)
                    reset=(current+timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
                    raise Held("project_budget" if provider.startswith('gemini:') else "daily_budget",
                               "Local daily call budget reached; saved work remains queued.",retry_after=max(1,math.ceil((reset-current).total_seconds())))
            for provider,cap in limits:
                db.execute("INSERT INTO usage(day,provider,calls) VALUES(?,?,1) ON CONFLICT(day,provider) DO UPDATE SET calls=calls+1",(day,provider))

    def check_provider(self, provider):
        with self.connect() as db:row=db.execute('SELECT until FROM provider_cooldowns WHERE provider=?',(provider,)).fetchone()
        if row and row['until']>time.time():
            raise Held('gemini_quota' if provider=='gemini' else 'provider_cooldown',
                       'Provider quota cooldown is active. Saved work remains queued; no new API request was sent.',
                       retry_after=max(1,math.ceil(row['until']-time.time())))

    def cool_provider(self, provider, minimum=0):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT until,failures FROM provider_cooldowns WHERE provider=?',(provider,)).fetchone()
            failures=(row['failures'] if row else 0)+1
            delay=max(float(minimum),min(3600,60*2**min(failures-1,6)))
            until=max(time.time()+delay,row['until'] if row else 0)
            db.execute('INSERT INTO provider_cooldowns(provider,until,failures) VALUES(?,?,?) ON CONFLICT(provider) DO UPDATE SET until=excluded.until,failures=excluded.failures',(provider,until,failures))
        return max(1,math.ceil(until-time.time()))

    def provider_succeeded(self, provider):
        with self.connect() as db:db.execute('DELETE FROM provider_cooldowns WHERE provider=?',(provider,))

    def gemini_budget_cap(self):
        config=self.config();settings=config['gemini']
        production=any(p.get('publication_mode','disabled')!='disabled' for p in config['channels'].values())
        if settings.get('enforce_local_budget',True) is not False or production:
            return int(settings.get('requests_per_day',30))
        return None

    def quota_status(self, provider, cap):
        day=datetime.now(timezone.utc).date().isoformat()
        with self.connect() as db:
            usage=db.execute('SELECT calls FROM usage WHERE day=? AND provider=?',(day,provider)).fetchone()
            cooldown=db.execute('SELECT until FROM provider_cooldowns WHERE provider=?',(provider,)).fetchone()
        used=usage[0] if usage else 0
        remaining=max(0,math.ceil(cooldown[0]-time.time())) if cooldown else 0
        return {'local_budget_day_utc':day,'local_calls_today':used,'local_daily_cap':cap,'local_remaining':max(0,cap-used) if cap is not None else None,'local_budget_enforced':cap is not None,
                'cooldown_seconds':remaining,'cooldown_until_utc':datetime.fromtimestamp(cooldown[0],timezone.utc).isoformat() if remaining else None,
                'provider_balance_known':False}

    def worker_lock(self, owner, release=False, name="media"):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if release:
                db.execute("DELETE FROM worker_locks WHERE name=? AND owner=?",(name,owner));return
            row=db.execute("SELECT owner,expires FROM worker_locks WHERE name=?",(name,)).fetchone()
            if row and row["owner"]!=owner and row["expires"]>time.time():raise Held("worker_busy","Another production worker holds the media lease.")
            db.execute("INSERT INTO worker_locks(name,owner,expires) VALUES(?,?,?) ON CONFLICT(name) DO UPDATE SET owner=excluded.owner,expires=excluded.expires",(name,owner,time.time()+180))

    def reset(self, job_id, stage="research"):
        if stage not in STAGES: raise ValueError("Unknown stage")
        job=self.get(job_id)
        with self.connect() as db:
            if db.execute("SELECT 1 FROM uploads WHERE job_id=?",(job_id,)).fetchone():
                raise Held("upload_exists","This job has an upload record. Reconcile it and create a new job for changed content.")
        if job["lease_until"] and job["lease_until"]>time.time(): raise Held("job_busy","Pause/finish the active worker first.")
        kept={k:v for k,v in job["artifacts"].items() if k in STAGES[:STAGES.index(stage)]}
        self.update(job_id,status="queued",stage=stage,artifacts=kept,error_code=None,message=None,retry_at=None,approval_hash=None)
        self.event(job_id,"reset",{"stage":stage})


def load_env_file(path):
    if not path: return
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if not line or line.startswith("#"): continue
        key,sep,value=line.partition("=")
        if sep and re.fullmatch(r"[A-Z][A-Z0-9_]*",key):
            os.environ.setdefault(key,value.strip().strip("\"'"))
