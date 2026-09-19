# 从零掌握 Airflow 与 PySpark：SHKP Club 项目实操手册

编写日期：2026-09-19。面向：会使用当前中央 UI，但没有 Airflow／PySpark 经验的项目维护者。

本课程的终点是：你能独立设计、运行、解释、排错和恢复一条批处理数据管道，并判断它是否适合进入真实项目。完成示例不等于掌握，结业需要独立考核。

## 目录与使用方法

1. [学习地图与验收方式](#1-学习地图与验收方式)
2. [你的项目与数据工程的关系](#2-你的项目与数据工程的关系)
3. [先学会这些词](#3-先学会这些词)
4. [第 0 关：环境与命令基础](#4-第-0-关环境与命令基础)
5. [第 1 关：先用普通 Python 跑通数据管道](#5-第-1-关先用普通-python-跑通数据管道)
6. [第 2 关：数据契约与匹配正确性](#6-第-2-关数据契约与匹配正确性)
7. [第 3 关：重复执行与失败恢复](#7-第-3-关重复执行与失败恢复)
8. [第 4 关：搭建独立 Linux 学习环境](#8-第-4-关搭建独立-linux-学习环境)
9. [第 5 关：第一次运行 Airflow](#9-第-5-关第一次运行-airflow)
10. [第 6 关：Airflow 故障与调度](#10-第-6-关airflow-故障与调度)
11. [第 7 关：第一次运行 PySpark](#11-第-7-关第一次运行-pyspark)
12. [第 8 关：独立实现两类匹配](#12-第-8-关独立实现两类匹配)
13. [第 9 关：Parquet、执行计划与性能](#13-第-9-关parquet执行计划与性能)
14. [第 10 关：Airflow 调用 Spark](#14-第-10-关airflow-调用-spark)
15. [第 11 关：增量、审计与结业任务](#15-第-11-关增量审计与结业任务)
16. [排错手册](#16-排错手册)
17. [真实项目接入检查](#17-真实项目接入检查)
18. [参考资料与验证边界](#18-参考资料与验证边界)

每关按“阅读 → 预测 → 操作 → 解释 → 改题 → 验收”进行。先猜输出再运行，才能发现自己理解错在哪里。没有通过前一关，可以预览后面的概念，但不跳过欠缺的技能。

## 1. 学习地图与验收方式

建议每次 45–90 分钟。以下时间只是安排参考，不是掌握保证；以验收结果为准。

| 关卡 | 核心成果 | 参考时间 | 你交给教练的证据 |
|---|---|---:|---|
| 0 | 分清 PowerShell、Bash、解释器和路径 | 1–2 小时 | 环境命令及解释 |
| 1 | 跑通普通 Python 分阶段管道 | 2–3 小时 | 输入、结果、每阶段作用 |
| 2 | 正确处理空键、重复候选和歧义 | 3–4 小时 | 手算结果、失败样例 |
| 3 | 验证重跑和提交后超时 | 2–3 小时 | 首次／重跑／恢复三组证据 |
| 4 | D 盘上的 WSL 与两个学习环境 | 1–3 小时 | 版本和实际存储位置 |
| 5 | Airflow DAG 成功执行 | 2–3 小时 | Graph、Run ID、任务日志 |
| 6 | 重试、失败阻断、逻辑时间 | 3–5 小时 | 故障恢复与调度解释 |
| 7 | Spark DataFrame 与惰性计算 | 2–3 小时 | 小实验及解释 |
| 8 | 用 Spark 独立实现匹配 | 4–6 小时 | 代码、5 个公开测试、现场改题 |
| 9 | Parquet 与有依据的性能比较 | 3–5 小时 | 计划、基准、正确性对比 |
| 10 | Airflow 编排 Spark 作业 | 3–5 小时 | 集成 DAG 与故障实验 |
| 11 | 增量批次与独立结业项目 | 5–8 小时 | 代码、恢复记录、设计说明 |

你每完成一关，在对话中写“验收第 N 关”，附命令、输出和解释。我会审查，并出一道没有照搬示例的变式题；有问题就给分级提示，修正后换题复测。不会仅凭“全绿截图”判断掌握。

详细评分、提交模板与进度表在 [ASSESSMENT.md](ASSESSMENT.md)。你不提交证据时，我无法验证进度；也不会后台自动跟踪你或把我的测试算成你的成绩。

## 2. 你的项目与数据工程的关系

### 2.1 先理解已经存在的东西

| 现有文件／目录 | 目前的职责 | 学习时对应的能力 |
|---|---|---|
| `src/shkpclub/application/bulk_import.py` | 初始化和环境分派 | 作业入口、参数契约 |
| `src/shkpclub/application/options.py` | 中央 UI 输入适配 | UI／调度器共用输入 |
| `src/shkpclub/sources/roi.py`、`buyer.py` | 来源解析与业务处理 | Extract、Transform、匹配 |
| `sources/go_park.py`、`townplace.py`、`signature_home.py`、`buyer_form.py` | 其他来源 | 多源接入与一致契约 |
| `src/shkpclub/operations/` | 更新和合并会员 | 有副作用的写入任务 |
| `src/shkpclub/infrastructure/` | 数据库、API、邮件等 | 外部系统适配与错误处理 |
| `src/shkpclub/reporting/` | 报告 | 数据产品与审计证据 |

Airflow 管“哪一步什么时候执行、依赖谁、成功还是失败”；PySpark 管“大量数据怎样筛选、转换、关联、聚合”。它们可以合作，也可以独立使用。

中央 UI 不必被替换。未来可以由 UI 提交参数，Airflow 后台执行，同一套来源处理函数供双方使用。当前课程只做隔离实验，尚未把这些组件接入中央 UI。

### 2.2 本课程保留的匹配边界

- ROI 与 Buyer：只用姓名＋散列 HKID。
- ROI／Buyer 与会员：姓名＋手机，或者姓名＋邮箱。
- ROI 与 Buyer 的手机号相同，不能替代 HKID 条件。
- 来源记录的散列 HKID 不参与会员匹配。

样本中的 `hash-a` 等是虚构标识，不是真实 HKID，也不演示真实身份信息散列。`100` 等是教学电话标识，不是合法号码样例；不要拿它们检验生产电话清洗器。

**教学约定，不能直接当作生产新规则**：空键不参与匹配；字段已经标准化；多个不同会员候选标记为 ambiguous；只把唯一匹配写入本地模拟接收端。这个隔离策略用于学习质量控制，不代表已经修改或核准生产歧义处理。

### 2.3 一条最终练习管道

```text
虚构 CSV → 固定输入快照 → 清洗／匹配 → 质量检查 → 本地模拟提交 → 报告
               │              │           │            │
             可追溯         可替换 Spark   失败阻断     可重跑
```

原始输入、处理中间结果、交付结果分别保存，才能知道错误发生在哪一步。不要只留下最终 Excel。

## 3. 先学会这些词

| 术语 | 简单解释 | 本项目例子 |
|---|---|---|
| ETL | 提取、转换、加载 | 从来源取得 ROI，清洗匹配，提交 CRM |
| Batch | 有明确输入边界的一批数据 | 某个文件或某个业务日期的记录 |
| Schema | 字段名称和类型约定 | 电话是字符串，不能丢前导零 |
| Primary key | 能唯一识别一条记录的键 | `source + id` 识别来源记录 |
| Composite key | 多列一起构成的键 | `name + hkid_hash` |
| Join | 按条件关联两份数据 | ROI 关联 Buyer |
| Candidate | 符合匹配条件的候选对象 | DAN 同时对应两名会员 |
| Idempotency／幂等 | 相同操作重做，不重复产生同一效果 | 超时后重试不新增第二笔同样提交 |
| Snapshot | 固定下来的输入副本 | 重跑继续用同一份 ROI |
| DAG | 无环的任务依赖图 | 提取完成后才能匹配 |
| Task | 一种任务定义 | quality |
| Task instance | 某次运行中的具体任务实例 | Run A 的 quality 与 Run B 的 quality |
| DAG run | 整条工作流的一次执行 | 你点击一次 Trigger |
| Retry | 同一任务实例失败后再次尝试 | 临时故障后重试 |
| XCom | Airflow 中任务间的小型信息 | 输出文件路径，不是全量会员表 |
| Driver | Spark 作业的协调端 | 你启动的 SparkSession 所在进程 |
| Executor | 执行分区计算的工作进程 | 集群工作节点；local 模式不等于集群 |
| Partition | 数据被拆成的处理单元 | 一部分匹配记录 |
| Shuffle | 按键重新分发数据 | 大表 Join 或 groupBy 可能发生 |
| Transformation | 描述怎样处理，通常延迟执行 | filter、select、join |
| Action | 触发 Spark 真正计算 | count、show、write |
| Lineage | 结果来自哪些输入和转换 | 某批提交对应哪个快照与代码版本 |
| Watermark | 增量处理中已处理的位置 | 上次成功处理的更新时间边界 |

别把 Spark 的 partition 与数据库分区、Parquet 目录分区、Airflow 任务混为一谈。它们可以相关，但不是同一个东西。

## 4. 第 0 关：环境与命令基础

### 4.1 当前已核实的机器情况

编写时，本仓库 `.venv/python.exe` 为 Python 3.9.25；WSL 命令存在但提示子系统未安装；没有发现 PATH 中的 Docker 命令。课程不要求 Docker。

课程目录：`D:\projects\data-engineering-lab\docs\data-engineering`。

运行目录：`D:\projects\data-engineering-lab\.learning-runtime`。其中数据、日志、缓存和 SQLite 不提交 Git；只保留控制忽略规则的 `.gitignore`。

### 4.2 认识命令提示符

- `PS D:\...>`：Windows PowerShell。环境变量写 `$env:NAME`。
- `ryan@machine:...$`：Ubuntu Bash。环境变量写 `$NAME`，设置用 `export`。
- `>>>`：Python 交互窗口，只接受 Python；输入 `exit()` 回到系统终端。

复制代码块内的内容，不要复制上述提示符。Windows 的 `D:\...` 在 WSL 中通常写成 `/mnt/d/...`。

### 4.3 第一组命令，不安装任何东西

在 PowerShell 执行：

```powershell
Set-Location D:\projects\data-engineering-lab
Get-Location
& .\.venv\Scripts\python.exe --version
& .\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
git status --short
wsl --list --verbose
```

`&` 的作用是执行一个程序路径。`-c` 表示把后面的短字符串作为 Python 代码运行。`git status` 是只读检查。WSL 未安装的错误在这一关不算失败：你应能识别它，而不是把错误信息当成 Python 问题。

如果 Git 报 dubious ownership，本课程的只读检查可使用：

```powershell
git -c safe.directory=D:/projects/data-engineering-lab status --short
```

不要把全局 `safe.directory=*` 当作排错办法。

**验收 G0**：给出 Python 版本、解释器完整路径、WSL 状态，并用自己的话说明“安装在另一个 Python 里的包，为什么当前 Python 可能找不到”。

## 5. 第 1 关：先用普通 Python 跑通数据管道

### 5.1 为什么先不安装 Airflow

如果还不理解输入、输出、错误和重跑，Airflow 只会把不清楚的流程画成图。本关让你看见真实的数据变化。提供的 `lab.py` 全部用标准库，现有 Python 3.9 可以运行。

### 5.2 按阶段执行

在 PowerShell：

```powershell
Set-Location D:\projects\data-engineering-lab
$lab = 'docs/data-engineering/lab.py'
$work = 'D:/projects/data-engineering-lab/.learning-runtime/g1'
& .\.venv\Scripts\python.exe $lab seed --workspace $work
Get-Content "$work/raw/roi.csv"
Get-Content "$work/raw/buyer.csv"
Get-Content "$work/raw/members.csv"
& .\.venv\Scripts\python.exe $lab extract --workspace $work
Get-Content "$work/manifest.json"
& .\.venv\Scripts\python.exe $lab match --workspace $work
Get-Content "$work/result.json"
& .\.venv\Scripts\python.exe $lab validate --workspace $work
& .\.venv\Scripts\python.exe $lab deliver --workspace $work
```

这些命令依次完成：生成虚构原始数据；校验字段并保存快照；计算两类匹配；核对结果；提交到当前练习目录内的 SQLite。

`seed` 只创建缺失文件，不覆盖已有文件。你改坏输入后再次 seed，不会神奇恢复；用新的练习目录生成一套干净数据即可。

### 5.3 文件要逐个看懂

| 文件 | 作用 | 是否可用于证明业务成功 |
|---|---|---|
| `raw/*.csv` | 来源输入 | 只能证明有输入 |
| `snapshots/<hash>.json` | 固定输入内容 | 能追踪本批数据来源 |
| `manifest.json` | 本次选择的快照与 SHA256 | 能指向输入版本 |
| `result.json` | 匹配边与每条来源记录的决定 | 需要检验内容，不只看存在 |
| `quality.json` | 数量汇总 | 数量正确不保证匹配对象正确 |
| `mock_crm.sqlite` | 本地接收端模拟 | 只能证明模拟写入 |
| `delivery.json` | 本次新增数和累计数 | 用于观察重跑 |

快照 hash 是内容的指纹，不是加密，不提供数据保密。相同的有序输入生成相同 hash；本演示调换原始行顺序也会改变 hash，这不是通用业务批次身份方案。

### 5.4 先手算，再看标准结果

先回答：ADA 的 ROI 与 Buyer 电话不同，能否匹配？CARA 邮箱相同但散列 HKID 不同，能否作 ROI–Buyer 匹配？FINN 的来源与会员都缺手机号，是否应匹配？

基准输入：8 条 ROI、7 条 Buyer、8 条会员。

标准汇总：

```json
{
  "roi_buyer_pairs": 5,
  "member_candidate_pairs": 13,
  "matched": 9,
  "ambiguous": 2,
  "unmatched": 4
}
```

其中后三项计数对象是 **15 条 ROI／Buyer 来源记录**，不是会员人数。13 是候选边数，9 是唯一匹配来源记录数。第一次 deliver 应得到 `inserted=9, total=9`。

**练习**：画出 GIA 的两路会员匹配，解释手机、邮箱同时命中同一会员为什么仍然只是一条候选边。

**验收 G1**：提交阶段命令、汇总、两条具体匹配的解释，以及你画的数据流。只运行一条 `run` 命令不算完成本关。

## 6. 第 2 关：数据契约与匹配正确性

### 6.1 学会区分四种问题

1. 文件不存在：获取输入失败。
2. 列名不正确：Schema 契约失败。
3. 列齐全但电话变成数字：类型可能有问题。
4. 类型正确但错误匹配：业务语义失败。

本演示 CSV 用字符串读取，避免手机号前导零损失。空字符串与数据库 NULL 不完全相同，Spark 关卡会同时考。

### 6.2 实验 A：字段丢失

新建 G2 练习输入：

```powershell
$work = 'D:/projects/data-engineering-lab/.learning-runtime/g2-schema'
& .\.venv\Scripts\python.exe docs/data-engineering/lab.py seed --workspace $work
notepad "$work/raw/roi.csv"
```

在记事本里只把表头 `hkid_hash` 改成 `hkid`，保存后运行 extract。

```powershell
& .\.venv\Scripts\python.exe docs/data-engineering/lab.py extract --workspace $work
$LASTEXITCODE
```

预期 `SCHEMA_ERROR` 且退出码非零。恢复字段名后再次执行。解释为什么不能用 try/except 把错误吃掉后打印“完成”。

### 6.3 实验 B：重复来源记录

再用独立目录 g2-duplicate。复制一整条 ROI 行，保留相同 id。extract 应返回 `ID_ERROR`。行数更多不代表信息更多；原始记录唯一键必须有定义。

### 6.4 实验 C：多个不同会员候选

用独立目录 g2-candidate，把会员 M007 的内容复制一行，将 id 改为 M009。运行 run。GIA 应出现两个不同会员候选，不能把 M007 与 M009 合并成同一个人。

预测新的 matched／ambiguous／候选边数，并解释应该在哪些字段上去重。不要仅按姓名去重，也不要随机选第一条会员。

### 6.5 实验 D：原始输入变化与快照

完成 extract 后修改 raw 中一条虚构电话，直接 match。因为 match 读取固定快照，结果应仍对应旧输入。再次 extract 后 match 才使用新快照。

这解释了为什么重试读取“当前最新文件”可能得到另一批数据。注意：演示 extract 会更新 manifest；正式批次需要绑定不可变的 batch id／manifest，不能让不同任务随意改同一个入口。

**验收 G2**：至少三种故障的命令、退出码、原因、修复与复测；另交一次行数没变但匹配对象改变的反例。

## 7. 第 3 关：重复执行与失败恢复

### 7.1 普通重跑

```powershell
$work = 'D:/projects/data-engineering-lab/.learning-runtime/g3-replay'
& .\.venv\Scripts\python.exe docs/data-engineering/lab.py run --workspace $work
& .\.venv\Scripts\python.exe docs/data-engineering/lab.py run --workspace $work
```

第一次新增 9 条，第二次新增 0 条，累计保持 9 条。查看 lab.py 中的主键和 INSERT OR IGNORE，说明究竟是谁防止重复。

### 7.2 更难的情况：接收端成功了，调用方却报错

```powershell
$work = 'D:/projects/data-engineering-lab/.learning-runtime/g3-timeout'
& .\.venv\Scripts\python.exe docs/data-engineering/lab.py run --workspace $work --fail-after-commit
$LASTEXITCODE
& .\.venv\Scripts\python.exe docs/data-engineering/lab.py deliver --workspace $work
```

第一次会抛出 `SIMULATED_TIMEOUT_AFTER_COMMIT`，但 SQLite 已提交；重试应得到 `inserted=0,total=9`。不能只看第一次进程失败就推断接收端没有记录。

这个例子把接收效果和去重键放在同一个数据库事务里。真实 CRM 与本地台账是两个系统：如果 CRM 已成功而台账未记录，单靠本地 INSERT OR IGNORE 不够。需要接收端支持幂等键，或使用请求标识查询结果、核对未知状态等协议。Airflow 重试本身不会提供 exactly-once。

### 7.3 人工读取模拟台账

在仓库根目录的 PowerShell，用你当前的 `$work` 值：

```powershell
& .\.venv\Scripts\python.exe -c "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); print(c.execute('select count(*) from deliveries').fetchone())" "$work/mock_crm.sqlite"
```

只对本课程路径执行。不要把业务数据库连接信息放进练习。

**独立题**：如果把 operation_key 改为“随机 UUID”或“当前时间”，重跑会怎样？如果只用姓名，又会漏掉什么？给出自己的反例。

**验收 G3**：两次正常重跑＋一次提交后故障恢复，并解释其边界。说“用了哈希所以永远不会重复”不能通过。

## 8. 第 4 关：搭建独立 Linux 学习环境

### 8.1 本课程固定组合

- Ubuntu 24.04，Python 3.12。
- Airflow 3.3.2，使用对应 Python 3.12 官方 constraints 安装。
- PySpark 4.0.1，Java 17；该版本是本课程固定基线，不宣称为最新。
- Airflow 和 Spark 分别使用 venv，不升级项目的 Python 3.9 环境。

版本信息根据官方文档核对；本机尚未安装 WSL，Linux 端安装和启动需要在本关实际完成后验收。[Airflow 安装](https://airflow.apache.org/docs/apache-airflow/stable/start.html)、[PySpark 4.0.1 安装](https://dlcdn.apache.org/spark/docs/4.0.1/api/python/getting_started/install.html)

建议为学习预留约 15–25 GB 可用空间、16 GB 系统内存；这是学习环境余量建议，不是软件最低要求。资源较少时先顺序运行服务，Spark 用 local[2]，暂停性能大数据实验。

### 8.2 WSL 发行版放在 D 盘

在管理员 PowerShell 中先查看：

```powershell
wsl --help
wsl --list --online
```

确认支持 `--location`，并且 D:\WSL\ClubDE 没有已有发行版数据后：

```powershell
wsl --install -d Ubuntu-24.04 --location D:\WSL\ClubDE
```

按系统提示重启，首次进入 Ubuntu 时创建 Linux 用户及密码。输入 Linux 密码通常不显示字符，这是正常行为。之后运行：

```powershell
wsl --list --verbose
wsl -d Ubuntu-24.04
```

WSL 列表要显示 VERSION 2。若当前 WSL 不认识 --location，先按微软说明更新 WSL 并再次检查，不能默默省略参数把大型发行版装到 C 盘。若已有 Ubuntu，先确认其虚拟磁盘位置；不要直接注销或迁移已有发行版。

Windows 的系统组件仍可能占用系统盘；发行版、学习缓存与数据优先落 D 盘，不保证所有 Windows 内部文件零占用 C 盘。[微软命令说明](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)

### 8.3 安装 Linux 基础依赖

以下都是 Ubuntu Bash 命令，不是在 PowerShell 中执行：

```bash
sudo apt-get update
sudo apt-get install -y python3.12-venv openjdk-17-jdk
python3.12 --version
java -version
pwd
ls /mnt/d/projects/data-engineering-lab/docs/data-engineering
```

发行版位于 D 盘时，apt 的缓存和 Linux 文件也位于该虚拟磁盘内。不要在已有 C 盘发行版里安装后才考虑移动。

### 8.4 每个终端加载统一配置

```bash
source /mnt/d/projects/data-engineering-lab/docs/data-engineering/env.sh
printf '%s\n' "$CLUB_LAB_ROOT" "$AIRFLOW_HOME" "$JAVA_HOME" "$TMPDIR"
```

`source` 让变量进入当前终端；直接 `bash env.sh` 的变量不会保留在父终端。配置不含密码。所有下文 Bash 终端都先 source。

配置还让 Airflow 监听本机回环地址；课程只用于本机学习，不对公司网络开放服务。

### 8.5 两个 venv

```bash
python3.12 -m venv "$CLUB_LAB_ROOT/venvs/airflow"
python3.12 -m venv "$CLUB_LAB_ROOT/venvs/spark"
```

本课程为路径清楚，将环境放在 D 盘挂载目录。若出现 DrvFS 文件锁或性能问题，改放 D 盘发行版内部的固定 Linux 目录，并同步更改所有启动路径；不要混用两份 AIRFLOW_HOME。

安装 Airflow：

```bash
source "$CLUB_LAB_ROOT/venvs/airflow/bin/activate"
python -m pip install "apache-airflow==3.3.2" \
  --constraint https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.12.txt
python -m pip check
airflow version
python -m pip freeze > "$CLUB_LAB_ROOT/airflow-installed.txt"
deactivate
```

安装 PySpark：

```bash
source "$CLUB_LAB_ROOT/venvs/spark/bin/activate"
python -m pip install "pyspark==4.0.1"
python -m pip check
python -c 'import sys,pyspark; print(sys.executable); print(pyspark.__version__)'
python -m pip freeze > "$CLUB_LAB_ROOT/spark-installed.txt"
deactivate
```

不要把 Airflow 装进项目 .venv；不要用“pip install 所有包”解决版本冲突。constraints 固定的是安装时依赖组合，Python 小版本必须匹配 URL。

**验收 G4**：提交 WSL2、Python、Java、Airflow、PySpark 版本，以及两个解释器路径。说明发行版、pip 缓存、日志分别位于哪里。不要提交登录密码。

## 9. 第 5 关：第一次运行 Airflow

### 9.1 先建立概念

你写的 DAG 文件描述任务依赖。Scheduler 决定哪些实例可以运行；执行器负责执行；metadata database 保存调度状态；API server／UI 展示运行。它的状态数据库不是你的 CRM 数据库。

课程使用 standalone 启动本机演示组件。它方便学习，不是正式部署方案。DAG 文件顶层只定义任务，不读取会员表、不建立 SparkSession、不发送 API。

### 9.2 终端 A：持续运行服务

Ubuntu Bash：

```bash
source /mnt/d/projects/data-engineering-lab/docs/data-engineering/env.sh
source "$CLUB_LAB_ROOT/venvs/airflow/bin/activate"
airflow standalone
```

保持此终端打开。浏览器访问 http://localhost:8080，按启动输出登录。若密码没显示，Airflow 3 standalone 使用的自动生成凭据文件通常位于 `$AIRFLOW_HOME/simple_auth_manager_passwords.json.generated`；只在本机查看，不把内容发来。[官方 Quick Start](https://airflow.apache.org/docs/apache-airflow/stable/start.html)

如果不能访问，先看终端是否仍运行，再看绑定地址、端口冲突和 WSL localhost 转发，不要先重装。

### 9.3 终端 B：检查 DAG

```bash
source /mnt/d/projects/data-engineering-lab/docs/data-engineering/env.sh
source "$CLUB_LAB_ROOT/venvs/airflow/bin/activate"
airflow config get-value core dags_folder
airflow dags list-import-errors
airflow dags list
```

应找到 `club_training`，且没有该 DAG 的导入错误。服务需要一点时间发现文件；持续不出现时用 list-import-errors 定位。

在 UI 里启用该 DAG，手动 Trigger 一次。Graph 应显示：

```text
extract → transform → quality → mock_delivery → report
```

打开各任务日志，找出工作目录和质量计数；记录 Run ID。XCom 中返回的是练习目录路径，不是完整记录集。

### 9.4 阅读代码，不只看颜色

打开 `dags/club_training.py`，逐项说明：

- `schedule=None`：只手动触发，不自动每天跑。
- `catchup=False`：以后设置定时调度时，不自动补齐所有历史区间；它不禁止手动历史回填。
- `max_active_runs=1`：同一 DAG 同时最多一个 active run，不是全系统只能一个任务。
- `retries=1`：首次尝试之外还允许一次重试。
- `retry_delay=15 秒`：失败后等待时间，不是任务最长执行时间。
- `subprocess.run(..., check=True)`：子进程失败时让任务失败。
- `run_id` 派生工作目录：同一 run 重试复用；不同 run 隔离。

这里所有任务运行在同一主机，才可以共享本地文件。分布式 executor 不能假设别的机器也能看到同一路径；以后需要共享存储、对象存储或其他明确的数据传递方式。

**验收 G5**：DAG Graph、Run ID、五步日志的要点、XCom 内容类型，并解释为什么该示例不用 Spark 也能运行。

## 10. 第 6 关：Airflow 故障与调度

### 10.1 实验：真正观察一次自动重试

用编辑器修改教学 DAG 的 quality task：读取 context 中的 run_id，生成稳定 marker 路径；marker 不存在时先写 marker，再抛出 RuntimeError；存在时继续原有 validate。

提示：marker 应在该 run 的 root 下。写 marker 必须发生在 raise 前。不要用内存全局变量保存“已失败一次”，因为任务重试可能在新进程中发生。

触发一个新 run，预期 quality 先进入重试等待，再成功；下游在质量通过前不执行。记录两次尝试日志。恢复代码后再跑干净批次。

### 10.2 实验：永久错误不能靠重试治好

把质量检查改为始终抛出错误，触发新 run。预期耗尽重试后 quality failed，下游默认依赖规则阻止交付。

不要在末尾加一个永远成功的 all_done 报告节点来掩盖失败。DAG run 的最终状态与叶子任务状态和 trigger rule 有关；结束节点设计不当会造成误导。[DAG run 文档](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)

### 10.3 Clear 与新建 run

- Clear 某次 run 的任务，是让已有任务实例重新执行；是否同时清理下游应按依赖与产物变化决定。
- Trigger 新 run 创建新的运行身份；本演示因此创建新的数据目录和新的 mock SQLite。
- 本演示只证明同一工作目录内的幂等，不证明跨 run 共用 CRM 接收端的去重；结业项目需要补这个场景。

### 10.4 学会业务日期与执行时间

假设每天凌晨 02:00 调度，业务窗口由 timetable 定义。调度型数据区间常在区间结束后才执行；logical date 不是你看到任务开始运行的墙钟时间。

练习：在 DAG 副本中打印 `logical_date`、`data_interval_start`、`data_interval_end` 和实际日志时间，先手动运行，再改成定时计划观察。读取 context 时处理手动 run 可能没有你期望的日期／区间的情况。

例如使用 `schedule="0 2 * * *"` 时，默认区间可能是上一天 02:00 到当天 02:00，不能直接称为前一个自然日。若业务要 00:00–24:00，应显式确定 business_date 并读取对应快照。

### 10.5 回填练习

先用 `airflow backfill create --help` 查看当前版本参数，不照搬 Airflow 2 的旧命令。先在手动实验里用两个显式业务日期和固定虚构输入练习，再尝试窄范围回填。

需要区分：自动 catchup、手动 backfill、重新 clear 失败任务。历史回填不应该读取今天最新文件。

**验收 G6**：一次临时故障恢复、一次永久故障阻断、两次不同业务日期，以及你对重试／Clear／新 run／回填的解释。

## 11. 第 7 关：第一次运行 PySpark

### 11.1 先确认用的是 Spark 环境

在新的 Ubuntu 终端：

```bash
source /mnt/d/projects/data-engineering-lab/docs/data-engineering/env.sh
source "$CLUB_LAB_ROOT/venvs/spark/bin/activate"
python -c 'import sys; print(sys.executable)'
java -version
python
```

进入 `>>>` 后逐行输入：

```python
from pyspark.sql import SparkSession, functions as F
spark = (SparkSession.builder.master("local[2]")
         .appName("first-club-lab")
         .config("spark.sql.shuffle.partitions", "4")
         .getOrCreate())
df = spark.createDataFrame([("ADA", "100"), ("BOB", "200"), ("FINN", "")], "name string, phone string")
valid = df.filter(F.col("phone") != "")
valid.printSchema()
valid.show()
valid.count()
valid.explain("formatted")
spark.stop()
exit()
```

`local[2]` 使用本机两个执行线程，不是两台服务器。schema 明确电话为字符串。filter 返回一个新 DataFrame，原来的 df 没有被就地改掉。

### 11.2 惰性计算

`valid = df.filter(...)` 主要是在构建计算计划；`show()`、`count()` 才触发计算。同一个 DataFrame 连续执行多个 action 可能重复计算；cache/persist 也不是一调用就完成物化，需要 action。

小数据调用 collect 是允许的；对全量会员表 collect/toPandas 会把数据带回 driver，可能用尽内存。不要把 Spark 处理好的大表重新变成 Python list 再逐行关联。

### 11.3 最小独立题

自行增加一条 phone 为 None 的记录，保留非空、非空字符串电话，只输出 name，并统计数量。说明 `isNotNull()` 与 `!= ""` 为什么各有作用。

**验收 G7**：代码、schema、计数和执行计划；指出哪些行构造计划、哪些触发计算。关掉示例后，从空白文件重新写出这一小实验。

## 12. 第 8 关：独立实现两类匹配

### 12.1 练习文件与允许使用的工具

打开 `spark_exercise.py`，只实现 `build_pairs(spark, batch)`。函数初始抛出 NotImplementedError 是刻意保留的作业，不是安装失败。

返回两个 Spark DataFrame：

| 返回对象 | 必须包含的列 |
|---|---|
| roi_buyer | `roi_id, buyer_id` |
| member_candidates | `source, record_id, member_id` |

使用明确的五列字符串 schema，这样输入为空列表也能创建 DataFrame。样本已经标准化，本关不擅自增加手机号格式或姓名清洗规则。

### 12.2 分步思路，不提供完整作业答案

1. 将 roi、buyer、members 分别转成 DataFrame。
2. ROI–Buyer 使用别名区分左右列，过滤空姓名／空 HKID，按两列 Join。
3. ROI–会员分别生成姓名＋手机、姓名＋邮箱候选。
4. 用 unionByName 合并两路；只按来源身份和会员身份去重。
5. Buyer–会员同样处理。
6. 两个来源合并时保留 source，防止两个来源恰好使用同一个 id。

API 提示：`createDataFrame`、`alias`、`F.col`、`F.lit`、`isNotNull`、`join`、`select`、`unionByName`、`dropDuplicates`。Python 的 `and`／`or` 不能直接用于 Spark Column 条件，应使用 `&`／`|` 并加括号。

### 12.3 跑公开测试

Ubuntu Spark 环境：

```bash
python "$CLUB_COURSE/spark_exercise.py" \
  --evidence "$CLUB_LAB_ROOT/evidence/g8-public.json"
```

需要通过：baseline、second_member_same_contacts、same_contact_different_name、null_keys、empty_buyer 五种情况。测试比较具体匹配边，不是只比较行数。重复输出也会失败。

checker 只对很小的固定数据 collect；你的实现禁止调用 reference、collect、toPandas 或硬编码答案。公开测试代码允许阅读，但抄参考函数不算 Spark 能力。

### 12.4 高发错误

- 只按 phone Join：同电话不同姓名也被关联。
- 空字符串参与 Join：缺失信息之间形成大量假匹配。
- 手机和邮箱两路都命中同一会员但不去重：候选数翻倍。
- 按 name 去重：两个不同会员被错误合并。
- 只筛选手机号匹配成功记录：邮箱单独命中的 CARA 丢失。
- 把会员条件写成手机且邮箱：误把“或者”改为“同时”。

### 12.5 验收不止公开测试

我会让你临场处理一组新 id／新顺序／重复来源 id 的变式，解释应该报错还是继续；再要求保留匹配原因 phone/email/both，说明如何避免因此改变候选去重语义。

**验收 G8**：实现、5 个 PASS、计划、至少一道新变式。一个 JSON PASS 文件可以被手工改写，所以不能单独证明掌握。

## 13. 第 9 关：Parquet、执行计划与性能

### 13.1 中间结果为什么不用一直存 Excel

Excel 适合人工交付；Parquet 适合带 schema 的列式数据交换。它能保存数据类型，支持按列读取，常用于批量分析。Spark 写 Parquet 的目标通常是一个目录，里面有多个 part 文件，不是单个 Excel 式文件。

在 Spark 交互环境里用你自己的匹配 DataFrame：

```python
output = "/mnt/d/projects/data-engineering-lab/.learning-runtime/g9/pairs"
roi_buyer.write.mode("errorifexists").parquet(output)
again = spark.read.parquet(output)
again.printSchema()
again.show()
```

这里 roi_buyer 指你调用 build_pairs 得到的返回值，不能直接复制到一个尚未定义变量的终端。重复写同一路径应失败；想做新实验就换输出目录。学习 overwrite 前先明确允许覆盖的批次边界。

**独立题**：读回后如何证明数据相同？小样本可以比较排序后的全部边；大样本需要双方差集、重复计数、schema 和行数等检查，单独 count 相同不够。

### 13.2 三种“分区”

- Spark 数据分区：影响并行计算。
- shuffle 分区：Join／聚合数据重分发后的分区。
- 文件目录分区：如 business_date=2026-09-19，帮助筛选数据。

不要按会员 id 或 HKID 这类高基数字段创建大量目录；先按日期／来源讨论是否有筛选价值。

### 13.3 怎样做一次可信的性能实验

1. 从 1,000、10,000、100,000 条虚构数据逐级开始，确认机器负载可承受。
2. 扩展样本时给每个重复组的 id 和匹配键都加组号；否则重复复制同一键会造成多对多 Join 爆炸。
3. 正确性先过关；不能用丢记录的方法获得更快结果。
4. 分开记录启动时间、读取、匹配、输出时间。测量到 action 完成，不能只计时构建 DataFrame。
5. 固定输入、输出列、运行环境与资源；至少三次，保留原始数据和中位数。
6. 比较普通 Python／pandas／Spark 时说明算法差异。lab.py 的 O(n*m) 参考器只用于小样本，不应直接扩展到大表后宣称 Spark 快了几千倍。
7. 若改 cache，应区分首次物化与缓存命中耗时；实验结束 unpersist。

### 13.4 读计划

执行 `df.explain("formatted")`，寻找 Scan、Filter、Join、Exchange 等节点。Exchange 常提示重分发；Join 算法可能因统计、AQE 和数据量变化，不能硬性要求每次必须看到同一个算子。

只有确认右表足够小才考虑 broadcast；集群能跑不代表 driver 可以 collect 全表。数据倾斜指少数键聚集大量数据；先观察键频率，再决定处理办法。优化后必须重新比较匹配结果。[Spark 性能文档](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html)

**验收 G9**：Parquet 读回等价证明、一份测量表、一个计划解释。允许结论是“当前小批次 Spark 更慢”，只要测量合理。

## 14. 第 10 关：Airflow 调用 Spark

### 14.1 保持两个环境独立

Airflow 在自己的 venv 中启动 Spark venv 的 Python 子进程。初学阶段不要求安装 Spark provider 或集群。先确认 Airflow 能执行普通任务、Spark 能独立运行，再集成。

你需要新增自己的 `spark_job.py`，支持：

```text
--input-manifest <path> --output <path>
```

它读取固定快照，调用你已经通过测试的 build_pairs，输出 Parquet 及小型统计报告；遇到错误退出非零。不能只调用公开测试脚本然后把“5 个 PASS”当作业务处理。

### 14.2 在 transform task 中调用

下面是调用形状，需要你按自己作业文件的实际位置完善：

```python
import os
import subprocess
from pathlib import Path

runtime = Path(os.environ["CLUB_LAB_ROOT"])
spark_python = runtime / "venvs" / "spark" / "bin" / "python"
subprocess.run([
    str(spark_python), str(job_path),
    "--input-manifest", str(manifest_path),
    "--output", str(output_path),
], check=True)
```

job_path、manifest_path、output_path 是你必须在 task 内明确定义的 Path；它们不是现成全局变量。不要拼接包含用户输入的 shell 命令。

XCom 返回 manifest／产物路径。quality task 检查 Spark 产物，mock_delivery 使用通过校验的结果。原来的 lab.py quality 接受 JSON 格式，不能直接拿 Parquet 目录替换；你需要写明新的产物契约，并相应实现验证。

### 14.3 重试与输出发布

同一 run 重试必须使用同一个输入快照。Spark 写出中途失败，可能留下不完整目录；重试前应区分失败尝试目录和已经发布的有效结果。

建议实验：每次尝试写独立 attempt 目录，成功验证后发布小型 manifest；下游只读取 manifest 指向的完整产物。后续换对象存储时不能假定目录 rename 与本地文件系统语义完全一样。

### 14.4 三个验收场景

1. 正常：Airflow 五步成功，Spark 产物与基准一致。
2. Spark 抛错：transform 失败，quality 和交付不把旧结果当新结果。
3. 写出中断后重试：恢复成功且无重复交付、不读半成品。

**验收 G10**：提交 DAG、Spark job、实际运行日志和三组证据。此时才算 Airflow＋Spark 集成完成；演示 DAG 本身仍是纯 Python 版。

## 15. 第 11 关：增量、审计与结业任务

### 15.1 增量不是简单过滤“今天的数据”

设计三批虚构输入：第一批全量；第二批新增一条并修改一条；第三批带一条迟到记录。为记录增加 source_id、updated_at、event_id 或其他有意义的版本标识。

要回答：

- 用哪个时间界限提取？同一时间有多条记录如何避免遗漏？
- 写入成功之前还是之后推进 watermark？
- 第二批执行一半失败，恢复读哪份快照？
- 迟到数据如何处理？重叠窗口加去重是否足够？
- 源系统删除记录如何表示？本轮不实现也必须写明缺口。

先用简单数据库表记录批次状态，了解语义后再考虑 CDC 或流处理。

### 15.2 运行台账至少记录什么

```text
run_id / batch_id / source / business_date / input_hash / code_version
input_count / candidate_count / matched / ambiguous / rejected
started_at / finished_at / status / attempt / output_manifest
```

运行状态和业务状态要区分。例如任务成功可能代表成功产生了一份包含拒绝记录的报告；不能把“任务绿色”解释为“所有记录都成功入会”。

提交台账记录 operation_key、payload_hash、接收结果及 unknown 状态。真实个人信息不写进公开日志；关联键用访问受控的内部标识。

### 15.3 独立结业任务

以虚构 ROI、Buyer、会员为核心，再自行生成一个额外来源，选 Go Park、Townplace、Signature Home 或 Buyer Form 场景。额外来源字段由你设计并写明教学契约，不能冒充生产字段完全一致。

从空白 DAG 和 job 文件完成：

1. 显式业务日期和输入快照。
2. 数据契约验证与问题记录隔离。
3. Spark 两类匹配，保留来源、匹配原因和歧义结果。
4. Airflow 编排与明确失败传播。
5. 同一批次重跑和跨 run 的同一操作去重。
6. 提交后故障恢复与结果核对。
7. 增量两批及一条迟到数据。
8. 报告、可追踪台账和性能说明。

考核时我会临时改变一项输入或故障条件。先让你说出预测，再操作；如果必须由我写核心逻辑，则本轮标记为“辅导完成”，改天换题独立复测。

本课程通过意味着具备这个批处理场景的独立实践能力，不代表已掌握所有 Spark 集群运维、Airflow 高可用或实时流处理。

## 16. 排错手册

排错固定顺序：记录命令与环境 → 找第一条有意义的异常 → 提出一个假设 → 用最小实验验证 → 修复 → 复测。同一问题不同时改五个变量。

| 症状 | 先检查 | 下一步 |
|---|---|---|
| PowerShell 不认识 source | 是否复制了 Bash 命令 | 进入 Ubuntu 后执行 |
| Ubuntu 找不到 D:\\ 路径 | Windows／Linux 路径混用 | 改为 /mnt/d/... |
| No module named airflow | 当前 python、venv 是否正确 | activate Airflow venv，再 pip check |
| No module named pyspark | 是否在 Airflow venv | 用 Spark venv 的解释器 |
| constraints 下载 404 | Airflow 版本和 Python 小版本 | 查官方版本及 URL，别随意删约束 |
| Java gateway exited | java -version、JAVA_HOME | Java 17，记录第一条 JVM 错误 |
| Spark worker 连接失败 | WSL hostname、SPARK_LOCAL_IP | source env.sh，确认 127.0.0.1；不要关闭全部防火墙 |
| DAG 不出现 | dags_folder 与导入错误 | dags list-import-errors |
| DAG 显示旧逻辑 | 文件路径和更新时间 | 等待解析、查看导入错误，再新建 run |
| Airflow 找不到输入 | task 的工作目录、变量 | 使用绝对路径；source 后重启服务进程 |
| 新终端变量为空 | 是否重新 source | 每个终端重新 source env.sh |
| UI 端口不能连接 | standalone 是否仍运行 | 看实际端口／绑定／日志 |
| SQLite locked | 是否重复启动 standalone | 停止多余实例；确认数据库路径，没有先删库 |
| API 失败但 task 绿色 | 子进程退出码、异常被吞 | check=True／重新抛出异常 |
| 源数据行数没变但匹配错 | 只比 count | 比较具体身份边和缺失／新增集合 |
| 输出目录已存在 | errorifexists 正常保护 | 新实验用新目录，先设计覆盖边界 |
| NotImplementedError | 是否运行未完成作业 | 实现 build_pairs，不重装 Spark |
| Python 文件缩进错误 | Tab／空格混用 | 统一 4 空格，定位报错行及其上一行 |
| Spark 小数据比 Python 慢 | 启动／序列化成本 | 分阶段计时，不伪造加速结论 |
| 重试后新增数据重复 | 去重键或接收端契约 | 检查幂等边界，别只把 retries 设为 0 |

求助时提交：关卡、系统终端类型、解释器路径、完整命令、第一条异常及相关上下文、你已验证的假设。不要只发最后一行“failed”，不要附真实会员数据或凭据。

## 17. 真实项目接入检查

课程期间不调用生产 bulk-import。你可以只读分析生产代码：

- options.py 当前输入来自中央 UI；怎样转换为显式任务参数？
- member_api.py 的异常如何变成调度器能识别的失败？
- buyer.py 的固定历史 Excel 路径如何变成可追踪输入？
- ROI 的 Windows 专用依赖如何与 Linux 执行环境隔离？
- 匹配样本全过，是否还需要包含现有生产清洗边界的回归集？答案是需要。
- API 的重试、限流、未知结果和真实幂等协议由谁负责？

这些是接入设计题，不是本课程对生产代码的自动修改授权。形成书面方案、跑脱敏离线回归并确认外部写入边界后，再安排真实接入。

你此前要求保持不变的业务行为仍然保持不变。教学样本的歧义隔离、空值约定不能直接覆盖既有生产逻辑。

## 18. 参考资料与验证边界

### 18.1 按关卡查资料，不一次看完

- G4：[Microsoft WSL 安装](https://learn.microsoft.com/en-us/windows/wsl/install)、[命令和 --location](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)。
- G4–G5：[Airflow Quick Start](https://airflow.apache.org/docs/apache-airflow/stable/start.html)、[课程使用的 constraints](https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.12.txt)。
- G5：[TaskFlow](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/taskflow.html)、[配置项](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html)。
- G6：[DAG Runs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)、[任务最佳实践](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)。
- G7：[Spark 4.0.1](https://spark.apache.org/docs/4.0.1/)、[安装](https://dlcdn.apache.org/spark/docs/4.0.1/api/python/getting_started/install.html)。
- G8–G9：[PySpark API](https://spark.apache.org/docs/4.0.1/api/python/reference/pyspark.sql/index.html)、[执行性能](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html)。

资料会更新。课程固定版本不会因为某网站示例变了就自动替换；升级要重新验证安装、DAG 和输出。

### 18.2 交付时的验证范围

已实际执行：Windows Python 3.9 上的离线基准管道、正确匹配汇总、重跑去重、提交后故障恢复、错误结果拒绝。完整日志见同目录 VALIDATION.md 所列 D 盘证据。

未实际执行：WSL 安装、Airflow 服务和 UI、PySpark JVM 作业、学习者写出的 Spark 练习。这台机器尚无可用 WSL；手册中的 Linux 路径和版本按官方资料编排，需在你的 G4–G8 实践中完成运行验收。

静态语法通过、示例代码存在、Airflow 页面绿色、公开测试通过、学习者独立掌握，是五种不同层级的证据。课程不会把前一层冒充后一层。

### 18.3 后续扩展

结业后按实际瓶颈选择：SQL/dbt 模型与测试、DuckDB 单机分析、容器化、对象存储、CDC、OpenLineage、Spark 集群。每次只新增一个明确解决问题的组件，并保留性能与正确性证据。

第一步现在就能做：完成第 0 关，把环境结果和解释发来。无需先装完整技术栈。
