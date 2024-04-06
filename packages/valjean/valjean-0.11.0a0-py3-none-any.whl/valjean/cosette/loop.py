from functools import update_wrapper

class LoopMarker:
    def __init__(self, values):
        self.values = tuple(values)

    def __call__(self, var):
        return Loop(var, self.values)

class Loop:
    def __init__(self, var, values):
        self.var = var
        self.values = values

    def __call__(self, wrapped):
        return LoopDecorator(wrapped, self.var, self.values)

class LoopDecorator:
    def __init__(self, wrapped, var, values):
        self.var = var
        self.values = values
        update_wrapper(self, wrapped, updated=())

    def __call__(self, *args, **kwargs):
        '''Redirect the call to the wrapped function.'''
        # pylint: disable=no-member
        return self.__wrapped__(*args, **kwargs)

    def __repr__(self):
        '''Redirect the call to the wrapped function.'''
        # pylint: disable=no-member
        return repr(self.__wrapped__)

    def get_tasks(self):
        for value in self.values:
            pass
