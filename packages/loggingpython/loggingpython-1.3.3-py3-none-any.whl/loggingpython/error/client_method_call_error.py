class ClientMethodCallError(Exception):
    """
    Raised when a method intended for the client is called on the server.
    """
    pass
