from pydantic import BaseModel, ConfigDict, Field

from .utils import restrict_arguments


class ErrorSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(default="")
    msg: str = Field(default="")
    
    def __new__(cls, *args, **kwargs):
        if cls is ErrorSchema:
            raise TypeError("ErrorSchema cannot be instantiated directly!")
        return super().__new__(cls)

    def to_dict(self):
        return self.model_dump()
    
    @classmethod
    @restrict_arguments("type")
    def database_error(cls, **kwargs):
        """Factory method to create an instance for a database error."""
        defaults = {
            "type": "database_error",
            "msg": "Database operation failed.",
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    @restrict_arguments("type")
    def file_error(cls, **kwargs):
        """Factory method to create an instance for a file error."""
        defaults = {
            "type": "file_error",
            "msg": "File processing failed.",
        }
        defaults.update(kwargs)
        return cls(**defaults)
