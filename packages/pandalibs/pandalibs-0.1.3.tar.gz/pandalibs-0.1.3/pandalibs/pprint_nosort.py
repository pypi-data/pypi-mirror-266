import pprint


def pp(data, **kwargs):
    """Shortcut for pprint with sorting disabled."""
    pprint.pprint(data, sort_dicts=False, **kwargs)
