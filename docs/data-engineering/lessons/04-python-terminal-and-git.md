# Prepare a reproducible Python workspace

## Bridge from Python programming to repeatable jobs

You can already write Python independently. This module is not a syntax course: it checks the environment, filesystem and process contracts that make a script reproducible for another person. If you can demonstrate the evidence at the end, move on without spending time repeating familiar basics.

A terminal accepts commands for a shell. PowerShell and Bash have different syntax. A Python interpreter runs Python programs. A virtual environment selects an interpreter and its installed packages; it is not a virtual machine and does not isolate network or filesystem access.

Git records source history. It does not automatically protect untracked data, remove secrets from old commits or prove that a program runs. Reproducibility needs source version, input version, environment and configuration together.

You need only Windows Python for SQL and reference-pipeline lessons. Do not install Airflow or Spark yet. The later Linux environment is separate from this course environment and the production project.

## Guided lab: obtain the standalone course

In PowerShell, first inspect whether the destination already exists. Do not overwrite another project.

~~~powershell
Test-Path D:\projects\data-engineering-lab
~~~

If the result is False, create the parent directory if needed, then clone:

~~~powershell
New-Item -ItemType Directory -Force D:\projects | Out-Null
Set-Location D:\projects
git clone https://github.com/Ryan970910/data-engineering-lab.git
Set-Location D:\projects\data-engineering-lab
~~~

If it already exists, inspect it instead. Use git status and git remote -v to confirm what it is. Do not run another clone into an existing directory. Without Git, download the ZIP from Resources, extract it to the intended directory and note that Git commands will not apply to a ZIP checkout.

The public repository contains teaching files, not the private application's source or configuration.

## Choose the interpreter explicitly

~~~powershell
py --version
py -3 -m venv .venv
& .\.venv\Scripts\python.exe --version
& .\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
& .\.venv\Scripts\python.exe -m pip --version
~~~

If py is unavailable, install Python from its official Windows distribution or select an existing trusted interpreter by full path. Do not guess that typing python reaches the same environment as your editor. Python 3.9+ is sufficient for standard-library lessons; record your actual version. Linux tool lessons use their separately pinned combination.

The & operator tells PowerShell to execute a program path. The -c option runs a short Python statement. Using interpreter -m pip makes the package-manager relationship explicit. “pip says installed” is weak evidence unless it belongs to the interpreter running the program.

A standard Windows venv uses .venv\Scripts\python.exe. Your existing private project used a different layout, .venv\python.exe. Published lessons use the standalone standard venv path. Do not change production to match a tutorial.

## Files, variables and exit codes

~~~powershell
$lab = "docs/data-engineering/lab.py"
$work = "D:/projects/data-engineering-lab/.learning-runtime/first"
& .\.venv\Scripts\python.exe $lab seed --workspace $work
$LASTEXITCODE
Get-Content "$work/raw/roi.csv"
~~~

A variable stores a value; it does not create the path it names. Quotes keep paths containing spaces together. A nonzero process exit code signals failure under the command's contract. A log line saying “done” does not replace checking that status and the expected output.

Bash assigns variables without spaces around =, and exported variables reach child processes. PowerShell environment variables use $env:NAME. At a Python >>> prompt, neither shell's syntax is appropriate; enter exit() to return to the shell.

## Read the existing program as a contract

Read lab.py in this order: fixtures, seed/load functions, reference matching, validate, deliver, then the CLI. Trace which functions read or write files and which are pure transformations.

The reference function consumes a batch and returns relationships/decisions. The deliver function writes to SQLite. Mixing these responsibilities would make it harder to test matching without triggering effects. This is why your Python fluency is useful: you can now focus on engineering boundaries rather than learn another language.

The boolean test of a contact only excludes a missing value. It is not a valid-phone-number checker. Do not infer unimplemented cleansing behavior from a convenient helper name.

## Independent challenge

Create a CLI script that accepts an input path, prints the interpreter path, reads synthetic CSV with csv.DictReader and reports header, row count, unique ID count and missing contact count. Treat a missing file or invalid schema as a failing process. Do not catch every exception and return success.

Save your solution separately from lab.py. Use an absolute data path while launching it from two different working directories. The results should agree. Record the repository commit and environment version.

## Failure investigation

Your editor runs one Python, PowerShell another, and only one can import an installed package. Identify three commands or settings to inspect. Explain why reinstalling packages without checking interpreter identity may change nothing.

<details><summary>Reasoning guide</summary>
Compare sys.executable in the failing process, interpreter -m pip --version and the editor's selected interpreter. Working directory and module search paths are separate from package installation. A file not found is not the same problem as a module not found. Test your CLI's nonzero exit behavior as carefully as its successful output.
</details>

## Evidence to keep

Submit interpreter/version output, the CSV profiler, its successful and failing exit codes, and a launch-from-another-directory check. This demonstrates a repeatable Python job boundary. Never include credentials or production configuration.
