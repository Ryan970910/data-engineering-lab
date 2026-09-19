'use strict';
const $ = (s, root = document) => root.querySelector(s);
const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const KEY = 'data-engineering-lab:progress:v1';
const ids = Array.from({length:12}, (_,i)=>`g${i}`);
const groups = [
  ['把基础做扎实','先理解数据，再引入工具',ids.slice(0,4)],
  ['让任务有序执行','用 Airflow 编排与恢复',ids.slice(4,7)],
  ['让数据正确流动','用 PySpark 转换与关联',ids.slice(7,10)],
  ['完成端到端交付','组合工具，独立证明',ids.slice(10)]
];
const outcomes = ['分清终端、路径与解释器','跑通一条五阶段数据管道','验证空键、重复与歧义','证明重放与失败恢复','准备独立的 Linux 环境','运行并解释第一个 DAG','观察重试、阻断与回填','理解 DataFrame 与惰性计算','独立实现两类匹配','用计划和测量解释性能','让调度与计算协同工作','完成增量处理与独立考核'];
let course, state = {version:1,last:'g0',read:[],notes:{},quiz:{}}, saveWarning=false, routeId='home';
let toastTimer;
function toast(message) { $('#toast').textContent=message; $('#toast').classList.add('visible'); clearTimeout(toastTimer); toastTimer=setTimeout(()=>$('#toast').classList.remove('visible'),4500); }
function validateState(value) {
  if(!value || value.version!==1 || !Array.isArray(value.read) || !value.notes || typeof value.notes!=='object' || Array.isArray(value.notes) || !value.quiz || typeof value.quiz!=='object' || Array.isArray(value.quiz)) throw Error('不是本课程的有效进度文件。');
  if(!ids.includes(value.last) || value.read.some(id=>!ids.includes(id))) throw Error('关卡信息无效。');
  const result={version:1,last:value.last,read:[...new Set(value.read)],notes:{},quiz:{}};
  for(const [id,note] of Object.entries(value.notes)) {
    if(!ids.includes(id) || typeof note!=='string' || note.length>30000) throw Error('笔记格式或长度无效。');
    result.notes[id]=note;
  }
  for(const [id,answers] of Object.entries(value.quiz)) {
    if(!ids.includes(id) || !Array.isArray(answers) || answers.length!==2 || answers.some(a=>!Number.isInteger(a)||a<0||a>2)) throw Error('自测记录无效。');
    result.quiz[id]=answers;
  }
  return result;
}
function save() {
  try {localStorage.setItem(KEY,JSON.stringify(state));return true;}
  catch {if(!saveWarning) {toast('浏览器无法保存进度。离开前请在“我的笔记与进度”中导出备份。');saveWarning=true;}return false;}
}
function download(filename,content,type='application/json') {
  const url=URL.createObjectURL(new Blob([content],{type})); const a=document.createElement('a'); a.href=url;a.download=filename; a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function pageById(id) {return course.pages.find(p=>p.id===id);}
function navLink(id,label,code='') {return `<a class="nav-link ${routeId===id?'active':''}" href="#${id}" ${routeId===id?'aria-current="page"':''}>${code?`<span class="nav-code">${code}</span>`:''}<span class="nav-label">${escapeHTML(label)}</span>${state.read.includes(id)?'<span class="read-dot" aria-label="已读"></span>':''}</a>`;}
function navigation() {
  $('#navigation').innerHTML=navLink('home','学习路线')+navLink('start','开始前的准备')+groups.map(([title,,list])=>`<p class="nav-group">${title}</p>${list.map(id=>navLink(id,pageById(id).title,id.toUpperCase())).join('')}`).join('')+`<p class="nav-group">随时查阅</p>`+[['project','项目与数据工程'],['glossary','概念速查'],['troubleshooting','排错手册'],['assessment','实操验收规则'],['resources','练习文件与参考资料']].map(([id,title])=>navLink(id,title)).join('');
  $('#read-progress').textContent=`已读 ${state.read.length} / 12 关`;$('#progress').value=state.read.length;
}
function frame(body) {return `<div class="page"><div class="topline"><a href="#home">数据工程实战 / Learning Lab</a><span>从项目出发，把知识变成能力</span></div>${body}<footer class="footer"><span>仅使用虚构教学数据</span><a href="#assessment">阅读 ≠ 掌握</a><a href="#notebook">备份学习进度</a><a href="https://github.com/Ryan970910/data-engineering-lab" target="_blank" rel="noopener noreferrer">GitHub</a></footer></div>`;}
function home() {
  const last=pageById(state.last);
  // A visited lesson is a resumable position even before the learner marks it read.
  return frame(`<div class="home-intro"><h1>让每一条数据，<br>都有清楚的来路。</h1><p class="lead">从熟悉的 ROI、Buyer 与会员匹配出发，<br>一步步学会 Airflow、PySpark，以及真正可靠的数据管道。</p></div><section class="resume" aria-label="继续学习"><div><small>${state.last!=='g0'||state.read.length?'继续上次的学习':'你的第一步，不需要安装完整技术栈'}</small><h2>${last.id.toUpperCase()} · ${escapeHTML(last.title)}</h2></div><a class="button primary" href="#${last.id}">${state.last!=='g0'||state.read.length?'继续学习':'从第 0 关开始'} <span aria-hidden="true">→</span></a></section><div class="practice-cycle" aria-label="每关学习流程"><span>阅读</span><b>→</b><span>预测</span><b>→</b><span>操作</span><b>→</b><span>解释</span><b>→</b><span>改题</span><b>→</b><span>提交验收</span></div><div class="section-heading"><h2>你的学习路线</h2><span>12 关 · 按能力，不赶进度</span></div>${groups.map(([title,description,list])=>`<section class="syllabus-group"><div><h3>${title}</h3><p>${description}</p></div><div>${list.map(id=>`<a class="lesson-row" href="#${id}"><span class="lesson-number">${id.toUpperCase()}</span><span><strong>${escapeHTML(pageById(id).title)}</strong><small>${outcomes[Number(id.slice(1))]}</small></span><span class="lesson-state ${state.read.includes(id)?'done':''}">${state.read.includes(id)?'已读':'待学习'} <span aria-hidden="true">›</span></span></a>`).join('')}</div></section>`).join('')}<p class="quiet-note">手机上阅读、做概念自测；电脑上运行练习。第一次在新电脑练习？先看 <a href="#start">开始前的准备</a>。实操能力需提交代码和证据，由教练另行验收。</p>`);
}
function start() {return frame(`<div class="article-head"><h1>先准备一个安全的练习空间。</h1><p class="lead">网页随时打开。真正的 Airflow 和 Spark 实验，在你自己的电脑上运行。</p></div><div class="prose"><div class="notice">这是独立的公开学习仓库，不包含业务源码或真实会员资料。网页版命令已改为独立路径 <code>D:\\projects\\data-engineering-lab</code>，不要在生产环境里安装练习依赖。</div><ol class="setup-steps"><li><h3>只想先读？现在就可以。</h3><p>从 G0 开始，边读边做每关底部的概念自测。无需登录。已读标记不是实操成绩。</p></li><li><h3>在 Windows 电脑上取得练习文件。</h3><p>已安装 Git 时，在 PowerShell 执行下列命令。若目标目录已存在，先确认其内容，不要覆盖。</p><pre><code class="language-powershell">Set-Location D:\\projects
git clone https://github.com/Ryan970910/data-engineering-lab.git
Set-Location D:\\projects\\data-engineering-lab</code></pre><p>没有 Git？<a href="https://github.com/Ryan970910/data-engineering-lab/archive/refs/heads/main.zip">下载课程 ZIP</a>，把最外层文件夹改名为 <code>data-engineering-lab</code>，放入 <code>D:\\projects</code>。确认 <code>docs/data-engineering/lab.py</code> 在其中。</p></li><li><h3>创建独立的 Python 环境。</h3><p>G0–G3 使用 Python 3.9 或以上的标准库，不需要安装 Airflow。先检查 Windows Python launcher；没有安装 Python 时，先从 <a href="https://www.python.org/downloads/windows/" target="_blank" rel="noopener noreferrer">Python 官网</a> 安装，别覆盖原项目的环境。</p><pre><code class="language-powershell">py --version
py -3 -m venv .venv
&amp; .\\.venv\\Scripts\\python.exe --version
&amp; .\\.venv\\Scripts\\python.exe -c "import sys; print(sys.executable)"</code></pre><p>新建标准 venv 的解释器在 <code>.venv\\Scripts\\python.exe</code>。原项目环境在 <code>.venv\\python.exe</code>，二者路径不同，网页中的操作命令使用前者。</p></li><li><h3>从 G0 提交第一份证据。</h3><p>完成环境检查，写下解释器路径与自己的理解。到每关底部填写笔记，再导出验收草稿发给教练。不要上传真实姓名、手机、HKID、数据库配置或密码。</p><a class="button primary" href="#g0">开始第 0 关 →</a></li></ol><h2>换设备时，进度怎么带走？</h2><p>当前版本没有账户或云端同步。到“我的笔记与进度”导出 JSON，在另一台设备打开网站后导入。清除浏览器数据会丢失本地记录，请定期备份。</p><h2>之后再安装什么？</h2><p>G4 会逐步准备 D 盘上的 WSL、独立 Airflow 与 Spark 环境。不要在第一天把全部软件都装好，也不要升级原项目的生产环境。手机无法执行这些系统命令。</p></div>`);}
function quizPanel(id) {const questions=course.quizzes[id];return `<section class="exercise-panel" id="practice"><h2>停一下，检验你的理解。</h2><p class="muted">先凭自己的判断作答。这里是概念自测，不是实操验收。</p><form class="quiz" data-lesson="${id}">${questions.map(([q,options],i)=>`<fieldset><legend>${i+1}. ${escapeHTML(q)}</legend>${options.map((option,n)=>`<label class="answer-option"><input type="radio" name="q${i}" value="${n}" required ${state.quiz[id]?.[i]===n?'checked':''}><span>${escapeHTML(option)}</span></label>`).join('')}</fieldset>`).join('')}<button class="primary" type="submit">检查答案与解释</button><div class="quiz-feedback" aria-live="polite"></div></form><label class="note-label" for="lesson-note">用自己的话，留下证据</label><p class="muted">写下预测、实际结果、原因和仍不理解的地方。只记录虚构数据，不粘贴密码或真实会员信息。</p><textarea id="lesson-note" maxlength="30000" placeholder="我的预测：&#10;实际命令与结果：&#10;我能解释的原因：&#10;我仍然不确定：">${escapeHTML(state.notes[id]||'')}</textarea><p class="note-hint">输入时自动保存到此浏览器；无云端同步。最多 30,000 字符。</p><div class="tools-row"><button id="export-evidence">导出本关验收草稿</button><a class="button" href="#assessment">查看验收标准</a></div><p class="note-hint">把草稿和可复现代码发给教练，并说“验收第 ${id.slice(1)} 关”。教练需要追问和独立变式，网页不会自动授予通过。</p></section>`;}
function article(page) {
  const isLesson=ids.includes(page.id); const n=ids.indexOf(page.id);
  return frame(`<header class="article-head"><div class="article-meta"><span>${isLesson?`第 ${n} 关 / 共 12 关`:'课程参考'}</span><span>${isLesson?outcomes[n]:'随时回来查阅'}</span></div><h1>${escapeHTML(page.title)}</h1>${isLesson?`<div class="lesson-actions"><button id="mark-read" aria-pressed="${state.read.includes(page.id)}">${state.read.includes(page.id)?'已标为读完 · 撤销':'标记为已读'}</button><a class="button primary" href="#${page.id}/practice">去做本关自测 ↓</a></div>`:''}</header><div class="reading-layout"><div class="prose">${page.id==='g0'?'<div class="notice">新电脑请先完成 <a href="#start">开始前的准备</a>。下文旧项目机器状况是作者编写时的记录，不代表你的机器；网页操作路径已改为独立课程目录。</div>':''}${page.html}${isLesson?quizPanel(page.id):''}<div class="lesson-footer">${isLesson?`<a class="button" href="#${n>0?ids[n-1]:'home'}">← ${n>0?'上一关':'学习路线'}</a><a class="button primary" href="#${n<11?ids[n+1]:'assessment'}">${n<11?'预览下一关':'查看结业要求'} →</a>`:'<a class="button" href="#home">回到学习路线</a>'}</div></div><nav class="toc" aria-label="本页目录"></nav></div>`);
}
function resources() {return frame(`<h1>练习材料，集中放好。</h1><p class="lead">所有练习只使用虚构数据。下载后在电脑上运行，不连接生产系统。</p><div class="tools-row"><a class="button primary" href="https://github.com/Ryan970910/data-engineering-lab/archive/refs/heads/main.zip">下载完整课程 ZIP</a><a class="button" href="#start">查看准备步骤</a></div>${[['lab.py','标准库管道','G1–G3：生成数据、匹配、校验、模拟交付。'],['spark_exercise.py','Spark 练习骨架','G8：需要你自己完成；NotImplementedError 是待实现提示。'],['dags/club_training.py','Airflow 示例 DAG','G5 起使用。只是教学编排，不触发生产 bulk-import。'],['env.sh','Linux 环境配置','G4：加载前检查 D 盘路径。'],['verify_course.py','作者基准验证脚本','用于检查练习基准，不代表你已掌握。']].map(([file,title,desc])=>`<section class="notebook-row"><h3>${title}</h3><p>${desc}</p><a href="docs/data-engineering/${file}" download>下载 ${file}</a></section>`).join('')}<h2>手册与参考</h2><div class="tools-row"><a class="button" href="#references">官方资料与验证边界</a><a class="button" href="#production">生产接入前的检查</a><a class="button" href="#map">学习地图与时间参考</a><a class="button" href="docs/data-engineering/MANUAL.md" download>下载完整 Markdown 手册</a></div><div class="notice warning">作者已验证 Windows 标准库管道。Airflow/Linux/Spark 的实际运行仍待学习环境验收；本网站的功能测试不等于这些运行环境已经通过。</div>`);}
function notebook() {return frame(`<h1>把思考留下来。</h1><p class="lead">这里记录你的阅读、自测和笔记。真正的实操成绩，由教练根据证据另行确认。</p><div class="notice">仅保存在当前浏览器。换设备前请导出 JSON；在另一设备导入即可继续。导入会替换当前记录，建议先备份。</div><div class="tools-row"><button class="primary" id="export-progress">导出进度备份</button><button id="import-progress">导入进度</button><input type="file" id="import-file" accept="application/json,.json" hidden></div>${ids.map(id=>`<section class="notebook-row"><h3><a href="#${id}">${id.toUpperCase()} · ${escapeHTML(pageById(id).title)}</a></h3><small class="muted">${state.read.includes(id)?'已读':'尚未标记已读'} · ${state.quiz[id]?`最近自测 ${score(id,state.quiz[id])}/2`:'尚未自测'} · 实操需教练验收</small>${state.notes[id]?`<p>${escapeHTML(state.notes[id])}</p>`:'<p>还没有笔记。从本关末尾开始记录你的预测和解释。</p>'}</section>`).join('')}`);}
function score(id,answers) {return course.quizzes[id].filter((q,i)=>q[2]===answers[i]).length;}
function feedback(id,answers) {
  const count=score(id,answers); $('.quiz-feedback').innerHTML=`<div class="quiz-result ${count<2?'needs-work':''}"><strong>${count}/2 · ${count<2?'发现了值得补练的地方':'本次概念自测答对了'}</strong><ol>${course.quizzes[id].map((q,i)=>`<li><strong>${answers[i]===q[2]?'正确':'需修正'}</strong>：${escapeHTML(q[3])}</li>`).join('')}</ol><p>下一步：运行本关实验，并用自己的话解释结果。自测成绩不等于实操通过。</p></div>`;
}
function evidence(id) {return `# 验收第 ${id.slice(1)} 关\n\n本文件由学习者在网页生成，不是教练评分。请删除敏感信息后提交。\n\n环境与版本：\n目标：\n操作前预测：\n实际命令：\n代码路径：\n实际输出与退出码：\n故障恢复与复测：\n独立解释：\n使用过的帮助：\n\n## 我的笔记\n${state.notes[id]||'尚未填写'}\n\n网页最近自测：${state.quiz[id]?`${score(id,state.quiz[id])}/2`:'未完成'}（仅概念检查）\n\n请教练检查证据并提供一道新的变式题。\n`;}
function enhance() {
  document.querySelectorAll('.prose pre').forEach(pre=>{
    const wrapper=document.createElement('div');wrapper.className='code-wrap'; pre.before(wrapper);
    const toolbar=document.createElement('div');toolbar.className='code-toolbar';
    const lang=$('code',pre)?.className.replace('language-','')||'text';
    toolbar.innerHTML=`<span>${escapeHTML(lang)}</span><button type="button" aria-label="复制 ${escapeHTML(lang)} 代码">复制</button>`;wrapper.append(toolbar,pre);
    $('button',toolbar).onclick=async()=>{try{await navigator.clipboard.writeText(pre.textContent);toast('代码已复制；运行前请确认终端类型和路径。');}catch{const range=document.createRange();range.selectNodeContents(pre);getSelection().removeAllRanges();getSelection().addRange(range);toast('无法自动复制，已选中代码，请手动复制。');}};
  });
  document.querySelectorAll('.prose table').forEach(table=>{const wrap=document.createElement('div');wrap.className='table-scroll';wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','课程表格，可横向滚动');table.before(wrap);wrap.append(table);});
  const headings=[...document.querySelectorAll('.prose > h2,.prose > h3')];
  headings.forEach((h,i)=>h.id=`section-${i}`);
  if($('.toc')) $('.toc').innerHTML='<strong>本页内容</strong>'+headings.map(h=>`<a href="#${routeId}/${h.id}">${escapeHTML(h.textContent)}</a>`).join('')+(ids.includes(routeId)?`<a href="#${routeId}/practice">概念自测与笔记</a>`:'');
  if($('#mark-read')) $('#mark-read').onclick=()=>{state.read=state.read.includes(routeId)?state.read.filter(i=>i!==routeId):[...state.read,routeId];save();const yes=state.read.includes(routeId);$('#mark-read').textContent=yes?'已标为读完 · 撤销':'标记为已读';$('#mark-read').setAttribute('aria-pressed',String(yes));navigation();};
  if($('.quiz')) {const id=routeId;$('.quiz').onsubmit=e=>{e.preventDefault();const form=new FormData(e.target);const answers=[Number(form.get('q0')),Number(form.get('q1'))];state.quiz[id]=answers;save();feedback(id,answers);};if(state.quiz[id])feedback(id,state.quiz[id]);}
  if($('#lesson-note')) $('#lesson-note').oninput=e=>{state.notes[routeId]=e.target.value;save();};
  if($('#export-evidence')) $('#export-evidence').onclick=()=>download(`${routeId}-evidence.md`,evidence(routeId),'text/markdown;charset=utf-8');
  if($('#export-progress')) $('#export-progress').onclick=()=>download('learning-lab-progress.json',JSON.stringify(state,null,2));
  if($('#import-progress')) {$('#import-progress').onclick=()=>$('#import-file').click();$('#import-file').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>1024*1024)throw Error('文件超过 1 MB，请选择本课程导出的进度文件。');const imported=validateState(JSON.parse(await file.text()));if(!confirm('导入将替换当前浏览器的笔记和进度。已导出备份，并确认继续吗？'))return;state=imported;save();render();toast('进度已导入。实操成绩仍需教练验收。');}catch(err){toast(`导入失败，原记录未更改：${err.message}`);}finally{if($('#import-file'))$('#import-file').value='';}};}
}
function search() {
  const term=$('#search').value.trim().toLowerCase();if(!term){render();return;}
  closeMenu(false); const matches=course.pages.filter(p=>`${p.title} ${p.text}`.toLowerCase().includes(term));
  $('#main').innerHTML=frame(`<h1>搜索课程</h1><p class="muted">“${escapeHTML(term)}” · ${matches.length} 个结果</p>${matches.length?matches.map(p=>{const pos=Math.max(0,p.text.toLowerCase().indexOf(term)-40);return `<section class="search-result"><a href="#${p.id}">${escapeHTML(p.title)}</a><p>${escapeHTML(p.text.slice(pos,pos+160).replace(/[#*`]/g,''))}…</p></section>`;}).join(''):'<div class="empty-state">没有找到相关章节。试试“匹配”“重试”“环境”或具体报错。</div>'}`);
}
function render() {
  const [id,anchor]=(location.hash.slice(1)||'home').split('/');if(id==='main')return;
  if(id===routeId && anchor && document.getElementById(anchor)){document.getElementById(anchor).scrollIntoView();return;}
  routeId=id; const page=pageById(id);
  if(ids.includes(id)){state.last=id;save();}
  $('#main').innerHTML=id==='home'?home():id==='start'?start():id==='resources'?resources():id==='notebook'?notebook():page?article(page):frame('<h1>没有找到这一页。</h1><p>链接可能已失效。</p><a class="button primary" href="#home">回到学习路线</a>');
  document.title=`${page?.title||({home:'学习路线',start:'开始前的准备',resources:'练习材料',notebook:'我的笔记与进度'}[id]||'页面未找到')} · Learning Lab`;
  navigation();enhance();window.scrollTo(0,0);if(anchor)document.getElementById(anchor)?.scrollIntoView();
}
const mobile=matchMedia('(max-width:760px)');
function closeMenu(returnFocus=true) {const opened=document.body.classList.contains('menu-open');document.body.classList.remove('menu-open');$('#scrim').hidden=true;$('#menu-toggle').setAttribute('aria-expanded','false');$('#sidebar').inert=mobile.matches;$('#main').inert=false;if(opened&&returnFocus)$('#menu-toggle').focus();}
$('#menu-toggle').onclick=()=>{if(document.body.classList.contains('menu-open')){closeMenu();return;}document.body.classList.add('menu-open');$('#scrim').hidden=false;$('#sidebar').inert=false;$('#main').inert=true;$('#menu-toggle').setAttribute('aria-expanded','true');$('#search').focus();};
$('#scrim').onclick=()=>closeMenu();mobile.addEventListener('change',()=>closeMenu(false));
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu();if(e.key==='Tab'&&document.body.classList.contains('menu-open')){const targets=[$('#menu-toggle'),...[...$('#sidebar').querySelectorAll('a,button,input')].filter(el=>el.offsetParent!==null)];const first=targets[0],last=targets.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}});
$('#navigation').addEventListener('click',e=>{if(e.target.closest('a')){closeMenu(false);$('#search').value='';$('#main').focus();}});
document.addEventListener('click',e=>{const link=e.target.closest('a[href^="#"]');if(link && link.getAttribute('href')===location.hash && $('.search-result')){e.preventDefault();$('#search').value='';render();}});
$('#search').addEventListener('input',()=>{if(!mobile.matches)search();});
$('#search').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();search();$('#main').focus();}});
window.addEventListener('hashchange',()=>{if(!course)return;$('#search').value='';closeMenu(false);render();});
fetch('course.json').then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.json();}).then(data=>{
  course=data;let warning='';try{const stored=localStorage.getItem(KEY);if(stored)state=validateState(JSON.parse(stored));}catch{warning='无法读取已存进度，本次从默认状态打开。可以导入之前的备份。';}
  closeMenu(false);render();if(warning)toast(warning);
}).catch(()=>{$('#main').innerHTML=frame('<h1>课程暂时没有加载成功。</h1><p>请检查网络并刷新页面。若从电脑直接打开 HTML，请改用网站网址或本地 HTTP 服务。</p><button onclick="location.reload()">重新加载</button>');});
