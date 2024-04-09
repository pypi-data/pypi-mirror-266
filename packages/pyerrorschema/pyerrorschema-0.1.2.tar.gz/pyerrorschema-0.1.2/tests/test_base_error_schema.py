import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pyerrorschema import ErrorSchema


def test_error_schema_instantiation():
    with pytest.raises(TypeError) as exc_info:
        ErrorSchema()

    assert str(exc_info.value) == "ErrorSchema cannot be instantiated directly!"
