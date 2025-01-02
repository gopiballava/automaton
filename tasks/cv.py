from invoke import task
from imager.demo import demo_loop
from imager.led import find_led, find_blue

@task
def demo(ctx):
    demo_loop()

@task
def led(ctx):
    find_led()

@task
def blue(ctx):
    find_blue()