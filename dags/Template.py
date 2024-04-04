# -*- coding: utf-8 -*-
from airflow import DAG, utils
from datetime import timedelta, datetime
from dateutil.relativedelta import *
import os
import random
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.models import Variable
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator

def get_dynamic_schedule_interval():
    wdp_env = Variable.get("Env", default_var="prod")
    if wdp_env == "prod":
        return '0 23 * * *'
    elif wdp_env == "qa":
        return '30 22 * * *'
    elif wdp_env == "dev":
        return '0 22 * * *'
    else:
        return None

SCHEDULE_INTERVAL = get_dynamic_schedule_interval()

AIRFLOW_DAG_ID = 'name_of_dag'

Env = Variable.get("Env")

startup_timeout_seconds = 300

subnets = ["we need to add the subnet ids here"]

def slack_failed_task(context, channel=None):
    if not channel:
        channel = Variable.get("slack_monitoring", default_var="#solution-name-monitoring")

    if channel:
        slack_webhook_token = BaseHook.get_connection('slack').password
        environment = Variable.get("Env", default_var="DEV")
        slack_msg = """
                :red_circle: Task Failed. 
                *Env*: {env}
                *Task*: {task}  
                *Dag*: {dag} 
                *Execution Time*: {exec_date}  
                *Log Url*: {log_url} 
                """.format(
            env=environment,
            task=context.get('task_instance').task_id,
            dag=context.get('task_instance').dag_id,
            ti=context.get('task_instance'),
            exec_date=context.get('execution_date'),
            log_url=context.get('task_instance').log_url,
        )

        if environment == "prod":
            channel = "#solution-name-monitoring"
        else:
            channel = "#testing-name-monitoring"
            
        failed_alert = SlackWebhookOperator(
            task_id='slack_notif',
            http_conn_id='slack',
            webhook_token=slack_webhook_token,
            message=slack_msg,
            username='airflow',
            channel=channel)

        return failed_alert.execute(context=context)


def send_notifications(context, slack_channel=None):
    try:
        slack_failed_task(context, slack_channel)
    except Exception:
        pass

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': utils.dates.days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'startup_timeout_seconds': 300,
    'image_pull_policy': "IfNotPresent",
    'get_logs': True,
    'in_cluster': True,
    'is_delete_operator_pod': True,
    'on_failure_callback': send_notifications,
    'labels': {"project": "job_search-connector", "runner": "airflow"},
    'max_active_runs': 1
}

with DAG(
        dag_id=AIRFLOW_DAG_ID,
        default_args=args,
        start_date=datetime(2021, 12, 1),
        schedule_interval=SCHEDULE_INTERVAL,
        concurrency=1,
        catchup=False,
) as dag:

    start = DummyOperator(task_id='start-here', dag=dag)

    name_of_table_load = EcsRunTaskOperator(
        task_id="incr-run-page-views",
        dag=dag,
        aws_conn_id="aws_ecs",
        cluster=f"im-analytics-airflow-{Env}",
        task_definition=f"wdp-job_search-extractor-{Env}",
        awslogs_group=f'/aws/ecs/analytics/wdp-job_search-extractor-{Env}',
        awslogs_stream_prefix=f'ecs/wdp-job_search-extractor-{Env}',
        launch_type="FARGATE",
        overrides={
            "containerOverrides": [
                {
                    "name": f"wdp-job_search-extractor-{Env}",
                    "command": [
                        "python", "main.py",
                        "--table", "name_of_table",
                        "--load_type", "incr"
                    ],
                },
            ],
        },
        network_configuration={
            "awsvpcConfiguration": {
                "securityGroups": [os.environ.get("SECURITY_GROUP_ID", "add the security group id here")],
                "subnets": [subnets[random.randint(0,len(subnets)-1)]],
            },
        }
    )

    load_start = DummyOperator(task_id='load-start', dag=dag)

    load_complete = DummyOperator(task_id='load-complete', dag=dag)

    load_start.set_downstream([
        name_of_table_load
        ])

    load_complete.set_upstream([
        name_of_table_load
    ])