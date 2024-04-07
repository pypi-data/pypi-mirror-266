from rockai_cli_app.predictor import BasePredictor
from typing import Any
from rockai_cli_app.server.types import Input
from pydantic import BaseModel

class MyTestOutput(BaseModel):
    data:str
    year:int

class Predictor(BasePredictor):
    def setup(self):
        """Load the model into memory to make running multiple predictions efficient"""
        print("model loading")

    # def predict(
    #     self
    # ) -> str:
    #     return "Prediction Successfully no input"

    def predict(
        self,
        name: str = Input(description="This is so cool"),
        size: int = Input(description="Image Size"),
    ) -> MyTestOutput:
        # return "Prediction Successfully {} {}".format(name, size)
        return MyTestOutput(data="You eat too much", year=2021)
