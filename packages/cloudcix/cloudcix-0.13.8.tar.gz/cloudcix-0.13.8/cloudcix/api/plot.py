from cloudcix.client import Client


class Plot:
    """
    The Plot Application exposes a REST API capable of managing historial measurement data
    """
    _application_name = 'plot'
    category = Client(
        _application_name,
        'category/',
    )
    reading = Client(
        _application_name,
        'reading/',
    )
    source = Client(
        _application_name,
        'source/',
    )
    source_share = Client(
        _application_name,
        'source_share/',
    )
    unit = Client(
        _application_name,
        'unit/',
    )
