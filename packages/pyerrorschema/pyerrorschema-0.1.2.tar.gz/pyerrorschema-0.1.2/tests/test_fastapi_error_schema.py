import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pyerrorschema import FastAPIErrorSchema


def test_fastapi_error_schema_initiation():
    error = FastAPIErrorSchema()
    assert error.type == ""
    assert error.msg == ""
    assert error.loc == []
    assert error.input == {}


def test_fastapi_error_schema_database_error():
    error = FastAPIErrorSchema.database_error(
        loc=["request"], input={"data": "some data"}
    )
    assert error.type == "database_error"
    assert error.msg == "Database operation failed."
    assert error.loc == ["request"]
    assert error.input == {"data": "some data"}


def test_fastapi_error_schema_file_error():
    error = FastAPIErrorSchema.file_error(
        loc=["request"], input={"data": "some data"}
    )
    assert error.type == "file_error"
    assert error.msg == "File processing failed."
    assert error.loc == ["request"]
    assert error.input == {"data": "some data"}


def test_fastapi_error_schema_validation_error():
    error = FastAPIErrorSchema.validation_error(
        loc=["request"], input={"data": "some data"}
    )
    assert error.type == "validation_error"
    assert error.msg == "Validation failed."
    assert error.loc == ["request"]
    assert error.input == {"data": "some data"}


def test_fastapi_error_schema_value_error():
    error = FastAPIErrorSchema.value_error(
        loc=["body"], input={"data": "some data"}
    )
    assert error.type == "value_error"
    assert error.msg == "Value error."
    assert error.loc == ["body"]
    assert error.input == {"data": "some data"}

def test_fastapi_error_schema_docker_error():
    error = FastAPIErrorSchema.docker_error(
        loc=["request"], input={"data": "some data"}
    )
    assert error.type == "docker_error"
    assert error.msg == "Docker operation failed."
    assert error.loc == ["request"]
    assert error.input == {"data": "some data"}


def test_fastapi_error_schema_customized_error():
    error = FastAPIErrorSchema.customized_error(
        type="customized_error",
        msg="Customized error.",
        loc=["request", "body"],
        input={"data": "some data"},
    )
    assert error.type == "customized_error"
    assert error.msg == "Customized error."
    assert error.loc == ["request", "body"]
    assert error.input == {"data": "some data"}


def test_fastapi_error_schema_to_dict():
    error = FastAPIErrorSchema.customized_error(
        type="customized_error",
        msg="Customized error.",
        loc=["request", "body"],
        input={"data": "some data"},
    )
    error_dict = error.to_dict()
    assert error_dict == {
        "type": "customized_error",
        "msg": "Customized error.",
        "loc": ["request", "body"],
        "input": {"data": "some data"},
    }
