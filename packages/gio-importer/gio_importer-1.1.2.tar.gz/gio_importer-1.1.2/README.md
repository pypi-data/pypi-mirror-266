# Scheduler Airflow
开发基于Airflow的DAG


## 环境依赖
| |1.0|
|----|----|
|Python|3.6|

## 开发依赖
项目根路径下执行 python3 -m pip install -r requirements.txt

## DAG介绍
|名称|dag_id|用途|
|----|----|----|
|offline_backfill_dag|offline-dag-backfill|补数使用，区别重跑在于未执行过|
|offline_rerun_dag|offline-dag-rerun|重跑使用|
|offline_daily_dag|offline-daily|天任务使用|
|offline_hourly_dag|offline-hourly|小时任务使用|

### offline_backfill_dag与offline_rerun_dag 使用方式
1. 进入Airflow页面，点击DAG的Trigger DAG按钮
2. 添加Configuration参数，JSON格式：
```
{
	"dag_id":"test-daily", # 必须
	"start_time":"2021-01-10 00:00:00", # 补数时必须
	"end_time":"2021-01-12 03:00:00" # 补数时必须
}
```