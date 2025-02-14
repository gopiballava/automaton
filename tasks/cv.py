from invoke import task
# from imager.demo import demo_loop
# from imager.led import find_led, find_blue

@task
def demo(ctx):
    from imager.demo import demo_loop
    demo_loop()

@task
def led(ctx):
    from imager.led import find_led
    find_led()

@task
def blue(ctx):
    from imager.led import find_blue
    find_blue()
