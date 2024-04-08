# Import necessary libraries
from transformers import pipeline


class LingoJudge:
    model_name = "wayveai/Lingo-Judge"
    pipe: pipeline

    def __init__(self) -> None:
        self.pipe = pipeline("text-classification", model=self.model_name)

    def evaluate(self, question: str, answer: str, prediction: str) -> float:
        input = f"[CLS]\nQuestion: {question}\nAnswer: {answer}\nStudent: {prediction}"
        result = self.pipe(input)
        return result[0]["score"]


if __name__ == "__main__":
    model = LingoJudge()
    print(
        model.evaluate(
            "Are there any pedestrians crossing the road? If yes, how many?",
            "1",
            "Yes, there is one",
        )
    )
