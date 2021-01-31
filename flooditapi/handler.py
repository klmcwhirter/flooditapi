from .flood_it import handle_request


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    return handle_request(req)
