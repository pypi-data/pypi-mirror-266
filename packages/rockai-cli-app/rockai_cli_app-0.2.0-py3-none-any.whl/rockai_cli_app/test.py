# from server.utils import load_predictor_from_ref


# def main():
#     print("In main method")
#     load_predictor_from_ref('predict: "predict.py:Predictor"')


# if __name__ == "__main__":
#     main()

from typing import Type, Any

class Animal:
    def speak(self) -> None:
        pass

class Dog(Animal):
    def speak(self) -> None:
        print("Woof!")

class Cat(Animal):
    def speak(self) -> None:
        print("Meow!")

def create_animal(animal_class: Type[Animal]) -> Animal:
    return animal_class()

# Using the create_animal function to create instances of Dog and Cat
dog = create_animal(Dog)
cat = create_animal(Cat)

dog.speak()  # Outputs: Woof!
cat.speak()  # Outputs: Meow!
