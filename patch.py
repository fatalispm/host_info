from functools import wraps


def _is_class(cls):
    return isinstance(cls, type)


def importer(path):
    """
    Function that imports module and returns module, attr pair
    :param path: str path to function
    :return: tuple(module, attribute)
    """
    target, attribute = path.rsplit('.', 1)
    target = target.split('.')
    start = target.pop(0)
    module = __import__(start)

    for comp in target:
        start += '.%s' % comp
        try:
            module = getattr(module, comp)
        except AttributeError:
            __import__(start)
            module = getattr(module, comp)
    return module, attribute


class patch(object):
    """
    Class for patching methods
    """

    def __init__(self, target, new):
        """

        :param target: str path to function
        :param new: callable function to replace target
        """
        assert callable(new), 'new must be callable'
        self.target = target
        self.new = new

    def _replace_function(self):
        """

        :return:
        """
        module, attribute = importer(self.target)
        function = getattr(module, attribute)
        self.original = function
        setattr(module, attribute, self.new)
        self.module, self.attribute = module, attribute

    def decorate_class(self, klass):
        """

        :param klass:
        """
        for item in dir(klass):
            func = getattr(klass, item)
            if callable(func) and item.startswith('test'):
                setattr(klass, item, self.decorate_callable(func))
        return klass

    def __call__(self, func):
        if _is_class(func):
            return self.decorate_class(func)
        return self.decorate_callable(func)

    def decorate_callable(self, func):

        """

        :param func:
        :return:
        """

        @wraps(func)
        def patched(*args, **kwargs):
            exc_info = tuple()
            self.__enter__()
            result = func(*args, **kwargs)
            self.__exit__(*exc_info)
            return result

        return patched

    def __enter__(self):
        self._replace_function()

    def __exit__(self, *exc_info):
        setattr(self.module, self.attribute, self.original)
