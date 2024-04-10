class TerminalColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    LIGHT_GRAY = '\033[37m'
    UNDERLINE = '\033[4m'


def print_colored(color, *args, **kwargs):
    print(color, sep='', end='')
    print(*args, **kwargs)
    print(TerminalColors.ENDC, sep='', end='')


def print_warning(*args, **kwargs):
    print_colored(TerminalColors.WARNING, *args, **kwargs)


def print_error(*args, **kwargs):
    print_colored(TerminalColors.FAIL, *args, **kwargs)


def print_success(*args, **kwargs):
    print_colored(TerminalColors.OKGREEN, *args, **kwargs)


def print_info(*args, **kwargs):
    print_colored(TerminalColors.OKBLUE, *args, **kwargs)


def print_bold(*args, **kwargs):
    print_colored(TerminalColors.BOLD, *args, **kwargs)


def print_gray(*args, **kwargs):
    print_colored(TerminalColors.LIGHT_GRAY, *args, **kwargs)


def print_header(*args, **kwargs):
    print_colored(TerminalColors.HEADER, *args, **kwargs)


def print_cyan(*args, **kwargs):
    print_colored(TerminalColors.OKCYAN, *args, **kwargs)


if __name__ == '__main__':
    print_warning("This is a warning message")
    print_error("This is an error message")
    print_success("This is a success message")
    print_info("This is an info message")
    print_header("This is a header message")
    print_bold("This is a bold message")
    print_cyan("This is a cyan message")
    print_cyan({'foo', 'bar'})
    print_cyan(['foo', 'bar'])
    print_gray("This is a gray message", "foo", f"bar{44 + 44}")
