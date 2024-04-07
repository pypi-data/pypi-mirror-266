from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
import os
import signal
from rockai_cli_app.predictor import BasePredictor
import uvicorn
from rockai_cli_app.parser.config_util import parse_config_file, get_predictor_class_name,get_predictor_path
from rockai_cli_app.server.utils import (
    load_class_from_file,
    get_input_type,
    get_output_type,
)
import rockai_cli_app.data_class
import typing
import logging
from rockai_cli_app.data_class import InferenceResponse
from pathlib import Path
# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Set the initial logging level to INFO

# Create a logger
logger = logging.getLogger(__name__)


class MyFastAPI(FastAPI):
    pass

def create_app(path:Path) -> MyFastAPI:

    app: MyFastAPI = MyFastAPI()

    pred: BasePredictor = load_class_from_file(
        Path.cwd() / get_predictor_path(parse_config_file(path / "rock.yaml")),
        get_predictor_class_name(parse_config_file(path / "rock.yaml")),
        BasePredictor,
    )
    input_type = get_input_type(pred)
    output_type = get_output_type(pred)

    class InferenceRequest(
        rockai_cli_app.data_class.InferenceRequest.get_pydantic_model(
            input_type=input_type
        )
    ):
        pass

    @app.on_event("startup")
    async def start_up_event():
        logger.debug("setup start...")
        pred.setup()
        logger.debug("setup finish...")


    @app.post("/shutdown")
    async def shutdown():
        # Get the process ID of the current process
        pid = os.getpid()
        # Send a SIGINT signal to the process
        os.kill(pid, signal.SIGINT)
        return JSONResponse(content={"message": "Shutting down"}, status_code=200)


    @app.get("/")
    async def root():
        return JSONResponse(content={"docs_url": "/docs"}, status_code=200)


    @app.post(
        "/predictions",
        response_model=InferenceResponse.get_pydantic_model(input_type=input_type, output_type=output_type),
        response_model_exclude_unset=True,
    )
    async def predict(
        request_body: InferenceRequest = Body(default=None),
    ) -> typing.Any:
        logger.debug("prediction start...")
        if request_body is None or request_body.input is None:
            request_body = InferenceRequest(input={})
        request_body = request_body.dict()
        result = pred.predict(**request_body['input'])
        return result.dict()


    return app


def start_server(port):
    app = create_app(path=Path.cwd())
    uvicorn.run(app, host="0.0.0.0", port=port)
