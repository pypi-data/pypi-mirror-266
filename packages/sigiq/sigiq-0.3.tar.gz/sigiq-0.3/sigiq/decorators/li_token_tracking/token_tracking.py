import functools
import os
import datetime
import uuid
import requests

from llama_index.core.schema import NodeWithScore


_LANGSMITH_API_KEY = os.environ.get("LANGCHAIN_API_KEY")
PROJECT_NAME = os.environ.get("LANGCHAIN_PROJECT")

class LangsmithLlamaIndexTokenLogger:
    def __init__(self, **kwargs):
        self.run_type = kwargs.get("run_type", "chain")
        self.name = kwargs.get("name", "My run")
        self.run_id = str(kwargs.get("run_id"))
        self.parent_run_id = str(kwargs.get("parent_run_id", ""))
        self.llm_model = kwargs.get("llm_model", None)
        self.prompts = kwargs.get("prompts", [])
        self.input_names = kwargs.get("input_names", [])
        self.output_names = kwargs.get("output_names", [])


    def post_run(self, **kwargs):
        inputs = kwargs.get("inputs", {})
        body = {
            "id": self.run_id,
            "name": self.name,
            "run_type": self.run_type,
            "start_time": datetime.datetime.utcnow().isoformat(),
            "inputs": self.convert_input_to_openai_schema(inputs),
            "session_name": PROJECT_NAME,
        }
        if self.parent_run_id:
            body["parent_run_id"] = self.parent_run_id

        status = requests.post(
            "https://api.smith.langchain.com/runs",
            json=body,
            headers={"x-api-key": _LANGSMITH_API_KEY},
        )
        print(f"Post status:\n{status.json()}")


    def patch_run(self, **kwargs):
        outputs = kwargs.get("outputs", {})
        body = {
            "outputs": self.convert_output_to_openai_schema(outputs),
            "end_time": datetime.datetime.utcnow().isoformat(),
        }

        status = requests.patch(
            f"https://api.smith.langchain.com/runs/{self.run_id}",
            json=body,
            headers={"x-api-key": _LANGSMITH_API_KEY},
        )
        print(f"Patch status:\n{status.json()}")


    def convert_input_to_openai_schema(self, inputs):
        assert self.llm_model, "You must specify an LLM model to use this method"
        input_content = ""

        for prompt in self.prompts:
            if not isinstance(prompt, str):
                raise ValueError("Prompts must be strings")
        input_content += "".join([prompt for prompt in self.prompts])

        for input_name in self.input_names:
            if input_name not in inputs:
                raise ValueError(f"Input {input_name} not found in inputs")
            value = inputs.get(input_name)
            if isinstance(value, list):
                for v in value:
                    if isinstance(v, NodeWithScore):
                        input_content += f"{v.get_text()}{v.metadata}"
                    else:
                        input_content += f"{v}"
            else:
                input_content += f"{value}"

        openai_package = {
            "model": self.llm_model,
            "messages": [{"role": "system", "content": input_content}],
        }
        return openai_package
    

    def convert_output_to_openai_schema(self, outputs):
        assert self.llm_model, "You must specify an LLM model to use this method"
        output_content = ""

        if not self.output_names:
            output_content = f"{outputs}"
        else:
            for output_name in self.output_names:
                output_content += f"{outputs.get(output_name, '')}"

        openai_package = {
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": output_content,
                    },
                    "finish_reason": "stop",
                }
            ],
        }
        return openai_package
        

def traceable_li(**kwargs):
    name = kwargs.get("name", "My run")
    llm_model = kwargs.get("llm_model", None)
    prompts = kwargs.get("prompts", [])
    input_names = kwargs.get("input_names", [])
    output_names = kwargs.get("output_names", [])
    assert input_names, "You must provide input names"
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            inputs = { arg_name: arg_value for arg_name, arg_value in zip(func.__code__.co_varnames, args)}
            inputs.update(kwargs)

            run_id = kwargs.pop("run_id", str(uuid.uuid4()))
            parent_run_id = kwargs.pop("parent_run_id", None)

            logger = LangsmithLlamaIndexTokenLogger(run_type="llm", 
                                                    name=name, 
                                                    llm_model=llm_model, 
                                                    run_id=run_id, 
                                                    parent_run_id=parent_run_id,
                                                    prompts=prompts,
                                                    input_names=input_names,
                                                    output_names=output_names)
            logger.post_run(inputs=inputs)

            output = func(*args, **kwargs)

            logger.patch_run(outputs=output)
            return output
        return wrapper
    return decorator

