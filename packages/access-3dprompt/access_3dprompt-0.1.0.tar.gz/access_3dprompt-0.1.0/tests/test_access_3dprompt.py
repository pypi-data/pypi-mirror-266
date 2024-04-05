#!/usr/bin/env python3

"""
Tests for the 3dprompt access module.
"""

# pylint: disable=import-error
import access_3dprompt as a3

def test_salute():
    """Test for the hello function"""
    assert a3.salute() == "Hello from 3dprompt!"
