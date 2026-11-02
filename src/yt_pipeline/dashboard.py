from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from .core import Workspace, Held, STAGES, load_env_file
from .pipeline import Pipeline
from .cli import doctor, config_set
from .assets import register_asset
from .monitor import alerts, supervise, growth_report, incident
from .research import discover
from .publishing import publish
from .benchmarks import benchmark


class Production:
    def __init__(self, root):
        self.ws=Workspace(root);self.pool=ThreadPoolExecutor(max_workers=1)
        if Path('.env').is_file():load_env_file('.env')
        self.pending=set()

    def close(self):self.pool.shutdown(wait=True,cancel_futures=True)

    def status(self):
        jobs=self.ws.jobs()
        for job in jobs:
            rendered=job['artifacts'].get('render')
            if rendered:
                item=json.loads(Path(rendered['path']).read_text(encoding='utf-8'))
                job['outputs']={key:f"/production/files/{job['id']}/{key}" for key in ('video','cover','captions') if Path(item[key]).is_file()}
        return {'doctor':doctor(self.ws),'jobs':jobs,'alerts':alerts(self.ws),'profiles':self.ws.config()['channels'],
                'stages':STAGES,'pending':list(self.pending)}

    def run(self, job_id):
        self.ws.get(job_id)
        if job_id in self.pending:return {'queued':job_id}
        self.pending.add(job_id)
        def work():
            try:Pipeline(self.ws).run(job_id)
            except Held as exc:self.ws.alert(job_id+':'+exc.code,job_id,str(exc))
            finally:self.pending.discard(job_id)
        self.pool.submit(work)
        return {'queued':job_id}

    def action(self, body):
        action=body.get('action')
        if action=='create':
            request=body.get('request')
            if not isinstance(request,dict):raise ValueError('A job request must be a JSON object.')
            job=self.ws.create(body['channel'],request)
            if body.get('run',True):self.run(job['id'])
            return job
        if action=='run':return self.run(body['job'])
        if action=='retry':
            job=self.ws.get(body['job']);self.ws.reset(job['id'],body.get('stage') or (job['stage'] if job['stage'] in STAGES else 'research'))
            return self.run(job['id'])
        if action=='cancel':
            self.ws.get(body['job']);self.ws.update(body['job'],status='cancelled',message='Cancelled by owner');return {'cancelled':body['job']}
        if action=='config':return config_set(self.ws,body['path'],body['value'])
        if action=='asset':
            asset=register_asset(self.ws,Path(body['file']).resolve(),body['source_type'],{'reference':body['evidence']},test_only=body.get('test_only',False))
            config=self.ws.config();config['channels'][body['channel']]['footage_ids'].append(asset['id']);self.ws.save_config(config)
            return asset
        if action=='acknowledge':return alerts(self.ws,body['key'])
        if action=='supervise':return supervise(self.ws)
        if action=='report':return growth_report(self.ws,body['channel'])
        if action=='discover':return discover(self.ws,body['channel'],body.get('query',''))
        if action=='benchmark':return benchmark(self.ws,body['channel'],body.get('query',''))
        if action=='incident':return incident(self.ws,body['channel'],body['message'])
        if action=='publish_preview':return publish(self.ws,body['job'])
        raise ValueError('Unknown production action.')

    def output(self,job_id,kind):
        job=self.ws.get(job_id)
        if kind not in ('video','cover','captions','package'):raise ValueError('Unknown output')
        stage='package' if kind=='package' else 'render'
        if stage not in job['artifacts']:raise ValueError('This output is not ready.')
        path=Path(job['artifacts'][stage]['path'])
        if kind!='package':path=Path(json.loads(path.read_text(encoding='utf-8'))[kind])
        if not path.resolve().is_relative_to(self.ws.job_dir(job_id)):raise ValueError('Output is outside its job directory.')
        return path
