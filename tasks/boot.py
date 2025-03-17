from invoke import task
from web.core import Core
from web.client import send_dylos
from particle.dylos import Dylos
from objectifier.web import quickstart

@task
def objectifier(ctx):
    quickstart()


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

@task
def rawparticle(ctx):
    from particle.raw import Raw
    from web.client import send_raw
    d = Raw()
    count = d.get_single_reading()
    send_raw("alton.diningroom.raw_particle", count)
    
    while True:
        count = d.get_averaged_readings()
        send_raw("alton.diningroom.raw_particle", count)

@task
def pms(ctx):
    from particle.pms5003 import PMS
    from web.client import send_pms
    d = PMS()
    (small, medium, large) = d.get_single_reading()
    send_pms("alton.diningroom.pms", small, medium, large)
    
    while True:
        (small, medium, large) = d.get_averaged_readings()
        send_pms("alton.diningroom.pms", small, medium, large)
