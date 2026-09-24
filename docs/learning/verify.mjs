import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,readdir} from 'node:fs/promises';
import {createServer} from 'node:http';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('playwright');
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../../.learning-runtime/site-build');
const evidence=path.resolve(here,'../../.learning-runtime/course-v2-qa'+(process.argv[2]?'-live':''));
await mkdir(evidence,{recursive:true});
const data=JSON.parse(await readFile(path.join(root,'course.json'),'utf8'));
const manifest=JSON.parse(await readFile(path.join(root,'manifest.json'),'utf8'));
const checks=[],record=name=>{checks.push(name);console.log('PASS '+name);};
async function files(dir,prefix=''){
  const result=[];
  for(const entry of await readdir(dir,{withFileTypes:true})){
    if(!prefix&&entry.name==='.git')continue;
    const name=prefix+entry.name;
    if(entry.isDirectory())result.push(...await files(path.join(dir,entry.name),name+'/'));else result.push(name);
  }
  return result;
}
assert.deepEqual((await files(root)).sort(),[...Object.keys(manifest.files),'manifest.json'].sort());
for(const [name,hash] of Object.entries(manifest.files))assert.equal(createHash('sha256').update(await readFile(path.join(root,name))).digest('hex'),hash,name);
record('exact public allowlist and SHA-256 hashes; no extra private/cache files');
assert.equal(data.pages.length,27);assert.equal(data.modules.length,20);
assert.equal(Object.values(data.quizzes).flat().length,60);
assert.ok(!/[\u3400-\u9fff]/.test(JSON.stringify(data)));
for(const p of data.pages){
  for(const match of p.html.matchAll(/href="([^"]+)"/g)){
    const href=match[1];if(href.startsWith('#'))assert.ok(data.pages.some(p=>p.id===href.slice(1)),href);
  }
}
record('20 English modules, 60 questions, 27 content pages and valid chapter links');
const server=createServer(async(req,res)=>{
  try{
    const relative=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const filename=path.resolve(root,'.'+(relative==='/'?'/index.html':relative));
    if(!filename.startsWith(root+path.sep))throw Error('outside root');
    const content=await readFile(filename);
    const type={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml'}[path.extname(filename)]||'text/plain';
    res.writeHead(200,{'Content-Type':type+'; charset=utf-8'});res.end(content);
  }catch{res.writeHead(404);res.end('Not found');}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=process.argv[2]||'http://127.0.0.1:'+server.address().port+'/';
let browser;
try{
  browser=await chromium.launch({headless:true});
  const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce',acceptDownloads:true});
  const page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  async function visit(id){
    await page.goto(base+'#'+id);
    await page.locator('h1').waitFor();
    const content=data.pages.find(p=>p.id===id);
    if(content)await page.waitForFunction(title=>document.querySelector('h1')?.textContent===title,content.title);
  }
  await visit('home');assert.equal(await page.locator('.lesson-row').count(),20);
  assert.equal(await page.locator('html').getAttribute('lang'),'en');
  const routes=['home',...data.pages.map(p=>p.id),'resources','notebook'];
  for(const width of [1440,390]){
    await page.setViewportSize({width,height:900});
    for(const id of routes){
      await visit(id);
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'overflow '+width+' '+id);
      assert.ok(!/[\u3400-\u9fff]/.test(await page.locator('body').innerText()),'English UI '+id);
      if(/^m\d+$/.test(id))assert.equal(await page.locator('.quiz fieldset').count(),3);
    }
    record('all '+routes.length+' routes render in English without viewport overflow at '+width+'px');
  }
  await page.setViewportSize({width:1440,height:1000});
  for(const id of Object.keys(data.quizzes)){
    await visit(id);
    for(const wrong of [true,false]){
      for(let i=0;i<data.quizzes[id].length;i++){
        const answer=data.quizzes[id][i][2];
        await page.locator('input[name=q'+i+'][value="'+(wrong?(answer+1)%3:answer)+'"]').check();
      }
      await page.locator('.quiz button[type=submit]').click();
      assert.ok((await page.locator('.quiz-feedback').innerText()).includes(wrong?'0/3':'3/3'));
      assert.equal(await page.locator('.quiz-feedback li').count(),3);
    }
  }
  record('all 60 questions exercised wrong then correct with explanatory feedback');
  await visit('m05');await page.locator('details summary').click();
  assert.equal(await page.locator('details').getAttribute('open'),'');
  await page.locator('#mark-read').click();
  const note='Prediction, result, diagnosis <img src=x onerror=alert(1)> — not a practical pass.';
  await page.locator('#lesson-note').fill(note);await page.reload();await page.locator('#lesson-note').waitFor();
  assert.equal(await page.locator('#lesson-note').inputValue(),note);
  assert.equal(await page.locator('#mark-read').getAttribute('aria-pressed'),'true');
  assert.equal(await page.locator('#main img').count(),0);
  record('reasoning disclosure, read state, safe note escaping and persistence');
  const draftWait=page.waitForEvent('download');await page.locator('#export-evidence').click();
  await (await draftWait).saveAs(path.join(evidence,'m05-evidence.md'));
  assert.match(await readFile(path.join(evidence,'m05-evidence.md'),'utf8'),/not a verified grade/);
  await visit('notebook');
  const backupWait=page.waitForEvent('download');await page.locator('#export-progress').click();
  await (await backupWait).saveAs(path.join(evidence,'progress.json'));
  const exported=JSON.parse(await readFile(path.join(evidence,'progress.json'),'utf8'));assert.equal(exported.notes.m05,note);
  const before=await page.evaluate(()=>localStorage.getItem('data-engineering-lab:progress:v2'));
  for(const invalid of [{version:99},{version:2,last:'m05',read:[],notes:{},quiz:{m05:[99,0,0]}},{version:1,last:'g0',read:[],notes:{},quiz:{}}]){
    await page.locator('#import-file').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(invalid))});
    await page.waitForFunction(()=>document.querySelector('#toast').textContent.includes('Import failed'));
    assert.equal(await page.evaluate(()=>localStorage.getItem('data-engineering-lab:progress:v2')),before);
  }
  record('assessment and progress exports; invalid/version-1 imports cannot replace current state');
  const imported={version:2,last:'m08',read:['m08'],notes:{m08:'Restored from another device'},quiz:{m08:[1,2,0]}};
  page.once('dialog',d=>d.dismiss());
  await page.locator('#import-file').setInputFiles({name:'valid.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(imported))});
  assert.equal(await page.evaluate(()=>localStorage.getItem('data-engineering-lab:progress:v2')),before);
  page.once('dialog',d=>d.accept());
  await page.locator('#import-file').setInputFiles({name:'valid.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(imported))});
  await page.waitForFunction(()=>document.querySelector('#toast').textContent.includes('Progress imported'));
  assert.match(await page.locator('#main').innerText(),/Restored from another device/);
  record('import cancellation preserves state; confirmed import restores valid version-2 records');
  const legacy=JSON.stringify({version:1,last:'g0',read:['g0'],notes:{g0:'Preserve these old notes'},quiz:{}});
  await page.evaluate(value=>localStorage.setItem('data-engineering-lab:progress:v1',value),legacy);
  await page.reload();await page.locator('#export-legacy').waitFor();
  const legacyWait=page.waitForEvent('download');await page.locator('#export-legacy').click();
  await (await legacyWait).saveAs(path.join(evidence,'legacy.json'));
  assert.equal(await readFile(path.join(evidence,'legacy.json'),'utf8'),legacy);
  assert.equal(await page.evaluate(()=>localStorage.getItem('data-engineering-lab:progress:v1')),legacy);
  await visit('g8');await page.waitForFunction(()=>location.hash==='#m15');
  record('legacy notes remain unchanged and downloadable; old links route to revised modules');
  await visit('m05');await page.locator('#search').fill('SQL');
  await page.locator('.search-result a[href="#m05"]').click();await page.locator('.quiz').waitFor();
  await page.locator('#search').fill('unfindable_zzzz');assert.equal(await page.locator('.empty-state').count(),1);
  await visit('m06');await page.goBack();await page.locator('h1').waitFor();
  record('full-text search, same-route result navigation, empty state and browser back');
  await visit('m05');await context.grantPermissions(['clipboard-read','clipboard-write']);
  await page.locator('.code-toolbar button').first().click();
  assert.ok((await page.evaluate(()=>navigator.clipboard.readText())).includes('SELECT'));
  record('code copy writes actual snippet to clipboard');
  await page.evaluate(()=>document.body.style.zoom='2');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'200% text layout');
  await page.evaluate(()=>document.body.style.zoom='');
  record('lesson layout remains contained with 200% CSS zoom');
  await page.setViewportSize({width:390,height:844});await visit('home');
  await page.locator('#menu-toggle').click();assert.equal(await page.locator('#main').evaluate(el=>el.inert),true);
  await page.locator('#navigation a[href="#m05"]').click();await page.locator('.quiz').waitFor();
  assert.equal(await page.locator('#menu-toggle').getAttribute('aria-expanded'),'false');
  assert.equal(await page.locator('#main').evaluate(el=>el.inert),false);
  await page.locator('#menu-toggle').click();await page.keyboard.press('Escape');
  assert.equal(await page.locator('#menu-toggle').getAttribute('aria-expanded'),'false');
  record('mobile drawer navigation, inert background and Escape closure');
  await visit('resources');
  for(const href of await page.locator('a[download]').evaluateAll(nodes=>nodes.map(n=>n.href)))assert.equal((await context.request.get(href)).status(),200);
  record('all seven course download links return HTTP 200');
  for(const [name,hash] of Object.entries(manifest.files)){
    if(name.startsWith('.'))continue;
    const response=await context.request.get(new URL(name,base).href);
    assert.equal(response.status(),200,name);
    assert.equal(createHash('sha256').update(await response.body()).digest('hex'),hash,'served hash '+name);
  }
  record('every non-dot public artifact served byte-for-byte as built');
  await page.evaluate(()=>localStorage.clear());await page.reload();await page.locator('h1').waitFor();
  for(const [name,width,height,id] of [['desktop',1440,1000,'home'],['mobile',390,844,'home'],['lesson-desktop',1440,1000,'m05'],['lesson-mobile',390,844,'m05']]){
    await page.setViewportSize({width,height});await visit(id);
    await page.screenshot({path:path.join(evidence,name+'.png'),fullPage:false});
  }
  assert.deepEqual(errors,[]);record('no browser JavaScript exceptions; four viewport screenshots saved');
  const blocked=await browser.newContext();
  await blocked.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw Error('blocked');}}));
  const blockedPage=await blocked.newPage();await blockedPage.goto(base+'#m00');await blockedPage.locator('.quiz').waitFor();
  assert.match(await blockedPage.locator('#toast').innerText(),/progress|saved/i);await blocked.close();
  const failure=await browser.newContext();const errorPage=await failure.newPage();
  await errorPage.route('**/course.json',route=>route.abort());await errorPage.goto(base);
  await errorPage.getByText('The course could not load.').waitFor();await failure.close();
  record('blocked storage and network failure render actionable English recovery');
  await writeFile(path.join(evidence,'verification.json'),JSON.stringify({base,checkedAt:new Date().toISOString(),checks,consoleErrors:errors,screenshots:['desktop.png','mobile.png','lesson-desktop.png','lesson-mobile.png']},null,2));
}finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
