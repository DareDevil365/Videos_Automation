"use strict";
const $=id=>document.getElementById(id);
const state={project:null,id:null,shot:0,assets:[],presets:[],projects:[],jobs:[],job:null,token:""};
const copy=value=>JSON.parse(JSON.stringify(value));
const shot=()=>state.project.scenes[state.shot];
const config=()=>state.project.composition;
const esc=value=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const total=()=>state.project.scenes.reduce((sum,s)=>sum+s.duration,0);
let timer,revision=0,previewBusy=false,previewAgain=false,toastTimer;
function toast(message,error=false){$("toast").textContent=message;$("toast").classList.toggle("error",error);$("toast").hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$("toast").hidden=true,error?8000:3500);}
async function api(path,body){const response=await fetch(path,{method:body===undefined?"GET":"POST",headers:{"X-Editor-Token":state.token,"Content-Type":"application/json"},body:body===undefined?undefined:JSON.stringify(body)});const data=await response.json();if(!response.ok)throw Error(data.error||"Request failed");return data;}
function keep(){try{localStorage.setItem("shorts-compositor-draft",JSON.stringify({project:state.project,id:state.id,shot:state.shot}));}catch{}}
function changed(){keep();$("save-state").textContent="Draft kept locally";summary();timeline();schedule();}
function summary(){
  $("name").value=state.project.name;$("format-name").textContent=state.presets.find(p=>p.id===state.project.format)?.name||"Composition";
  $("size").textContent=state.project.resolution==="1080p"?"1080 × 1920":"720 × 1280";
  $("total").textContent=`${total().toFixed(1)} seconds`;
  $("time").max=Math.max(0,shot().duration-.001);$("time").value=Math.min(Number($("time").value),Number($("time").max));
  $("shot-time").textContent=`${Number($("time").value).toFixed(1)}s`;$("shot-end").textContent=`${shot().duration.toFixed(1)}s`;
  $("remove-shot").disabled=state.project.scenes.length===1;$("add-shot").disabled=state.project.scenes.length>=30;
}
function presets(){
  $("presets").innerHTML=state.presets.map(p=>`<button data-preset="${p.id}" class="${p.id===state.project.format?"active":""}" aria-pressed="${p.id===state.project.format}" title="${esc(p.description)}">${esc(p.name)}</button>`).join("");
  $("presets").querySelectorAll("button").forEach(button=>button.onclick=async()=>{
    try{
      const fresh=await api(`/api/templates/${button.dataset.preset}`);
      // Switching layout keeps actual input files and timing; it changes geometry only.
      state.project.format=fresh.format;state.project.composition={...config(),x:fresh.composition.x,y:fresh.composition.y,width:fresh.composition.width,height:fresh.composition.height,foreground_fit:fresh.composition.foreground_fit};
      if(fresh.format==="focus")config().audio_source="background";
      fill();presets();changed();
    }catch(error){toast(error.message,true);}
  });
}
function timeline(){
  $("shots").innerHTML=state.project.scenes.map((s,i)=>`<button data-shot="${i}" class="${i===state.shot?"active":""}" aria-label="Select shot ${i+1}" aria-pressed="${i===state.shot}">${String(i+1).padStart(2,"0")}<small>${s.duration.toFixed(1)} seconds</small></button>`).join("");
  $("shots").querySelectorAll("button").forEach(button=>button.onclick=()=>{state.shot=Number(button.dataset.shot);$("time").value=0;fill();summary();timeline();keep();schedule();});
}
function assets(){
  const available=state.assets.filter(a=>$("show-demo").checked||!a.demo);
  for(const id of ["background-media","foreground-media","music"]){
    const audio=id==="music";
    $(id).innerHTML=`<option value="">${audio?"No music":"Choose an imported file"}</option>`+available.filter(a=>audio?a.has_audio:a.kind!=="audio").map(a=>`<option value="${a.id}">${esc(a.name)}${a.duration?` · ${a.duration.toFixed(1)}s`:""}</option>`).join("");
    const selected=id==="music"?state.project.music:shot()[id==="background-media"?"media":"secondary_media"];
    // A previously selected test asset stays visible; no asset is silently substituted.
    if(selected&&!available.some(a=>a.id===selected)){
      const a=state.assets.find(a=>a.id===selected);if(a)$(id).add(new Option(`${a.name} · selected test asset`,a.id));
    }
  }
}
function fill(){
  const s=shot(),c=config(),p=state.project;
  const fields={"background-media":s.media,"foreground-media":s.secondary_media,"background-start":s.media_start,"foreground-start":s.secondary_start,"background-fit":s.fit,"foreground-fit":c.foreground_fit,"duration":s.duration,"box-x":c.x*100,"box-y":c.y*100,"box-width":c.width*100,"box-height":c.height*100,"border-width":c.border_width,"border-color":c.border_color,"glow":c.glow,"focus-x":s.focus_x,"focus-y":s.focus_y,"music":p.music,"music-volume":p.music_volume,"source-volume":p.source_volume,"audio-source":c.audio_source,"effect":c.effect,"effect-at":s.effect_at,"cta-text":c.cta_text,"cta-at":c.cta_at,"cta-duration":c.cta_duration,"resolution":p.resolution,"fps":p.fps};
  assets();for(const [id,value] of Object.entries(fields))$(id).value=value;
  $("cta").checked=c.cta;$("cta-options").hidden=!c.cta;
  const stack=p.format==="stack",focus=p.format==="focus";
  $("background-fit").disabled=focus;if(focus)$("background-fit").value="cover";
  $("foreground-slot").hidden=focus;$("background-label").textContent=focus?"Main clip":stack?"Bottom block":"Background footage";
  for(const id of ["box-x","box-y","box-width"])$(id).disabled=stack;
  $("layout-note").textContent=stack?"Height controls the top block. The background fills the remaining bottom block.":focus?"The sharp copy of your main clip stays inside this box; a blurred copy fills the background.":"The foreground keeps its aspect ratio and anchors at the top of this box.";
}
function schedule(){revision++;clearTimeout(timer);timer=setTimeout(preview,350);}
async function preview(){
  if(previewBusy){previewAgain=true;return;}if(!state.project)return;
  previewBusy=true;previewAgain=false;const current=revision;$("loading").hidden=false;$("loading").textContent="Rendering frame…";
  try{const result=await api("/api/preview",{project:state.project,scene:state.shot,at:Number($("time").value)});if(current===revision){$("preview").onload=()=>$("loading").hidden=true;$("preview").src=result.url;if($("preview").complete&&$("preview").naturalWidth)$("loading").hidden=true;}}
  catch(error){if(current===revision)$("loading").textContent=error.message;}
  finally{previewBusy=false;if(previewAgain||current!==revision){clearTimeout(timer);timer=setTimeout(preview,100);}}
}
async function save(){const result=await api("/api/projects",{id:state.id,project:state.project});state.project=result.project;state.id=result.id;keep();$("save-state").textContent="Saved on this computer";const item=state.projects.find(p=>p.id===state.id);if(item)item.name=state.project.name;else state.projects.unshift({id:state.id,name:state.project.name});return result;}
async function importMedia(file,slot){
  if(!file)return;document.body.classList.add("busy");$("import-status").textContent=`Importing ${file.name}…`;
  try{const response=await fetch("/api/assets",{method:"POST",headers:{"X-Editor-Token":state.token,"X-Filename":encodeURIComponent(file.name)},body:file});const a=await response.json();if(!response.ok)throw Error(a.error);state.assets.unshift(a);if(slot==="music"){if(!a.has_audio)throw Error("Choose a file containing audio.");state.project.music=a.id;}else{if(a.kind==="audio")throw Error("Choose an image or clip for this slot.");shot()[slot]=a.id;shot()[slot==="media"?"media_start":"secondary_start"]=0;}fill();changed();$("import-status").textContent=`Imported ${file.name}.`;}catch(error){toast(error.message,true);$("import-status").textContent=error.message;}finally{document.body.classList.remove("busy");}
}
function download(value,name){const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function renderJob(job){
  const result=$("result");result.hidden=false;const active=["queued","running"].includes(job.status);$("export").disabled=active;
  if(result.dataset.job===job.id&&job.status==="complete"&&result.querySelector("video"))return;
  result.dataset.job=job.id;
  result.innerHTML=`<div class="result-head"><h2>${job.status==="complete"?"Export ready":esc(job.name)}</h2>${active?'<button id="cancel">Cancel</button>':`<span class="hint">${esc(job.status)}</span>`}</div><p class="result-message">${esc(job.message)}</p>${active?`<div class="meter" role="progressbar" aria-valuenow="${Math.round(job.progress*100)}" aria-valuemin="0" aria-valuemax="100"><div style="width:${Math.max(2,job.progress*100)}%"></div></div>`:""}${job.status==="complete"?`<video controls preload="metadata" src="${job.url}" poster="${job.cover}" aria-label="Exported composition"></video><div class="downloads"><a href="${job.url}" download="composition.mp4">Download MP4</a><a href="${job.cover}" download>Cover frame</a><a href="/media/jobs/${job.id}/video.project.json">Project JSON</a><a href="/media/jobs/${job.id}/video.manifest.json">Render details</a></div>`:""}<div class="history">${state.jobs.filter(j=>j.id!==job.id).slice(0,4).map(j=>`<button data-job="${j.id}">${esc(j.name)} · ${esc(j.status)}</button>`).join("")}</div>`;
  $("cancel")?.addEventListener("click",()=>api(`/api/jobs/${job.id}/cancel`,{}).catch(e=>toast(e.message,true)));
  result.querySelectorAll("[data-job]").forEach(button=>button.onclick=()=>{state.job=button.dataset.job;renderJob(state.jobs.find(j=>j.id===state.job));});
}
function bind(){
  $("new").onclick=async()=>{try{await save();state.project=await api(`/api/templates/${state.project.format}`);state.id=null;state.shot=0;state.job=null;$("result").hidden=true;$("export").disabled=false;$("time").value=0;fill();presets();changed();}catch(error){toast(error.message,true);}};
  const sceneFields={"background-media":["media",false],"foreground-media":["secondary_media",false],"background-start":["media_start",true],"foreground-start":["secondary_start",true],"background-fit":["fit",false],"duration":["duration",true],"focus-x":["focus_x",true],"focus-y":["focus_y",true],"effect-at":["effect_at",true]};
  for(const [id,[key,numeric]] of Object.entries(sceneFields))$(id).addEventListener("input",()=>{shot()[key]=numeric?Number($(id).value):$(id).value;if(key==="media")shot().media_start=0;if(key==="secondary_media")shot().secondary_start=0;changed();});
  const compositionFields={"foreground-fit":"foreground_fit","box-x":"x","box-y":"y","box-width":"width","box-height":"height","border-width":"border_width","border-color":"border_color","glow":"glow","audio-source":"audio_source","effect":"effect","cta-text":"cta_text","cta-at":"cta_at","cta-duration":"cta_duration"};
  for(const [id,key] of Object.entries(compositionFields))$(id).addEventListener("input",()=>{const node=$(id);config()[key]=["number","range"].includes(node.type)?Number(node.value)/(id.startsWith("box-")?100:1):node.value;changed();});
  for(const [id,key] of Object.entries({"music":"music","music-volume":"music_volume","source-volume":"source_volume","resolution":"resolution","fps":"fps"}))$(id).oninput=()=>{state.project[key]=["music_volume","source_volume","fps"].includes(key)?Number($(id).value):$(id).value;changed();};
  $("cta").onchange=()=>{config().cta=$("cta").checked;$("cta-options").hidden=!config().cta;changed();};
  $("name").oninput=()=>{state.project.name=$("name").value;changed();};
  $("time").oninput=()=>{summary();schedule();};$("refresh").onclick=schedule;
  $("show-demo").onchange=fill;
  for(const [id,slot] of [["background-file","media"],["foreground-file","secondary_media"],["music-file","music"]])$(id).onchange=event=>{importMedia(event.target.files[0],slot);event.target.value="";};
  $("match-duration").onclick=()=>{const key=state.project.format==="focus"?"media":"secondary_media";const asset=state.assets.find(a=>a.id===shot()[key])||state.assets.find(a=>a.id===shot().media);if(!asset?.duration){toast("Choose a video clip first.");return;}shot().duration=Math.min(180,asset.duration-shot()[key==="media"?"media_start":"secondary_start"]);if(shot().duration<1){toast("Less than one second remains. Change the clip start.",true);return;}fill();changed();};
  $("save").onclick=()=>save().then(()=>toast("Project saved")).catch(e=>toast(e.message,true));
  $("export").onclick=async()=>{try{$("export").disabled=true;await save();const job=await api("/api/renders",{project:state.project});state.job=job.id;state.jobs.unshift(job);renderJob(job);$("result").scrollIntoView({behavior:"smooth",block:"nearest"});}catch(error){$("export").disabled=false;toast(error.message,true);}};
  $("add-shot").onclick=()=>{if(state.project.scenes.length>=30)return;state.project.scenes.splice(state.shot+1,0,copy(shot()));state.shot++;$("time").value=0;fill();changed();};
  $("remove-shot").onclick=()=>{if(state.project.scenes.length<=1)return;state.project.scenes.splice(state.shot,1);state.shot=Math.min(state.shot,state.project.scenes.length-1);fill();changed();};
  $("download-layout").onclick=()=>{const p=copy(state.project);p.name+=" layout";p.music="";p.narration="";for(const s of p.scenes){s.media="";s.secondary_media="";s.media_start=0;s.secondary_start=0;}download(p,"composition-layout.json");};
  $("download-job").onclick=()=>download(state.project,"composition-project.json");
  $("open").onclick=()=>{$("projects").innerHTML=state.projects.map(p=>`<button class="project-row" data-id="${p.id}">${esc(p.name)}</button>`).join("")||'<p class="hint">No saved projects.</p>';$("projects").querySelectorAll("button").forEach(button=>button.onclick=async()=>{try{const saved=await api(`/api/projects/${button.dataset.id}`);if(!state.presets.some(p=>p.id===saved.project.format)){toast("That is an older card-editor recipe. Its files are preserved; use /legacy to open it.");return;}state.project=saved.project;state.id=saved.id;state.shot=0;fill();presets();changed();$("projects-dialog").close();}catch(e){toast(e.message,true);}});$("projects-dialog").showModal();};
  $("close-dialog").onclick=()=>$("projects-dialog").close();
  $("project-file").onchange=async event=>{try{const file=event.target.files[0];if(!file)return;const raw=JSON.parse(await file.text());const p=raw.project||raw;if(!state.presets.some(f=>f.id===p.format))throw Error("Import a media-composition layout, not a legacy card recipe.");const saved=await api("/api/projects",{project:p});state.project=saved.project;state.id=saved.id;state.shot=0;fill();presets();changed();$("projects-dialog").close();}catch(e){toast(e.message,true);}finally{event.target.value="";}};
}
async function init(){try{const boot=await api("/api/bootstrap");Object.assign(state,{token:boot.token,assets:boot.assets,projects:boot.projects,jobs:boot.jobs});state.presets=boot.formats.filter(f=>f.tag==="Composition");try{const draft=JSON.parse(localStorage.getItem("shorts-compositor-draft"));if(state.presets.some(f=>f.id===draft?.project?.format)){state.project=draft.project;state.id=draft.id;state.shot=Math.min(draft.shot||0,draft.project.scenes.length-1);}}catch{}if(!state.project)state.project=await api("/api/templates/overlay");bind();fill();presets();summary();timeline();schedule();setInterval(async()=>{try{state.jobs=await api("/api/jobs");const job=state.jobs.find(j=>j.id===state.job);if(job)renderJob(job);}catch{}},1300);}catch(error){$("loading").textContent=error.message;toast(error.message,true);}}
init();
