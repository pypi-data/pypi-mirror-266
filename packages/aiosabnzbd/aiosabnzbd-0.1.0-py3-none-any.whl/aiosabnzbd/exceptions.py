"""Exceptions for SABnzbd."""


class SabnzbdError(Exception):
    """Generic error occurred in SABnzbd package."""


class SabnzbdConnectionError(SabnzbdError):
    """Error occurred while communicating to the SABnzbd API."""


class SabnzbdConnectionTimeoutError(SabnzbdError):
    """Timeout occurred while connecting to the SABnzbd API."""
