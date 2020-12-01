
imports = (
        "weixin.mq.delay_tasks",
        )

broker_url = 'redis://localhost/14'
result_backend = 'redis://localhost/14'
worker_prefetch_multiplier = 4
task_create_missing_queues = True
task_routes = ([
    ("weixin.mq.delay_tasks.*", {'queue': "delay"}),
    ],)
