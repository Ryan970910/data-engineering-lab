# 数据工程实战课程

本课程基于 SHKP Club 项目的 ROI、Buyer、会员匹配及批次提交场景。

从 [上手手册](MANUAL.md) 开始，按关卡练习；验收规则见 [考核与学习记录](ASSESSMENT.md)。

`lab.py` 是只使用 Python 标准库的演示管道；`spark_exercise.py` 是需要你完成的练习；`dags/club_training.py` 是 Airflow 演示 DAG。

所有数据都是虚构的。练习不导入生产包、不读取生产配置、不请求 CRM、不连接业务数据库。SQLite 只模拟提交，不等于真实 API。

运行输出、缓存和学习环境放在 D 盘，具体路径见手册。
