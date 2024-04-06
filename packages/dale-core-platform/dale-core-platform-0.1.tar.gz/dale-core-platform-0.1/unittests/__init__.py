def catch_all(func):
    def wrapper(context, *args, **kwargs):
        try:
            func(context, *args, **kwargs)
            context.exc = None
        except Exception as e:
            context.exc = e

    return wrapper