import os

broker_url = "sqs://"
broker_user = os.getenv("AWS_ACCESS_KEY_ID")
broker_password = os.getenv("AWS_SECRET_ACCESS_KEY")
broker_connection_retry_on_startup = True
task_default_queue = "map-queue"
result_backend = 'rpc://'
enable_utc = True
