from invoke import task
from led import core

@task
def hw(ctx, offset):
    print("Hi!")
    core.hello(int(offset))

@task
def zoom(ctx):
    core.zoom()

@task
def usa(ctx):
    core.usa()

@task
def dual(ctx):
    core.dual()