from celery import shared_task

@shared_task(bind=True)
def tasc_func(self):
    for i in range(10):
        print(i)
    pass
    return "done"

