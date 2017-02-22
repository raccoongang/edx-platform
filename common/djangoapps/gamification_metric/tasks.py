from celery.task import task

from api_calls import APICalls


@task()
def send_api_request(data):
    api = APICalls()
    if api.is_enabled:
        api.api_call(**data)
