# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class MetaSingleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in MetaSingleton.__instances:
            MetaSingleton.__instances[cls] = super(MetaSingleton, cls).__call__(
                *args, **kwargs
            )
        return MetaSingleton.__instances[cls]
