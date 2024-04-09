class VersionError(ImportError):
    """Import attempt failed from a library for which we support multiple versions with different import API's."""

    pass
