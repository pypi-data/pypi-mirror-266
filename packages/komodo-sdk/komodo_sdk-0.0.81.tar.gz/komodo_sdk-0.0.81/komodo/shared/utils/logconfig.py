import logging


def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # Create a file handler for outputting logs to a file
    file_handler = logging.FileHandler('application.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Create a console handler for outputting logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Get the root logger and add the handlers to it
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def safe_log(message, level=logging.INFO):
    try:
        if level == logging.DEBUG:
            logging.debug(message)
        elif level == logging.INFO:
            logging.info(message)
        elif level == logging.WARNING:
            logging.warning(message)
        elif level == logging.ERROR:
            logging.error(message)
        elif level == logging.CRITICAL:
            logging.critical(message)
    except Exception as e:
        print(f"Logging failed: {e}")
        print(message)


if __name__ == "__main__":
    configure_logging()
    safe_log("This is an info message")
    safe_log("This is a debug message", level=logging.DEBUG)
    safe_log("This is a warning message", level=logging.WARNING)
    safe_log("This is an error message", level=logging.ERROR)
    safe_log("This is a critical message", level=logging.CRITICAL)

    logger = logging.getLogger(__name__)
    logger.info("Informational message")
    logger.error("Error occurred", exc_info=True)  # Log exception information
