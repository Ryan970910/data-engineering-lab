// Export teaching material only. Never copy the private repository or its history.
import {readFile, writeFile, mkdir, copyFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const {marked} = await import(pathToFileURL(require.resolve('marked')).href);
const source = path.resolve(here, '../data-engineering');
const out = path.resolve(process.argv[2] || path.join(here, '../../.learning-runtime/site-build'));
if ([here, source, path.resolve(here, '../..')].includes(out)) throw Error('Use a dedicated output directory.');
const catalog = JSON.parse(await readFile(path.join(here,'curriculum.json'),'utf8'));
const quizzes = JSON.parse(await readFile(path.join(here,'quizzes.json'),'utf8'));
const resources = [
  {id:'start',title:'How to use this course',file:'MANUAL.md'},
  {id:'assessment',title:'Assessment and checkpoints',file:'ASSESSMENT.md'},
  {id:'glossary',title:'Working glossary',file:'GLOSSARY.md'},
  {id:'troubleshooting',title:'Troubleshooting',file:'TROUBLESHOOTING.md'},
  {id:'references',title:'Sources and verification limits',file:'REFERENCES.md'},
  {id:'cases',title:'Fictional cases and tool choices',file:'CASES.md',source:'../../case_lab/CASES.md'},
  {id:'case-walkthrough',title:'Fictional case code walkthrough',file:'WALKTHROUGH.md',source:'../../case_lab/WALKTHROUGH.md'}
];
const originals = {};
const exported = [];
async function put(name, content) {
  await mkdir(path.dirname(path.join(out,name)), {recursive:true});
  await writeFile(path.join(out,name), content);
  exported.push(name);
}
const adapt = text => text;
const content = [...catalog.modules,...resources];
const links = new Map(content.map(p=>[p.file,p.id]));
function render(text) {
  return marked.parse(text, {gfm:true}).replace(/href="([^"]+)"/g,(full,href)=>{
    const normalized=href.replace(/^\.\//,'');
    return links.has(normalized) ? 'href="#'+links.get(normalized)+'"' : full;
  });
}
for (const p of content) {
  if (!/^(lessons\/[\w-]+\.md|[A-Z]+\.md)$/.test(p.file)) throw Error('Invalid content path');
  const text=await readFile(p.source ? path.resolve(here,p.source) : path.join(source,p.file),'utf8');
  if (/[\u3400-\u9fff]/.test(text)) throw Error('Non-English course source: '+p.file);
  if (!text.startsWith('# ')) throw Error('Missing title: '+p.file);
  originals[p.file]=text;
  await put('docs/data-engineering/'+p.file,text);
}
const practice=['.gitattributes','README.md','lab.py','sql_lab.py','spark_exercise.py','verify_course.py','env.sh','dags/club_training.py'];
for (const file of practice) await put('docs/data-engineering/'+file,adapt(await readFile(path.join(source,file),'utf8')));
if (catalog.modules.length!==20 || Object.keys(quizzes).length!==20) throw Error('Curriculum coverage mismatch');
for (const module of catalog.modules) {
  const qs=quizzes[module.id];
  if (!qs || qs.length!==3 || qs.some(q=>q[1].length!==3 || q[3].length!==3 || !Number.isInteger(q[2]) || q[2]<0 || q[2]>2)) throw Error('Invalid quiz '+module.id);
  const text=originals[module.file];
  for (const heading of ['Guided','Independent','Failure','Evidence']) {
    if (!new RegExp('^## .*'+heading,'mi').test(text)) throw Error('Missing learning activity '+heading+' in '+module.file);
  }
}
const pages=content.map(p=>({...p,html:render(originals[p.file].replace(/^# .+\r?\n/,'')),text:originals[p.file]}));
await put('course.json',JSON.stringify({version:2,sourceDate:'2026-09-24',groups:catalog.groups,modules:catalog.modules,pages,quizzes}));
for (const file of ['index.html','style.css','app.js','favicon.svg']) {
  await copyFile(path.join(here,file),path.join(out,file));exported.push(file);
}
await put('.nojekyll','');
for (const file of ['README.md','.gitignore']) await put(file,await readFile(path.resolve(here,'../..',file),'utf8'));
for (const file of ['__init__.py','stages.py','demo.py','spark_stages.py','dag.py','CASES.md','WALKTHROUGH.md']) {
  await put('case_lab/'+file,await readFile(path.resolve(here,'../../case_lab',file),'utf8'));
}
const hashes={};
for (const name of exported.sort()) hashes[name]=createHash('sha256').update(await readFile(path.join(out,name))).digest('hex');
await put('manifest.json',JSON.stringify({files:hashes},null,2));
console.log(JSON.stringify({output:out,files:exported.length,pages:pages.length,lessons:catalog.modules.length,questions:Object.values(quizzes).flat().length,words:pages.reduce((n,p)=>n+p.text.split(/\s+/).length,0)},null,2));
