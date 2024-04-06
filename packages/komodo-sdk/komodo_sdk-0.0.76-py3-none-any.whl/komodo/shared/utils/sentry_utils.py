import sentry_sdk


def sentry_trace(func):
    def wrapper(*args, **kwargs):
        transaction = sentry_sdk.Hub.current.scope.transaction
        if transaction:
            with transaction.start_child(op=func.__name__, description=func.__name__):
                return func(*args, **kwargs)
        else:
            with sentry_sdk.start_transaction(op=func.__name__, name=func.__name__):
                return func(*args, **kwargs)

    return wrapper
