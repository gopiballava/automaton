from invoke import task
from web.core import Core


@task
def primary_cloud(ctx):
    print(
        "Initial bootup for the main cloud server. Will handle git updates, etc. etc."
    )


@task
def laptop(ctx):
    print(
        "Initial bootup on your laptop; currently starts up the web backend which is expected to be the same as the primary cloud server."
    )
    server = Core(local_test=True)
    server.run()
