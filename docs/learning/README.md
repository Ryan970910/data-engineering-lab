# Website authoring

This public repository owns both the English course sources and the generated Pages site. No production checkout, business package or private history is required.

## Source ownership

- ../data-engineering/lessons/*.md: twenty authoritative course chapters.
- ../data-engineering/MANUAL.md and reference pages: learning instructions.
- ../../case_lab/CASES.md and WALKTHROUGH.md: authoritative fictional case references.
- curriculum.json and quizzes.json: chapter order and sixty explained concept questions.
- index.html, style.css and app.js: English browser interface.
- build.mjs and verify.mjs: allowlisted export and actual Chromium checks.

Root website files and the CASES.md/WALKTHROUGH.md copies under docs/data-engineering are generated. Edit their sources, not the generated copies.

## Build and test

Use Node 22+ and the pinned dependencies in package.json. If dependencies are absent, install only after the environment owner authorizes setup. Existing matching dependencies can be resolved via NODE_PATH.

~~~powershell
$env:npm_config_cache = "$PWD/.learning-runtime/npm-cache"
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD/.learning-runtime/browser-cache"
$env:TEMP = "$PWD/.learning-runtime/tmp"
$env:TMP = $env:TEMP
$env:PYTHONDONTWRITEBYTECODE = "1"
New-Item -ItemType Directory -Force $env:TEMP | Out-Null
node docs/learning/build.mjs
node docs/learning/verify.mjs
python -m unittest discover -s tests -v
python -m case_lab.demo
python docs/data-engineering/verify_course.py --workspace .learning-runtime/new-author-check
~~~

The author-check workspace must be new. Build output is .learning-runtime/site-build; screenshots and raw evidence go to .learning-runtime/course-v2-qa. The live verifier uses course-v2-qa-live.

The builder checks English content, twenty modules, sixty questions and required learning activities. It exports an explicit file list with SHA-256 hashes. The browser verifier checks every exported file and all thirty routes at desktop/mobile widths. Spark and Airflow checks are optional runtime tests, not simulated successes.

## Publication

Pages uses main at root /. Build and verify the isolated output first. Copy only manifest-listed files plus manifest.json into the repository root; never erase authoring files merely because they are not website artifacts. Review all staged files before a normal commit/push.

Never stage .learning-runtime, real records, private archives, credentials or business history. Keep core.autocrlf=false so published bytes match the manifest. After Pages builds, run:

~~~powershell
node docs/learning/verify.mjs https://ryan970910.github.io/data-engineering-lab/
~~~

Version-1 learner notes remain untouched. Version-2 progress is browser-local, exportable and not a practical grade. No backend or cloud synchronization is provided.
