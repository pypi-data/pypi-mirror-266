"""This is a sample python file for testing functions from the source code."""

from __future__ import annotations

from meteoswiss_async.hello_world import hello_world


def test_hello():
    """
    This defines the expected usage, which can then be used in various test cases.
    Pytest will not execute this code directly, since the function does not contain the suffix "test"
    """
    hello_world()
