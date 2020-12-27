from .flood_it import config_logging, handle_request

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    config_logging(use_stdout=True)
    return handle_request(req)
