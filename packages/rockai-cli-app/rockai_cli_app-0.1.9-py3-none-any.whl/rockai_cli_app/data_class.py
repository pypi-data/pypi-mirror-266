from pydantic import BaseModel, create_model
import typing as t
from rockai_cli_app.server.types import URLPath
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class InferenceBase(BaseModel, extra="allow"):
    input: Dict[str, Any]


class InferenceRequest(InferenceBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def get_pydantic_model(cls, input_type: t.Type[t.Any]) -> t.Any:
        # dynamic_model = create_model(cls.__name__, __base__=cls, input=(input_type,...))
        dynamic_model = create_model(
            cls.__name__, __base__=cls, input=(input_type, None)
        )
        return dynamic_model


class InferenceResponse(InferenceBase):
    output: t.Any

    id: t.Optional[str] = None
    version: t.Optional[str] = None

    created_at: t.Optional[datetime] = None
    started_at: t.Optional[datetime] = None
    completed_at: t.Optional[datetime] = None

    logs: str = ""
    error: t.Optional[str] = None
    metrics: t.Optional[t.Dict[str, t.Any]] = None

    @classmethod
    def get_pydantic_model(
        cls, input_type: t.Type[t.Any], output_type: t.Type[t.Any]
    ) -> t.Any:
        return create_model(
            cls.__name__,
            __base__=InferenceResponse,
            input=(t.Optional[input_type], None),
            output=(output_type, None),
        )


class BaseInput(BaseModel):

    class Config:
        # When using `choices`, the type is converted into an enum to validate
        # But, after validation, we want to pass the actual value to predict(), not the enum object
        use_enum_values = True

    def cleanup(self) -> None:
        """
        Cleanup any temporary files created by the input.
        Later date to added file remover.
        """
        for _, value in self:
            # Handle URLPath objects specially for cleanup.
            if isinstance(value, URLPath):
                value.unlink()
            # Note this is pathlib.Path, which cog.Path is a subclass of. A pathlib.Path object shouldn't make its way here,
            # but both have an unlink() method, so may as well be safe.
            elif isinstance(value, Path):
                try:
                    value.unlink()
                except FileNotFoundError:
                    pass
