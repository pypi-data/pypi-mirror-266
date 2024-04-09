try:
    from icecream import ic, install, argumentToString
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa
    install = lambda: None

from .misc import EntryError


install()


