class ServerMethodCallError(Exception):
    """
    Raised when a method intended for the server is called on the client.
    """
    pass
