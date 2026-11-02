let token='',state=null;
const $=s=>document.querySelector(s);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function notice(message){$('#notice').textContent=message;$('#notice').hidden=false;}
async function action(body){const r=await fetch('/api/production',{method:'POST',headers:{'Content-Type':'application/json','X-Editor-Token':token},body:JSON.stringify(body)});const value=await r.json();if(!r.ok)throw Error(value.error||'Request failed');return value;}
async function safe(fn){try{await fn()}catch(e){notice(e.message)}}
async function refresh(){const r=await fetch('/api/production');if(!r.ok)throw Error('Cannot reach production server');state=await r.json();render();}
function render(){
 const d=state.doctor,active=state.jobs.filter(j=>['queued','running'].includes(j.status)).length;
 $('#summary').textContent=`${active} active · ${state.jobs.filter(j=>j.status==='ready').length} ready · ${state.alerts.filter(a=>!a.acknowledged).length} new alerts`;
 $('#job-count').textContent=`${state.jobs.length} jobs`;
 $('#jobs').innerHTML=state.jobs.map(j=>`<article class="job"><div class="job-head"><div><h3>${esc(j.request.topic||j.request.brief?.title||'Imported production job')}</h3><div class="meta">${esc(j.channel)} · ${esc(j.id.slice(0,8))} · ${esc(new Date(j.created_at).toLocaleString())}</div></div><span class="tag ${esc(j.status)}">${esc(j.status.replaceAll('_',' '))}</span></div><div class="steps">${state.stages.map(s=>`<span class="step ${j.artifacts[s]?'done':''}">${esc(s)}</span>`).join('')}</div><p>${esc(j.message||'Waiting for a worker')}${j.error_code?` <strong>(${esc(j.error_code)})</strong>`:''}</p><div class="actions">${['held','failed','retry_wait','cancelled'].includes(j.status)?`<button data-action="retry" data-id="${j.id}">Resume / retry</button>`:''}${j.status==='queued'?`<button data-action="run" data-id="${j.id}">Run</button>`:''}${['queued','running'].includes(j.status)?`<button data-action="cancel" data-id="${j.id}">Cancel</button>`:''}${Object.entries(j.outputs||{}).map(([k,url])=>`<a href="${esc(url)}" target="_blank">${esc(k)} ↗</a>`).join('')}${j.artifacts.package?`<a href="/production/files/${j.id}/package">Metadata ↓</a><button data-action="publish_preview" data-id="${j.id}">Upload preview</button>`:''}</div></article>`).join('')||'<p class="empty">No jobs yet. Start with one focused topic or import a prepared request.</p>';
 $('#checks').innerHTML=[['Gemini key',d.gemini_key_present],['Local voice model',d.voice_model&&d.piper_runtime],['FFmpeg / ffprobe',d.ffmpeg&&d.ffprobe],['Entertainment footage',d.channels.entertainment.footage_count>0],['Education OAuth',d.channels.education.oauth_file_present],['Entertainment OAuth',d.channels.entertainment.oauth_file_present]].map(([label,ok])=>`<div class="connection"><span>${label}</span><strong>${ok?'Ready':'Pending'}</strong></div>`).join('');
 $('#free-tier').checked=d.gemini_free_tier_confirmed;
 $('#profiles').innerHTML=Object.entries(state.profiles).map(([name,p])=>`<div class="profile"><div><strong>${esc(p.name)}</strong><span>${esc(p.publication_mode)} publishing · ${p.daily_cap}/day cap</span></div><button data-pause="${esc(name)}" data-value="${!p.paused}">${p.paused?'Resume':'Pause'}</button></div>`).join('');
 $('#alerts').innerHTML=state.alerts.filter(a=>!a.acknowledged).map(a=>`<div class="alert"><button data-ack="${esc(a.key)}">Acknowledge</button>${esc(a.message)}</div>`).join('')||'<p class="hint">No unacknowledged alerts.</p>';
}
document.addEventListener('click',e=>safe(async()=>{
 const b=e.target.closest('button');if(!b)return;
 if(b.dataset.action){const result=await action({action:b.dataset.action,job:b.dataset.id});if(b.dataset.action==='publish_preview')notice(JSON.stringify(result));await refresh();}
 if(b.dataset.pause){await action({action:'config',path:`channels.${b.dataset.pause}.paused`,value:b.dataset.value==='true'});await refresh();}
 if(b.dataset.ack){await action({action:'acknowledge',key:b.dataset.ack});await refresh();}
}));
$('#create').onsubmit=e=>{e.preventDefault();safe(async()=>{const f=new FormData(e.target),raw=f.get('json').trim();const request=raw?JSON.parse(raw):{topic:f.get('topic'),source_urls:f.get('sources').split('\n').map(s=>s.trim()).filter(Boolean)};await action({action:'create',channel:f.get('channel'),request});notice('Job created. Saved stages remain available if an input is missing.');await refresh();});};
$('#asset').onsubmit=e=>{e.preventDefault();safe(async()=>{await action({action:'asset',...Object.fromEntries(new FormData(e.target))});notice('Footage registered. Resume a held entertainment job when ready.');await refresh();});};
$('#incident').onsubmit=e=>{e.preventDefault();safe(async()=>{await action({action:'incident',...Object.fromEntries(new FormData(e.target))});e.target.reset();await refresh();});};
$('#free-tier').onchange=e=>safe(async()=>{await action({action:'config',path:'gemini.free_tier_confirmed',value:e.target.checked});await refresh();});
$('#refresh').onclick=()=>safe(refresh);
$('#scan').onclick=()=>safe(async()=>{await action({action:'supervise'});await refresh()});
$('#growth').onclick=()=>safe(async()=>{const result=await action({action:'report',channel:$('#channel').value});$('#report').textContent=JSON.stringify(result,null,2);$('#report').hidden=false;});
$('#benchmark').onclick=()=>safe(async()=>{const result=await action({action:'benchmark',channel:$('#channel').value,query:$('#benchmark-query').value});$('#report').textContent=JSON.stringify(result,null,2);$('#report').hidden=false;});
$('#example').onclick=()=>safe(async()=>{const r=await fetch('/api/production-example');if(!r.ok)throw Error('Example unavailable');const value=await r.json();$('#create [name=json]').value=JSON.stringify(value,null,2);$('#create [name=topic]').value=value.brief.title;$('#channel').value='education';});
safe(async()=>{const r=await fetch('/api/bootstrap');token=(await r.json()).token;await refresh();setInterval(()=>safe(refresh),5000)});
