from cloudcix.client import Client


class PAT:
    """
    The Pat Application exposes a REST API capable of managing Pod records
    """
    _application_name = 'pat'
    galaxy = Client(
        _application_name,
        'galaxy/',
    )
    pod = Client(
        _application_name,
        'pod/',
    )
