## Consoler

A terminal printer that's totally tailored to how I like terminal printouts. If this happens to also be how you like terminal printouts, this package may well be for you too.

### Installing

`poetry add consoler` or `pip install consoler`

### Usage

    from consoler import console
    console.log("This is a log level print out")
    console.info("This is an info level print out")
    console.warn("This is a warning level print out")

    try:
        1 / 0
    except Exception as e:
        console.error("Oh no!", e)


### Settings

Using with Django you set a few things in the Django settings to affect behaviour of conoler.

    DEBUG = True

If `DEBUG` is `True` consoler will print to stdout, otherwise it will send the output to loguru.

    CONSOLE_LOG_LEVEL = 'LOG'

You can set a log level for which message you want to reach the screen. Available levels are...

    LOG
    INFO
    SUCCESS
    TEMPLATE
    WARN
    ERROR

    CONSOLE_PATH_PREFIX = ''

When developing in a docker container or VM, the start of consoler's file paths might not quite match your local filesystem. Set a prefix here to prepend to the output's path string. This is super useful if you use https://github.com/dandavison/iterm2-dwim to make file paths clickable in iTerm.
