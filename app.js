'use strict';
const $=(s,root=document)=>root.querySelector(s);
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const KEY='data-engineering-lab:progress:v2', LEGACY='data-engineering-lab:progress:v1';
const legacyRoutes={g0:'m04',g1:'m06',g2:'m08',g3:'m10',g4:'m12',g5:'m13',g6:'m13',g7:'m14',g8:'m15',g9:'m16',g10:'m17',g11:'m19',map:'start',project:'m01',production:'m19'};
let course,ids=[],routeId='home',saveWarning=false,legacyBackup='',toastTimer;
let state={version:2,last:'m00',read:[],notes:{},quiz:{}};
function toast(message){$('#toast').textContent=message;$('#toast').classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').classList.remove('visible'),6000);}
function validateState(value){
  if(!value||value.version!==2||!Array.isArray(value.read)||!value.notes||typeof value.notes!=='object'||Array.isArray(value.notes)||!value.quiz||typeof value.quiz!=='object'||Array.isArray(value.quiz))throw Error('Not a valid version-2 course progress file.');
  if(!ids.includes(value.last)||value.read.some(id=>!ids.includes(id)))throw Error('Invalid module identifiers.');
  const result={version:2,last:value.last,read:[...new Set(value.read)],notes:{},quiz:{}};
  for(const [id,note] of Object.entries(value.notes)){
    if(!ids.includes(id)||typeof note!=='string'||note.length>30000)throw Error('Invalid note or note longer than 30,000 characters.');
    result.notes[id]=note;
  }
  for(const [id,answers] of Object.entries(value.quiz)){
    if(!ids.includes(id)||!Array.isArray(answers)||answers.length!==course.quizzes[id].length||answers.some((a,i)=>!Number.isInteger(a)||a<0||a>=course.quizzes[id][i][1].length))throw Error('Invalid self-check answers.');
    result.quiz[id]=answers;
  }
  return result;
}
function save(){try{localStorage.setItem(KEY,JSON.stringify(state));return true;}catch{if(!saveWarning){toast('Progress cannot be saved in this browser. Export a backup from Notes and progress before leaving.');saveWarning=true;}return false;}}
function download(filename,content,type='application/json'){const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
const pageById=id=>course.pages.find(p=>p.id===id);
const link=(id,label,code='')=>'<a class="nav-link '+(routeId===id?'active':'')+'" href="#'+id+'" '+(routeId===id?'aria-current="page"':'')+'>'+(code?'<span class="nav-code">'+code+'</span>':'')+'<span class="nav-label">'+esc(label)+'</span>'+(state.read.includes(id)?'<span class="read-dot" aria-label="Read"></span>':'')+'</a>';
function navigation(){
  $('#navigation').innerHTML=link('home','Learning path')+link('start','How to use this course')+course.groups.map((g,n)=>'<p class="nav-group">'+esc(g.title)+'</p>'+course.modules.filter(m=>m.group===n).map(m=>link(m.id,m.title,m.id.toUpperCase())).join('')).join('')+'<p class="nav-group">Reference desk</p>'+['glossary','troubleshooting','assessment','references'].map(id=>link(id,pageById(id).title)).join('')+link('resources','Practice files');
  $('#read-progress').textContent='Read '+state.read.length+' / '+ids.length+' modules';$('#progress').max=ids.length;$('#progress').value=state.read.length;
}
function frame(body){return '<div class="page"><div class="topline"><a href="#home">Data Engineering / Learning Lab</a><span>Concepts → practice → evidence</span></div>'+body+'<footer class="footer"><span>Fictional data only</span><a href="#assessment">Reading ≠ mastery</a><a href="#notebook">Back up progress</a><a href="https://github.com/Ryan970910/data-engineering-lab" target="_blank" rel="noopener noreferrer">GitHub</a></footer></div>';}
function home(){
  const last=pageById(state.last);
  return frame('<div class="home-intro"><h1>Understand the data.<br>Build the pipeline.</h1><p class="lead">Start with what data engineering means. Then learn SQL, reliable pipelines, Airflow and PySpark through a project you can explain and defend.</p><p class="quiet-note">For a Python developer with basic SQL. Twenty modules, real experiments and an independent capstone. No tools to install on day one.</p></div><section class="resume" aria-label="Continue learning"><div><small>Your next reading position · not an assessed grade</small><h2>'+last.id.toUpperCase()+' · '+esc(last.title)+'</h2></div><a class="button primary" href="#'+last.id+'">'+(state.last==='m00'&&!state.read.length?'Start with the concepts':'Continue learning')+' →</a></section><div class="practice-cycle" aria-label="Learning cycle"><span>Understand</span><b>→</b><span>Predict</span><b>→</b><span>Build</span><b>→</b><span>Break & explain</span><b>→</b><span>Prove</span></div><div class="section-heading"><h2>Your learning path</h2><span>20 modules · progress by ability</span></div>'+course.groups.map((g,n)=>'<section class="syllabus-group"><div><h3>'+esc(g.title)+'</h3><p>'+esc(g.description)+'</p></div><div>'+course.modules.filter(m=>m.group===n).map(m=>'<a class="lesson-row" href="#'+m.id+'"><span class="lesson-number">'+m.id.toUpperCase()+'</span><span><strong>'+esc(m.title)+'</strong><small>'+esc(m.outcome)+'</small></span><span class="lesson-state '+(state.read.includes(m.id)?'done':'')+'">'+(state.read.includes(m.id)?'Read':'Explore')+' ›</span></a>').join('')+'</div></section>').join('')+'<p class="quiet-note">Read and take notes on your phone; run experiments on a computer. Start with <a href="#start">How to use this course</a>. Practical competence requires code, outputs, explanation and an unseen variant with your coach.</p>');
}
function quizPanel(id){
  return '<section class="exercise-panel" id="practice"><h2>Check the concept. Then prove the skill.</h2><p class="muted">Three visible questions help you find gaps. They do not assess your code or grant a practical pass.</p><form class="quiz" data-lesson="'+id+'">'+course.quizzes[id].map(([q,options],i)=>'<fieldset><legend>'+(i+1)+'. '+esc(q)+'</legend>'+options.map((option,n)=>'<label class="answer-option"><input type="radio" name="q'+i+'" value="'+n+'" required '+(state.quiz[id]?.[i]===n?'checked':'')+'><span>'+esc(option)+'</span></label>').join('')+'</fieldset>').join('')+'<button class="primary" type="submit">Check answers and reasoning</button><div class="quiz-feedback" aria-live="polite"></div></form><label class="note-label" for="lesson-note">Keep your reasoning and evidence</label><p class="muted">Record predictions, commands, results, explanations and help used. Use fictional data only; never paste credentials or member details.</p><textarea id="lesson-note" maxlength="30000" placeholder="My prediction:&#10;Commands and actual results:&#10;Why this happened:&#10;Failure and recovery:&#10;Help used / remaining questions:">'+esc(state.notes[id]||'')+'</textarea><p class="note-hint">Auto-saved in this browser when storage is available. No cloud sync. Limit: 30,000 characters.</p><div class="tools-row"><button id="export-evidence">Export assessment draft</button><a class="button" href="#assessment">See the assessment rubric</a></div><p class="note-hint">Send the draft, code and outputs to your coach. Ask “Assess '+id.toUpperCase()+' and give me an unseen variant.” This website cannot verify a runtime or certify mastery.</p></section>';
}
function article(page){
  const n=ids.indexOf(page.id),lesson=n>=0;
  return frame('<header class="article-head"><div class="article-meta"><span>'+(lesson?page.id.toUpperCase()+' / 20 modules':'Course reference')+'</span><span>'+esc(lesson?page.effort+' · estimate, not a deadline':'Return whenever you need it')+'</span></div><h1>'+esc(page.title)+'</h1>'+(lesson?'<p class="lead">'+esc(page.outcome)+'</p><div class="lesson-actions"><button id="mark-read" aria-pressed="'+state.read.includes(page.id)+'">'+(state.read.includes(page.id)?'Marked read · undo':'Mark as read')+'</button><a class="button primary" href="#'+page.id+'/practice">Concept self-check ↓</a></div>':'')+'</header><div class="reading-layout"><div class="prose">'+page.html+(lesson?quizPanel(page.id):'')+'<div class="lesson-footer">'+(lesson?'<a class="button" href="#'+(n?ids[n-1]:'home')+'">← '+(n?'Previous module':'Learning path')+'</a><a class="button primary" href="#'+(n<ids.length-1?ids[n+1]:'assessment')+'">'+(n<ids.length-1?'Next module':'Capstone assessment')+' →</a>':'<a class="button" href="#home">Back to learning path</a>')+'</div></div><nav class="toc" aria-label="On this page"></nav></div>');
}
function resources(){
  const files=[['lab.py','Offline Python pipeline','M06–M10: snapshots, matching, validation and mock delivery.'],['sql_lab.py','Read-only SQL practice','M05: execute queries on fictional data and check exact identities.'],['spark_exercise.py','Spark implementation scaffold','M15: build_pairs is deliberately yours to implement.'],['dags/club_training.py','Airflow teaching DAG','M13: single-host orchestration; no production calls.'],['env.sh','Linux environment settings','M12: inspect D-drive paths before sourcing.'],['verify_course.py','Author baseline checks','Checks supplied code; not a learner certificate.']];
  return frame('<h1>Your practice workspace.</h1><p class="lead">Download the complete course, then run isolated experiments on your computer.</p><div class="tools-row"><a class="button primary" href="https://github.com/Ryan970910/data-engineering-lab/archive/refs/heads/main.zip">Download course ZIP</a><a class="button" href="#start">Setup and study guide</a></div>'+files.map(([file,title,desc])=>'<section class="notebook-row"><h3>'+title+'</h3><p>'+desc+'</p><a href="docs/data-engineering/'+file+'" download>Download '+file+'</a></section>').join('')+'<h2>Course sources</h2><p>All 20 English chapters are included in the ZIP under docs/data-engineering/lessons. The website renders those same sources.</p><div class="tools-row"><a class="button" href="docs/data-engineering/MANUAL.md" download>Download course index</a><a class="button" href="#references">Official references and limits</a><a class="button" href="#assessment">Assessment guide</a></div><div class="notice warning">Website and offline author checks are not Airflow/Spark runtime verification. Run the real environment exercises and keep evidence. No learner checkpoint is automatically passed.</div>');
}
const score=(id,answers)=>course.quizzes[id].filter((q,i)=>q[2]===answers[i]).length;
function notebook(){
  return frame('<h1>Keep the thinking, not just the score.</h1><p class="lead">Reading, self-checks and notes live here. Practical assessment happens with your coach and your actual code.</p><div class="notice">Saved only in this browser. Export JSON before switching devices. Import replaces current records after confirmation. Back up first.</div><div class="tools-row"><button class="primary" id="export-progress">Export progress backup</button><button id="import-progress">Import progress</button><input type="file" id="import-file" accept="application/json,.json" hidden></div>'+(legacyBackup?'<div class="notice"><h2>Previous course notes are preserved</h2><p>Your version-1 records remain unchanged. The new curriculum has different modules, so old reading marks and scores are not migrated into new completion.</p><button id="export-legacy">Download previous-course backup</button></div>':'')+ids.map(id=>'<section class="notebook-row"><h3><a href="#'+id+'">'+id.toUpperCase()+' · '+esc(pageById(id).title)+'</a></h3><small class="muted">'+(state.read.includes(id)?'Read':'Not marked read')+' · '+(state.quiz[id]?'Latest self-check '+score(id,state.quiz[id])+'/'+course.quizzes[id].length:'No self-check yet')+' · Practical assessment pending</small><p>'+(state.notes[id]?esc(state.notes[id]):'No notes yet. Record your prediction and evidence at the end of the module.')+'</p></section>').join(''));
}
function feedback(id,answers){
  const count=score(id,answers),total=course.quizzes[id].length;
  $('.quiz-feedback').innerHTML='<div class="quiz-result '+(count<total?'needs-work':'')+'"><strong>'+count+'/'+total+' · '+(count<total?'Revisit these concepts':'Concept check complete')+'</strong><ol>'+course.quizzes[id].map((q,i)=>'<li><strong>'+(answers[i]===q[2]?'Correct':'Revisit')+'</strong>: '+esc(q[3][answers[i]])+'<p>Best answer: '+esc(q[1][q[2]])+'. '+esc(q[3][q[2]])+'</p></li>').join('')+'</ol><p>Next: complete the experiment, explain the result and submit independent evidence. This score is not a practical pass.</p></div>';
}
function evidence(id){
  return '# Assess '+id.toUpperCase()+'\n\nLearner-authored draft, not a verified grade. Remove sensitive information.\n\nEnvironment and versions:\nObjective:\nPrediction:\nCommands and exit codes:\nCode revision/path:\nInput fixture or snapshot hash:\nExpected and actual identities:\nFailure, recovery and tests:\nIndependent explanation:\nHelp used:\nLimitations:\n\n## Notes\n'+(state.notes[id]||'Not provided')+'\n\nVisible concept self-check: '+(state.quiz[id]?score(id,state.quiz[id])+'/'+course.quizzes[id].length:'Not completed')+'\n\nCoach: review the evidence, ask follow-up questions and provide an unseen variation. Grade correctness, explanation, independence and diagnosis separately. Do not infer mastery from website progress.\n';
}
function enhance(){
  document.querySelectorAll('.prose pre').forEach(pre=>{
    const wrap=document.createElement('div');wrap.className='code-wrap';pre.before(wrap);
    const toolbar=document.createElement('div');toolbar.className='code-toolbar';
    const lang=$('code',pre)?.className.replace('language-','')||'text';
    toolbar.innerHTML='<span>'+esc(lang)+'</span><button type="button" aria-label="Copy '+esc(lang)+' code">Copy</button>';wrap.append(toolbar,pre);
    $('button',toolbar).onclick=async()=>{try{await navigator.clipboard.writeText(pre.textContent);toast('Code copied. Check the terminal type and paths before running.');}catch{const range=document.createRange();range.selectNodeContents(pre);getSelection().removeAllRanges();getSelection().addRange(range);toast('Automatic copy unavailable. Code selected; copy it manually.');}};
  });
  document.querySelectorAll('.prose table').forEach(table=>{const wrap=document.createElement('div');wrap.className='table-scroll';wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Course table, horizontally scrollable');table.before(wrap);wrap.append(table);});
  const headings=[...document.querySelectorAll('.prose > h2,.prose > h3')];headings.forEach((h,i)=>h.id='section-'+i);
  if($('.toc'))$('.toc').innerHTML='<strong>On this page</strong>'+headings.map(h=>'<a href="#'+routeId+'/'+h.id+'">'+esc(h.textContent)+'</a>').join('')+(ids.includes(routeId)?'<a href="#'+routeId+'/practice">Self-check and notes</a>':'');
  if($('#mark-read'))$('#mark-read').onclick=()=>{state.read=state.read.includes(routeId)?state.read.filter(i=>i!==routeId):[...state.read,routeId];save();const yes=state.read.includes(routeId);$('#mark-read').textContent=yes?'Marked read · undo':'Mark as read';$('#mark-read').setAttribute('aria-pressed',String(yes));navigation();};
  if($('.quiz')){const id=routeId;$('.quiz').onsubmit=e=>{e.preventDefault();const form=new FormData(e.target);const answers=course.quizzes[id].map((_,i)=>Number(form.get('q'+i)));state.quiz[id]=answers;save();feedback(id,answers);};if(state.quiz[id])feedback(id,state.quiz[id]);}
  if($('#lesson-note'))$('#lesson-note').oninput=e=>{state.notes[routeId]=e.target.value;save();};
  if($('#export-evidence'))$('#export-evidence').onclick=()=>download(routeId+'-evidence.md',evidence(routeId),'text/markdown;charset=utf-8');
  if($('#export-progress'))$('#export-progress').onclick=()=>download('learning-lab-progress-v2.json',JSON.stringify(state,null,2));
  if($('#export-legacy'))$('#export-legacy').onclick=()=>download('learning-lab-progress-v1-preserved.json',legacyBackup);
  if($('#import-progress')){
    $('#import-progress').onclick=()=>$('#import-file').click();
    $('#import-file').onchange=async e=>{
      const file=e.target.files[0];if(!file)return;
      try{
        if(file.size>1024*1024)throw Error('File exceeds 1 MB. Choose an exported progress backup.');
        const imported=validateState(JSON.parse(await file.text()));
        if(!confirm('Import will replace current notes and progress. Have you exported a backup, and do you want to continue?'))return;
        state=imported;save();render();toast('Progress imported. Practical assessment still requires a coach.');
      }catch(err){toast('Import failed; existing records are unchanged: '+err.message);}
      finally{if($('#import-file'))$('#import-file').value='';}
    };
  }
}
function search(){
  const term=$('#search').value.trim().toLowerCase();if(!term){render();return;}closeMenu(false);
  const matches=course.pages.filter(p=>(p.title+' '+p.text).toLowerCase().includes(term));
  $('#main').innerHTML=frame('<h1>Search the course</h1><p class="muted">'+esc(term)+' · '+matches.length+' results</p>'+(matches.length?matches.map(p=>{const pos=Math.max(0,p.text.toLowerCase().indexOf(term)-40);return '<section class="search-result"><a href="#'+p.id+'">'+esc(p.title)+'</a><p>'+esc(p.text.slice(pos,pos+180).replace(/[#*]/g,''))+'…</p></section>';}).join(''):'<div class="empty-state">No matching chapters. Try “join”, “retry”, “schema” or the exact error message.</div>'));
}
function render(){
  let [id,anchor]=(location.hash.slice(1)||'home').split('/');if(id==='main')return;
  if(legacyRoutes[id]){location.replace('#'+legacyRoutes[id]);return;}
  if(id===routeId&&anchor&&document.getElementById(anchor)){document.getElementById(anchor).scrollIntoView();return;}
  routeId=id;const page=pageById(id);if(ids.includes(id)){state.last=id;save();}
  $('#main').innerHTML=id==='home'?home():id==='resources'?resources():id==='notebook'?notebook():page?article(page):frame('<h1>Page not found.</h1><p>This link may belong to an older course version.</p><a class="button primary" href="#home">Return to the learning path</a>');
  document.title=(page?.title||({home:'Learning path',resources:'Practice files',notebook:'Notes and progress'}[id]||'Page not found'))+' · Learning Lab';
  navigation();enhance();window.scrollTo(0,0);if(anchor)document.getElementById(anchor)?.scrollIntoView();
}
const mobile=matchMedia('(max-width:760px)');
function closeMenu(returnFocus=true){const opened=document.body.classList.contains('menu-open');document.body.classList.remove('menu-open');$('#scrim').hidden=true;$('#menu-toggle').setAttribute('aria-expanded','false');$('#sidebar').inert=mobile.matches;$('#main').inert=false;if(opened&&returnFocus)$('#menu-toggle').focus();}
$('#menu-toggle').onclick=()=>{if(document.body.classList.contains('menu-open')){closeMenu();return;}document.body.classList.add('menu-open');$('#scrim').hidden=false;$('#sidebar').inert=false;$('#main').inert=true;$('#menu-toggle').setAttribute('aria-expanded','true');$('#search').focus();};
$('#scrim').onclick=()=>closeMenu();mobile.addEventListener('change',()=>closeMenu(false));
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu();if(e.key==='Tab'&&document.body.classList.contains('menu-open')){const targets=[$('#menu-toggle'),...[...$('#sidebar').querySelectorAll('a,button,input')].filter(el=>el.offsetParent!==null)];const first=targets[0],last=targets.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}});
$('#navigation').addEventListener('click',e=>{if(e.target.closest('a')){closeMenu(false);$('#search').value='';$('#main').focus();}});
document.addEventListener('click',e=>{const link=e.target.closest('a[href^="#"]');if(link&&link.getAttribute('href')===location.hash&&$('.search-result')){e.preventDefault();$('#search').value='';render();}});
$('#search').addEventListener('input',()=>{if(!mobile.matches)search();});
$('#search').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();search();$('#main').focus();}});
window.addEventListener('hashchange',()=>{if(!course)return;$('#search').value='';closeMenu(false);render();});
fetch('course.json').then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();}).then(data=>{
  if(data.version!==2)throw Error('Course version mismatch');
  course=data;ids=course.modules.map(m=>m.id);let warning='';
  try{legacyBackup=localStorage.getItem(LEGACY)||'';const stored=localStorage.getItem(KEY);if(stored)state=validateState(JSON.parse(stored));}catch{warning='Stored progress could not be read. Starting with defaults; import a valid backup if available.';}
  closeMenu(false);render();if(warning)toast(warning);
}).catch(()=>{$('#main').innerHTML=frame('<h1>The course could not load.</h1><p>Check your connection and refresh. If you opened an HTML file directly, use the hosted website or a local HTTP server.</p><button onclick="location.reload()">Try again</button>');});
