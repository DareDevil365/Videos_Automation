"use strict";
const $ = id => document.getElementById(id);
const state = {project:null,id:null,selected:0,assets:[],formats:[],projects:[],jobs:[],token:"",dirty:false,filter:"all",job:null};
let previewTimer, previewRunning=false, previewPending=false, previewRevision=0, toastTimer;
const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const clone = value => JSON.parse(JSON.stringify(value));
const seconds = () => state.project.scenes.reduce((sum,s)=>sum+Number(s.duration),0);
const scene = () => state.project.scenes[state.selected];

function toast(message,error=false){
  $("toast").textContent=message; $("toast").classList.toggle("error",error); $("toast").hidden=false;
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>$("toast").hidden=true,error?7000:3000);
}
async function api(path,options={}){
  const response=await fetch(path,{...options,headers:{"X-Editor-Token":state.token,...(options.body instanceof File?{}:{"Content-Type":"application/json"}),...options.headers}});
  const result=await response.json();
  if(!response.ok) throw new Error(result.error || `Request failed (${response.status})`);
  return result;
}
function changed(){
  state.dirty=true; $("save-state").textContent="Unsaved changes · draft kept in browser";
  keepDraft();
  renderTimeline(); updateSummary(); schedulePreview();
}
function keepDraft(){
  try{localStorage.setItem("shorts-studio-draft",JSON.stringify({project:state.project,id:state.id,selected:state.selected}));}catch{}
}
function updateSummary(){
  $("project-name").value=state.project.name;
  $("format-name").textContent=state.formats.find(f=>f.id===state.project.format)?.name || "Your format";
  $("resolution-label").textContent=state.project.resolution==="1080p"?"1080 × 1920":"720 × 1280";
  $("total-duration").textContent=`${seconds().toFixed(1)} seconds total`;
  $("scene-count").textContent=state.project.scenes.length;
  $("scene-counter").textContent=`Scene ${String(state.selected+1).padStart(2,"0")}`;
  $("preview-time").max=Math.max(0,scene().duration-.01);
  $("preview-time").value=Math.min(Number($("preview-time").value),Number($("preview-time").max));
  $("time-label").textContent=`${Number($("preview-time").value).toFixed(1)}s / ${Number(scene().duration).toFixed(1)}s`;
}
function renderFormats(){
  $("formats").innerHTML=state.formats.map(f=>`<button class="format-card ${state.project?.format===f.id?"active":""}" data-format="${f.id}" title="${escapeHTML(f.description)}" aria-pressed="${state.project?.format===f.id}"><div class="format-graphic ${f.icon}" aria-hidden="true"><span></span><span></span><span></span></div><strong>${escapeHTML(f.name)}</strong></button>`).join("");
  $("formats").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>loadTemplate(button.dataset.format)));
}
async function loadTemplate(id){
  try{
    if(state.project && state.dirty) await save(false);
    state.project=await api(`/api/templates/${id}`); state.id=null; state.selected=0;
    $("preview-time").value=state.project.scenes[0].duration*.7;
    renderAll(); changed();
  }catch(error){toast(error.message,true);}
}
function renderAssets(){
  $("asset-count").textContent=state.assets.length;
  const assets=state.assets.filter(a=>state.filter==="all" || a.kind===state.filter);
  $("assets").innerHTML=assets.map(a=>`<button class="asset" data-asset="${a.id}" title="Use ${escapeHTML(a.name)} in the current scene">${a.kind==="image"?`<img src="/media/assets/${a.id}" alt="">`:`<span class="asset-placeholder">${a.kind==="audio"?"♫":"▶"}</span>`}<span class="asset-text"><span class="asset-name">${escapeHTML(a.name)}</span><span class="asset-detail">${a.kind.toUpperCase()}${a.duration?` · ${a.duration.toFixed(1)}s`:""}${a.demo?" · DEMO":""}</span></span></button>`).join("") || '<p class="empty-note">Import media to begin.</p>';
  $("assets").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>{
    const asset=state.assets.find(a=>a.id===button.dataset.asset);
    if(state.project.format==="chat" && asset.kind!=="audio"){toast("Chat scenes use the Messages field. Choose another format for images or clips.");return;}
    if(asset.kind==="audio") state.project.music=asset.id;
    else {scene().media=asset.id; scene().media_start=0;}
    fillFields(); changed(); toast(asset.kind==="audio"?"Added as background music":"Added to this scene");
  }));
  fillAssetOptions();
}
function fillAssetOptions(){
  for(const id of ["scene-media","scene-secondary","narration","music"]){
    const audio=id==="narration" || id==="music";
    $(id).innerHTML=`<option value="">${audio?(id==="music"?"No background music":"No voiceover"):"No media"}</option>`+
      state.assets.filter(a=>audio?a.has_audio:a.kind!=="audio").map(a=>`<option value="${a.id}">${escapeHTML(a.name)}</option>`).join("");
  }
}
function renderTimeline(){
  if(!state.project) return;
  $("timeline").innerHTML=state.project.scenes.map((s,i)=>`<button class="scene-tile ${i===state.selected?"active":""}" data-scene="${i}" aria-label="Select scene ${i+1}: ${escapeHTML(s.title)}" aria-pressed="${i===state.selected}"><span class="scene-tile-top"><span>${String(i+1).padStart(2,"0")}</span><span>${Number(s.duration).toFixed(1)}s</span></span><strong>${escapeHTML(s.title || "Untitled scene")}</strong><p>${escapeHTML(s.text || "Add your story")}</p></button>`).join("");
  $("timeline").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>selectScene(Number(button.dataset.scene))));
}
function selectScene(index){
  state.selected=index; $("preview-time").value=scene().duration*.7;
  fillFields(); renderTimeline(); updateSummary(); schedulePreview();
  keepDraft();
}
function fillFields(){
  if(!state.project) return;
  const s=scene(),p=state.project;
  const sceneFields={"scene-duration":"duration","scene-title":"title","scene-text":"text","scene-media":"media","scene-secondary":"secondary_media","media-start":"media_start","secondary-start":"secondary_start","scene-fit":"fit","focus-x":"focus_x","focus-y":"focus_y"};
  for(const [id,key] of Object.entries(sceneFields)) $(id).value=s[key];
  $("source-audio").checked=s.source_audio;
  $("scene-messages").value=s.messages.map(m=>`${m.name}: ${m.text}`).join("\n");
  for(const [id,key] of Object.entries({"accent":"accent","background":"background","font-scale":"font_scale","split-ratio":"split_ratio","narration":"narration","music":"music","music-volume":"music_volume","source-volume":"source_volume","resolution":"resolution","fps":"fps"})) $(id).value=p[key];
  $("swap-panels").checked=p.swap_panels;
  const chat=p.format==="chat",split=p.format==="split";
  $("chat-fields").hidden=!chat; $("visual-fields").hidden=chat; $("secondary-field").hidden=!split; $("secondary-start-field").hidden=!split; $("split-fields").hidden=!split;
  $("primary-label").textContent=split?"Primary panel":p.format==="story"?"Background":"Image / clip";
  $("caption-label").textContent=p.format==="punchline"?"Punchline · reveals halfway through":"Caption / takeaway";
  $("caption-help").textContent=["story","split"].includes(p.format)?"Line breaks create sequential caption cues.":"Keep it short enough to read comfortably.";
  $("crop-fields").hidden=s.fit!=="cover" || chat;
  $("delete-scene").disabled=p.scenes.length===1; $("move-left").disabled=state.selected===0; $("move-right").disabled=state.selected===p.scenes.length-1;
  $("add-scene").disabled=p.scenes.length>=30; $("duplicate-scene").disabled=p.scenes.length>=30;
}
function renderAll(){renderFormats(); renderAssets(); renderTimeline(); fillFields(); updateSummary(); schedulePreview(); keepDraft();}
function schedulePreview(){
  ++previewRevision; clearTimeout(previewTimer); previewTimer=setTimeout(updatePreview,400);
}
async function updatePreview(){
  if(!state.project) return;
  if(previewRunning){previewPending=true;return;}
  const revision=previewRevision; previewRunning=true; previewPending=false;
  $("preview-loading").hidden=false; $("preview-loading").textContent="Updating preview…";
  try{
    const result=await api("/api/preview",{method:"POST",body:JSON.stringify({project:state.project,scene:state.selected,at:Number($("preview-time").value)})});
    if(revision===previewRevision){
      $("preview").onload=()=>$("preview-loading").hidden=true;
      $("preview").src=result.url;
      if($("preview").complete && $("preview").naturalWidth) $("preview-loading").hidden=true;
    }
  }catch(error){if(revision===previewRevision) $("preview-loading").textContent=error.message;}
  finally{previewRunning=false;if(previewPending || revision!==previewRevision) {clearTimeout(previewTimer);previewTimer=setTimeout(updatePreview,100);}}
}
async function save(notify=true){
  const saved=await api("/api/projects",{method:"POST",body:JSON.stringify({id:state.id,project:state.project})});
  state.id=saved.id; state.project=saved.project; state.dirty=false;
  $("save-state").textContent="Saved on this computer";
  keepDraft();
  const existing=state.projects.find(p=>p.id===saved.id);
  if(existing) existing.name=state.project.name; else state.projects.unshift({id:saved.id,name:state.project.name});
  if(notify) toast("Project saved");
}
async function upload(files){
  files=Array.from(files);
  document.body.classList.add("uploading");
  for(const [index,file] of Array.from(files).entries()){
    $("upload-status").textContent=`Importing ${index+1} of ${files.length}: ${file.name}`;
    try{
      const asset=await api("/api/assets",{method:"POST",body:file,headers:{"X-Filename":encodeURIComponent(file.name)}});
      state.assets.unshift(asset); renderAssets(); fillFields();
      if(!scene().media && asset.kind!=="audio"){scene().media=asset.id;fillFields();changed();}
    }catch(error){toast(`${file.name}: ${error.message}`,true);}
  }
  $("upload-status").textContent="Your files stay on this computer."; document.body.classList.remove("uploading");
}
function parseMessages(value){
  const sides=new Map();
  return value.split("\n").filter(line=>line.trim()).map(line=>{
    const colon=line.indexOf(":");const name=colon<0?"":line.slice(0,colon).trim();const message=colon<0?line.trim():line.slice(colon+1).trim();
    if(!sides.has(name)) sides.set(name,sides.size%2===0?"left":"right");
    return {name,text:message,side:sides.get(name)};
  });
}
function bindFields(){
  const sceneFields={"scene-title":"title","scene-text":"text","scene-media":"media","scene-secondary":"secondary_media","scene-duration":"duration","media-start":"media_start","secondary-start":"secondary_start","scene-fit":"fit","focus-x":"focus_x","focus-y":"focus_y"};
  const numeric=new Set(["duration","media_start","secondary_start","focus_x","focus_y"]);
  for(const [id,key] of Object.entries(sceneFields)) $(id).addEventListener($(id).tagName==="SELECT" || $(id).type==="number"?"change":"input",()=>{
    const value=numeric.has(key)?Number($(id).value):$(id).value;
    if(numeric.has(key) && !Number.isFinite(value)) return;
    scene()[key]=value;
    if(key==="media") scene().media_start=0;
    if(key==="secondary_media") scene().secondary_start=0;
    if(["media","secondary_media","fit"].includes(key)) fillFields();
    changed();
  });
  const fields={"accent":"accent","background":"background","font-scale":"font_scale","split-ratio":"split_ratio","narration":"narration","music":"music","music-volume":"music_volume","source-volume":"source_volume","resolution":"resolution","fps":"fps"};
  for(const [id,key] of Object.entries(fields)) $(id).addEventListener("input",()=>{
    state.project[key]=["font_scale","split_ratio","music_volume","source_volume","fps"].includes(key)?Number($(id).value):$(id).value; changed();
  });
  $("source-audio").addEventListener("change",()=>{scene().source_audio=$("source-audio").checked;changed();});
  $("swap-panels").addEventListener("change",()=>{state.project.swap_panels=$("swap-panels").checked;changed();});
  $("project-name").addEventListener("input",()=>{state.project.name=$("project-name").value;changed();});
  $("scene-messages").addEventListener("input",()=>{scene().messages=parseMessages($("scene-messages").value);changed();});
}
function renderJob(job){
  const panel=$("export-panel");panel.hidden=false;
  const active=["queued","running"].includes(job.status);
  $("export-video").disabled=active;
  const video=job.status==="complete"?`<video controls preload="metadata" src="${job.url}" poster="${job.cover}" aria-label="Exported video"></video><div class="download-links"><a href="${job.url}" download="${escapeHTML(job.name)}.mp4">↓ MP4 video</a><a href="${job.cover}" download>Cover</a><a href="/media/jobs/${job.id}/video.srt">Captions</a><a href="/media/jobs/${job.id}/video.project.json">Project JSON</a><a href="/media/jobs/${job.id}/video.manifest.json">Export details</a></div>`:"";
  const existingVideo=panel.querySelector("video");
  if(existingVideo && panel.dataset.job===job.id && job.status==="complete") return;
  panel.dataset.job=job.id;
  panel.innerHTML=`<div class="export-heading"><strong>${job.status==="complete"?"Your video is ready":job.status==="failed"?"Export needs attention":job.status==="cancelled"?"Export cancelled":escapeHTML(job.name)}</strong>${active?'<button class="text-button" id="cancel-export">Cancel</button>':`<span class="muted">${escapeHTML(job.status)}</span>`}</div><p>${escapeHTML(job.message)}</p>${active?`<div class="progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(job.progress*100)}"><div style="width:${Math.max(2,job.progress*100)}%"></div></div>`:""}${video}<div class="export-history">${state.jobs.filter(j=>j.id!==job.id).slice(0,4).map(j=>`<button data-job="${j.id}">${escapeHTML(j.name)} · ${escapeHTML(j.status)}</button>`).join("")}</div>`;
  $("cancel-export")?.addEventListener("click",async()=>{try{await api(`/api/jobs/${job.id}/cancel`,{method:"POST",body:"{}"});}catch(e){toast(e.message,true);}});
  panel.querySelectorAll("[data-job]").forEach(b=>b.addEventListener("click",()=>{state.job=b.dataset.job;renderJob(state.jobs.find(j=>j.id===state.job));}));
}
async function pollJobs(){
  try{
    state.jobs=await api("/api/jobs");
    const job=state.jobs.find(j=>j.id===state.job);
    if(job) renderJob(job);
  }catch{}
}
async function exportVideo(){
  $("export-video").disabled=true;
  try{
    await save(false);
    const job=await api("/api/renders",{method:"POST",body:JSON.stringify({project:state.project})});
    state.job=job.id;state.jobs.unshift(job);renderJob(job);$("export-panel").scrollIntoView({behavior:"smooth",block:"nearest"});
  }catch(error){$("export-video").disabled=false;toast(error.message,true);}
}
function bindActions(){
  $("save-project").addEventListener("click",()=>save().catch(e=>toast(e.message,true)));
  $("export-video").addEventListener("click",exportVideo);
  $("refresh-preview").addEventListener("click",schedulePreview);
  $("preview-time").addEventListener("input",()=>{updateSummary();schedulePreview();});
  $("add-scene").addEventListener("click",()=>{if(state.project.scenes.length>=30)return;const s=clone(scene());s.title="Your next idea";s.text="Add the next part of your story.";state.project.scenes.splice(state.selected+1,0,s);state.selected++;renderAll();changed();});
  $("duplicate-scene").addEventListener("click",()=>{if(state.project.scenes.length>=30)return;state.project.scenes.splice(state.selected+1,0,clone(scene()));state.selected++;renderAll();changed();});
  $("delete-scene").addEventListener("click",()=>{if(state.project.scenes.length===1)return;state.project.scenes.splice(state.selected,1);state.selected=Math.min(state.selected,state.project.scenes.length-1);renderAll();changed();});
  for(const [id,delta] of [["move-left",-1],["move-right",1]]) $(id).addEventListener("click",()=>{const other=state.selected+delta;if(other<0||other>=state.project.scenes.length)return;[state.project.scenes[state.selected],state.project.scenes[other]]=[state.project.scenes[other],state.project.scenes[state.selected]];state.selected=other;renderAll();changed();});
  $("media-upload").addEventListener("change",event=>{upload(event.target.files);event.target.value="";});
  $("dropzone").addEventListener("dragover",event=>{event.preventDefault();$("dropzone").classList.add("dragover");});
  $("dropzone").addEventListener("dragleave",()=>$("dropzone").classList.remove("dragover"));
  $("dropzone").addEventListener("drop",event=>{event.preventDefault();$("dropzone").classList.remove("dragover");upload(event.dataTransfer.files);});
  document.querySelectorAll("[data-filter]").forEach(b=>b.addEventListener("click",()=>{state.filter=b.dataset.filter;document.querySelectorAll("[data-filter]").forEach(x=>x.classList.toggle("active",x===b));renderAssets();fillFields();}));
  document.querySelectorAll("[data-tab]").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll("[data-tab]").forEach(x=>x.classList.toggle("active",x===b));$("scene-panel").hidden=b.dataset.tab!=="scene";$("style-panel").hidden=b.dataset.tab!=="style";}));
  $("download-project").addEventListener("click",()=>{const blob=new Blob([JSON.stringify(state.project,null,2)],{type:"application/json"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="shorts-project.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  $("open-project").addEventListener("click",()=>{
    $("saved-projects").innerHTML=state.projects.map(p=>`<button class="saved-project" data-project="${p.id}"><span>${escapeHTML(p.name)}</span><span>↗</span></button>`).join("")||'<p class="empty-note">No saved projects yet.</p>';
    $("saved-projects").querySelectorAll("button").forEach(b=>b.addEventListener("click",async()=>{try{if(state.dirty) await save(false);const result=await api(`/api/projects/${b.dataset.project}`);state.id=result.id;state.project=result.project;state.selected=0;state.dirty=false;renderAll();$("save-state").textContent="Saved on this computer";$("project-dialog").close();}catch(e){toast(e.message,true);}}));
    $("project-dialog").showModal();
  });
  $("close-project-dialog").addEventListener("click",()=>$("project-dialog").close());
  $("project-import").addEventListener("change",async event=>{try{const file=event.target.files[0];if(!file)return;const json=JSON.parse(await file.text());if(state.dirty)await save(false);const saved=await api("/api/projects",{method:"POST",body:JSON.stringify({project:json.project||json})});state.project=saved.project;state.id=saved.id;state.selected=0;state.dirty=false;renderAll();$("project-dialog").close();toast("Project imported. Its media must be in this workspace.");}catch(e){toast(e.message,true);}finally{event.target.value="";}});
  document.addEventListener("keydown",event=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="s"){event.preventDefault();save().catch(e=>toast(e.message,true));}});
}
async function init(){
  try{
    const data=await api("/api/bootstrap");Object.assign(state,{token:data.token,assets:data.assets,formats:data.formats,projects:data.projects,jobs:data.jobs});
    try{const draft=JSON.parse(localStorage.getItem("shorts-studio-draft"));if(draft?.project?.version===1 && draft.project.scenes?.length){state.project=draft.project;state.id=draft.id;state.selected=Math.min(draft.selected||0,draft.project.scenes.length-1);}}catch{}
    if(!state.project)state.project=await api("/api/templates/story");
    bindFields();bindActions();renderAll();
    if(state.jobs.length){state.job=state.jobs[0].id;renderJob(state.jobs[0]);}
    if(!data.capabilities.ffmpeg||!data.capabilities.ffprobe)toast("FFmpeg and ffprobe are required to preview and export.",true);
    setInterval(pollJobs,1300);
  }catch(error){$("preview-loading").textContent=error.message;toast(error.message,true);}
}
init();
