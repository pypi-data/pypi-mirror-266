from rockai_cli_app.predictor import BasePredictor
import importlib.util
import os.path
from rockai_cli_app.data_class import BaseInput
from typing import Type, Any, Union, List, Dict
import inspect
from pydantic import create_model, BaseModel, Field
import enum
from typing import get_args, get_origin, Iterator
from pydantic.fields import FieldInfo
from rockai_cli_app.server.types import File as CogFile, Path as CogPath, Input, URLPath
import types
from typing_extensions import Annotated

ALLOWED_INPUT_TYPES: List[Type[Any]] = [str, int, float, bool, CogFile, CogPath]


def load_class_from_file(file_path, class_name, base_class):
    """
    Dynamically load a class from a given file path, check if it is a subtype of base_class,
    and return an instance of it. Raise an error if the class is not a subtype of base_class.

    :param file_path: The path to the .py file containing the class.
    :param class_name: The name of the class to be instantiated.
    :param base_class: The class type to check against.
    :return: An instance of the class if successful.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    module_name = os.path.splitext(os.path.basename(file_path))[0]

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load spec for {module_name} from {file_path}.")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise ImportError(f"Error loading module {module_name}: {e}")

    try:
        class_ = getattr(module, class_name)
    except AttributeError:
        raise AttributeError(f"Class {class_name} not found in {file_path}.")

    if not issubclass(class_, base_class):
        raise TypeError(f"{class_name} is not a subtype of {base_class.__name__}")

    instance = class_()
    return instance


def read_file_content(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "File not found."
    except IOError:
        return "Error reading the file."


def human_readable_type_name(t: Type[Any]) -> str:
    """
    Generates a useful-for-humans label for a type. For builtin types, it's just the class name (eg "str" or "int"). For other types, it includes the module (eg "pathlib.Path" or "cog.File").

    The special case for Cog modules is because the type lives in `cog.types` internally, but just `cog` when included as a dependency.
    """
    module = t.__module__
    if module == "builtins":
        return t.__qualname__
    elif module.split(".")[0] == "cog":
        module = "cog"

    try:
        return module + "." + t.__qualname__
    except AttributeError:
        return str(t)


def readable_types_list(type_list: List[Type[Any]]) -> str:
    return ", ".join(human_readable_type_name(t) for t in type_list)


def validate_input_type(type: Type[Any], name: str) -> None:
    if type is inspect.Signature.empty:
        raise TypeError(
            f"No input type provided for parameter `{name}`. Supported input types are: {readable_types_list(ALLOWED_INPUT_TYPES)}, or a Union or List of those types."
        )
    elif type not in ALLOWED_INPUT_TYPES:
        if get_origin(type) in (Union, List, list) or (
            hasattr(types, "UnionType") and get_origin(type) is types.UnionType
        ):  # noqa: E721
            for t in get_args(type):
                validate_input_type(t, name)
        else:
            raise TypeError(
                f"Unsupported input type {human_readable_type_name(type)} for parameter `{name}`. Supported input types are: {readable_types_list(ALLOWED_INPUT_TYPES)}, or a Union or List of those types."
            )


def get_input_create_model_kwargs(signature: inspect.Signature) -> Dict[str, Any]:
    create_model_kwargs = {}

    order = 0

    for name, parameter in signature.parameters.items():
        InputType = parameter.annotation

        validate_input_type(InputType, name)

        # if no default is specified, create an empty, required input
        if parameter.default is inspect.Signature.empty:
            default = Input()
        else:
            default = parameter.default
            # If user hasn't used `Input`, then wrap it in that
            if not isinstance(default, FieldInfo):
                default = Input(default=default)

        # Fields aren't ordered, so use this pattern to ensure defined order
        # https://github.com/go-openapi/spec/pull/116
        
        default.json_schema_extra["x-order"] = order
        order += 1

        # Choices!
        if default.json_schema_extra.get("choices"):
            choices = default.json_schema_extra["choices"]
            # It will be passed automatically as 'enum' in the schema, so remove it as an extra field.
            del default.json_schema_extra["choices"]
            if InputType == str:

                class StringEnum(str, enum.Enum):
                    pass

                InputType = StringEnum(  # type: ignore
                    name, {value: value for value in choices}
                )
            elif InputType == int:
                InputType = enum.IntEnum(name, {str(value): value for value in choices})  # type: ignore
            else:
                raise TypeError(
                    f"The input {name} uses the option choices. Choices can only be used with str or int types."
                )

        create_model_kwargs[name] = (InputType, default)

    return create_model_kwargs


def get_input_type(predictor: BasePredictor) -> Type[BaseInput]:
    """
    Creates a Pydantic Input model from the arguments of a Predictor's predict() method.

    class Predictor(BasePredictor):
        def predict(self, text: str):
            ...

    programmatically creates a model like this:

    class Input(BaseModel):
        text: str
    """

    signature = inspect.signature(predictor.predict)

    return create_model(
        "Input",
        __config__=None,
        __base__=BaseInput,
        __module__=__name__,
        __validators__=None,
        **get_input_create_model_kwargs(signature)
    )  # type: ignore


def get_output_type(predictor: BasePredictor) -> Type[BaseModel]:
    """
    Creates a Pydantic Output model from the return type annotation of a Predictor's predict() method.
    """

    predict = predictor.predict
    signature = inspect.signature(predict)
    OutputType: Type[BaseModel]
    if signature.return_annotation is inspect.Signature.empty:
        raise TypeError(
            """You must set an output type. If your model can return multiple output types, you can explicitly set `Any` as the output type.

For example:

    from typing import Any

    def predict(
        self,
        image: Path = Input(description="Input image"),
    ) -> Any:
        ...
"""
        )
    else:
        OutputType = signature.return_annotation

    # The type that goes in the response is a list of the yielded type
    if get_origin(OutputType) is Iterator:
        # Annotated allows us to attach Field annotations to the list, which we use to mark that this is an iterator
        # https://pydantic-docs.helpmanual.io/usage/schema/#typingannotated-fields
        field = Field(**{"x-cog-array-type": "iterator"})  # type: ignore
        OutputType: Type[BaseModel] = Annotated[List[get_args(OutputType)[0]], field]  # type: ignore

    name = OutputType.__name__ if hasattr(OutputType, "__name__") else ""

    if name == "Output":
        return OutputType

    # We wrap the OutputType in an Output class to
    # ensure consistent naming of the interface in the schema.
    #
    # NOTE: If the OutputType.__name__ is "TrainingOutput" then cannot use
    # `__root__` here because this will create a reference for the Object.
    # e.g.
    #   {'title': 'Output', '$ref': '#/definitions/TrainingOutput' ... }
    #
    # And this reference may conflict with other objects at which
    # point the item will be namespaced and break our parsing. e.g.
    #   {'title': 'Output', '$ref': '#/definitions/predict_TrainingOutput' ... }
    #
    # So we work around this by inheriting from the original class rather
    # than using "__root__".
    if name == "TrainingOutput":

        class Output(OutputType):  # type: ignore
            pass

        return Output
    else:
        class Output(OutputType):
            # __root__: OutputType  # type: ignore
            pass

        return Output
