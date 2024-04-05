import typing

GenericType = typing.TypeVar("GenericType")

def is_registered(function) -> bool:
    """Check if this function is registered as a timer.

    :param function: Function to check.
    :return: True when this function is registered, otherwise False.
    :rtype: bool
    """

    ...

def register(function: typing.Callable, first_interval=0, persistent: bool = False):
    """Add a new function that will be called after the specified amount of seconds.
    The function gets no arguments and is expected to return either None or a float.
    If None is returned, the timer will be unregistered.
    A returned number specifies the delay until the function is called again.
    functools.partial can be used to assign some parameters.

        :param function: The function that should called.
        :type function: typing.Callable
        :param first_interval: Seconds until the callback should be called the first time.
        :param persistent: Don't remove timer when a new file is loaded.
        :type persistent: bool
    """

    ...

def unregister(function: typing.Any):
    """Unregister timer.

    :param function: Function to unregister.
    :type function: typing.Any
    """

    ...
