from typing import Dict, List
from langsmith import Client
from langsmith.schemas import Run, Example

client = Client()


def create_dataset(dataset:Dict[str,List[str]], dataset_name:str):
    """Create a dataset"""
    examples = [(question,k) for k,v in dataset.items() for question in v]

    if not client.has_dataset(dataset_name=dataset_name):
    #TODO: if exists, update dataset
        dataset = client.create_dataset(dataset_name=dataset_name)
        inputs, outputs = zip(
            *[({"input": text}, {"output": label}) for text, label in examples]
        )
        client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)

class Evaluator:

    def __init__(self,runnable) -> None:
        self.runnable = runnable

    def predict_assistant(self, example: dict):
        """Invoke assistant for single tool call evaluation"""
        msg = [ ("user", example["input"]) ]
        result = self.runnable.invoke({"messages":msg})
        return {"response": result}

    def check_specific_tool_call(self, root_run: Run, example: Example) -> dict:
        """
        Check if the first tool call in the response matches the expected tool call.
        """
        # Expected tool call
        expected_tool_call = example.outputs['output']

        # Run
        response = root_run.outputs["response"]

        # Get tool call
        try:
            tool_call = getattr(response, 'tool_calls', [])[0]['name']
        except (IndexError, KeyError):
            tool_call = None

        score = 1 if tool_call == expected_tool_call else 0
        return {"score": score, "key": "single_tool_call"}