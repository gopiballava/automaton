from invoke import task
from web.core import Core
from web.client import send_dylos
from particle.dylos import Dylos


@task
def primary_cloud(ctx):
    print(
        "Initial bootup for the main cloud server. Will handle git updates, etc. etc."
    )
    server = Core()
    server.run()


@task
def laptop(ctx):
    print(
        "Initial bootup on your laptop; currently starts up the web backend which is expected to be the same as the primary cloud server."
    )
    server = Core(local_test=True)
    server.run()


@task
def particles(ctx):
    d = Dylos()
    (large, small) = d.get_single_reading()
    send_dylos("alton.diningroom.dylos", large, small)
    
    while True:
        (large, small) = d.get_averaged_readings()
        send_dylos("alton.diningroom.dylos", large, small)
