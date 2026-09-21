# Prepare Linux, Airflow and Spark safely

## Why a separate environment?
The production project is a Windows application with its own dependencies. Installing a scheduler and a JVM into that environment creates unrelated compatibility risks. Keep the public learning checkout and separate virtual environments. Airflow is exercised in Linux; Spark gets its own environment so its dependencies do not collide with Airflow's constraints.

This course targets Ubuntu 24.04, Python 3.12, Airflow 3.3.2 and PySpark 4.0.1 with Java 17. These are teaching targets, not an instruction to upgrade production. Actual installation and runtime must be verified on your machine.

## Understand the terminals and paths
PowerShell runs Windows commands and uses paths such as D:\projects\data-engineering-lab. Ubuntu Bash sees that directory as /mnt/d/projects/data-engineering-lab. A Windows virtual environment cannot be reused as a Linux virtual environment.

A prompt is not part of a command. Do not paste PowerShell's $work assignment into Bash. Bash uses NAME=value with no spaces; environment variables exported in one terminal do not automatically appear in an already-open separate terminal.

## Guided lab: inspect before installing
In PowerShell:

~~~powershell
wsl --status
wsl --list --verbose
wsl --help
~~~

If WSL is already configured, inspect the distribution and storage location before making changes. Do not reinstall or delete an existing distribution. On a machine without Ubuntu, current WSL versions support a custom installation location:

~~~powershell
wsl --install -d Ubuntu-24.04 --location D:\WSL\Ubuntu-24.04
~~~

Run this only when --help confirms --location support and the destination is appropriate. Windows may require administrator approval and a restart. If the option is unavailable, update/check WSL using the official instructions or ask for help; do not silently drop the D-drive location. Never use wsl --unregister as a routine troubleshooting step: it deletes the distribution.

In Ubuntu, install the learning prerequisites:

~~~bash
sudo apt update
sudo apt install -y python3.12-venv openjdk-17-jdk
python3.12 --version
java -version
cd /mnt/d/projects/data-engineering-lab
source docs/data-engineering/env.sh
printf '%s\n' "$CLUB_COURSE" "$CLUB_LAB_ROOT" "$JAVA_HOME"
~~~

The environment places runtime files, pip cache, temporary Spark data and Airflow state under the D-drive course folder. The distribution itself is D-backed when installed as above. Confirm sufficient free space. Do not move caches by deleting unfamiliar system folders.

## Install Airflow with matching constraints
In Ubuntu Bash:

~~~bash
python3.12 -m venv "$CLUB_LAB_ROOT/venv-airflow"
source "$CLUB_LAB_ROOT/venv-airflow/bin/activate"
python -m pip install --upgrade pip
python -m pip install "apache-airflow==3.3.2" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.12.txt"
python -m pip check
airflow version
~~~

The constraints file pins a compatible dependency set for that release and Python minor version. It is not interchangeable with a different Python version. Do not install an arbitrary plugin and assume the original compatibility guarantee still holds.

If installation fails, save the first relevant error, interpreter path and command. Repeatedly reinstalling into whichever environment happens to be active makes diagnosis harder.

## Install Spark separately
In the same Ubuntu terminal:

~~~bash
deactivate
python3.12 -m venv "$CLUB_LAB_ROOT/venv-spark"
source "$CLUB_LAB_ROOT/venv-spark/bin/activate"
python -m pip install "pyspark==4.0.1"
python -m pip check
python -c "import sys, pyspark; print(sys.executable); print(pyspark.__version__)"
java -version
~~~

Spark 4.0.1's Python installation documentation requires Python 3.9+ and Java 17 or later. This course chooses Python 3.12 and Java 17 to keep the environment concrete. Successful pip installation does not prove the JVM can start: M14 performs that check.

Mounted Windows filesystems can have different performance and permission behavior from Linux-native storage. For larger experiments, a project folder inside the D-backed distribution may be preferable; update env.sh explicitly if you change paths.

## Independent challenge
Open two new Ubuntu terminals. In each, source env.sh and activate the intended environment. Print sys.executable, tool version and runtime paths. Explain why “command not found” in a new terminal does not necessarily mean installation was lost.

Write an inventory with OS, Python, Java, Airflow, Spark and exact venv locations. Store version evidence, not passwords or the Airflow local login token.

## Failure investigation
You see $'\r': command not found while sourcing env.sh. Explain Windows CRLF versus Unix LF endings. Check the file in an editor and save it as LF; .gitattributes declares shell scripts as LF. Do not edit arbitrary system shell files to fix one course file.

<details><summary>Reasoning guide</summary>
A virtual environment selects an interpreter and packages; it does not replace the operating system or install Java. An environment variable applies to descendant processes of that terminal. Verify each layer independently instead of treating installation as a single yes/no event.
</details>

## Evidence and sources
Submit the inventory and version outputs. Mark service/JVM runtime checks pending until you actually run them.

Read the official [WSL commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands), [Airflow constrained installation](https://airflow.apache.org/docs/apache-airflow/3.3.2/installation/installing-from-pypi.html) and [Spark 4.0.1 installation requirements](https://spark.apache.org/docs/4.0.1/api/python/getting_started/install.html).
