"""DJ GPT CLI

Module to deal with prompt management and interacting with OpenAI's API
"""

import abc
import json
from enum import auto
from string import Formatter
from typing import Any, Dict, List, NamedTuple, Optional, Union

import openai
from strenum import LowercaseStrEnum

from djgpt.utils import CONSOLE, debug, retry


class TestCaseType(LowercaseStrEnum):
    HAPPY = auto()
    SAD = auto()
    HALLUCINATING = auto()


class PromptTestCase(NamedTuple):
    """Store spotify API data.

    Tuple of what we care about the URI/URLs and stash the rest just incase
    """

    prompt: str
    output: Union[List, Dict]
    case: TestCaseType


class PromptSystemMeta(abc.ABCMeta):
    """Metaclass for the PromptSystem.
    It handles the creation of new PromptSystem classes and ensures
    that they are correctly initialized based on their prompt strings.
    """

    def __new__(cls, name, bases, dct):
        prompt_parts = [
            base.prompt_part for base in reversed(bases) if hasattr(base, "prompt_part")
        ]
        prompt_parts.append(dct.get("prompt_part", ""))
        prompt = "".join(prompt_parts)

        formatter = Formatter()
        field_names = [field_name for _, field_name, _, _ in formatter.parse(prompt) if field_name]

        def init(self, **kwargs):
            for field_name in field_names:
                setattr(self, field_name, kwargs.get(field_name))

        dct["__init__"] = init
        dct["prompt"] = prompt
        return super().__new__(cls, name, bases, dct)


class PromptSystem(metaclass=PromptSystemMeta):
    """
    Abstract base class for all prompt systems.
    All subclasses must implement an 'ask' method.
    """

    @abc.abstractmethod
    def ask(self, user_prompt: str):
        """
        Abstract method for asking a question to the prompt system.
        Must be overridden by subclasses.

        Args:
            user_prompt (str): The user's question.

        Returns:
            The prompt system's response. The type of the response depends on the specific prompt system.
        """
        pass


class GPTHallucinationError(ValueError):
    """
    Exception raised for errors in the output from a model, in particular
    when the model is 'hallucinating' or producing irrelevant or erroneous output.
    """

    def __init__(
        self,
        *args,
        prompt: Optional["GPTPromptSystem"] = None,
        asked: str = None,
        output: Any = None,
    ):
        """
        Initializes HallucinationError with an error message.
        """
        self.prompt = prompt
        self.asked = asked
        self.output = output
        if not args:
            args = ("Model output is hallucinating.",)
        super().__init__(*args)


class GPTPromptSystem(PromptSystem):
    """
    A prompt system that uses the GPT-4 model to generate responses.
    """

    model = "gpt-4"
    max_tokens = 1000
    temperature = 0.9

    @retry(exception_class=openai.OpenAIError)
    def ask(self, user_prompt: str) -> str:
        """
        Asks a question to the GPT-4 model.

        Args:
            user_prompt (str): The user's question.

        Returns:
            str: The GPT-4 model's response message.
        """
        with CONSOLE.status("[bold green]Waiting for GPT..."):
            try:
                messages = [
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": user_prompt},
                ]
                response = openai.ChatCompletion.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=messages,
                )
                gpt_text = response["choices"][0]["message"]["content"]
                CONSOLE.log("[bold red]GPT Done!")
            except openai.OpenAIError as e:
                CONSOLE.log(f"[bold red]ERROR: {e}")
                raise
        debug(f"Raw GPT Response: {response}")
        debug(f"Raw GPT Text: {gpt_text}")
        return gpt_text


class AccurateAnswerPromptSystem(PromptSystem):
    prompt_part = """For any response you are an expert of high intelligence, and let's work things out in a 
    step by step way to be sure we have the right answer."""


class JSONGPTPromptSystem(GPTPromptSystem):
    """
    A GPT prompt system that attempts to control the output as valid JSON and deal with parsing outputs
    """

    prompt_part = """Ensure all output produced is strict JSON format, do not add any other text outside of valid JSON.
    Check the output step by step for invalid JSON formatting and invalid characters, always use utf8 encoded characters.\n"""

    @retry(exception_class=GPTHallucinationError, cooloff=True)
    def ask(self, user_prompt: str) -> str:
        gpt_text = super().ask(user_prompt)
        gpt_json = None  # This will also trigger a retry
        try:
            gpt_json = json.loads(gpt_text)
        except TypeError as e:
            CONSOLE.log(f"[bold red]ERROR: {e}")
            raise GPTHallucinationError(
                "Invalid JSON hallucinated.",
                prompt=self,
                asked=user_prompt,
                output=gpt_text,
            ) from e
        debug(f"GPT JSON Response: {gpt_json}")
        return gpt_json


class TestGPTPomptSystem(JSONGPTPromptSystem):
    """
    A fairly meta GPT prompt system for getting and using test cases for other GPT prompt systems
    """

    num_cases = 5

    prompt_part = """All user input to follow will be another GPT4 system prompt, can you produce some plausible user 
    prompts that would follow, and their associated outputs. Do this for {num_cases} examples across each case, that 
    would stretch the intent and meaning of the system prompt, as well as test fair conditions for a GPT model and those 
    that might create hallucinations. Provide the output as an array of JSON objects for each example with three fields 
    "prompt" as a string and "output" as the JSON that would be returned given the user prompt, and finally "case"
    with the values "happy", "sad", "hallucinating" based on how  likely we are to tax a large language model given the 
    system and user prompt combination."""

    def ask(self, user_prompt: str) -> List[PromptTestCase]:
        gpt_json = super().ask(user_prompt)
        try:
            [
                PromptTestCase(prompt=c["prompt"], output=c["output"], case=c["case"])
                for c in gpt_json
            ]
        except ValueError as e:
            if "is not a valid TestCaseType" in str(e):
                raise GPTHallucinationError(
                    f"TestCaseType was hallucinated should have been one of: {TestCaseType._member_names_}",
                    prompt=self,
                    asked=user_prompt,
                    output=gpt_json,
                ) from e


class SelfTestJSONGPTPromptSystem(JSONGPTPromptSystem):
    """
    A GPT JSON prompt system with some levels on introspection from GPT itself to produce test cases and estimates of
    performance given user data.
    """

    def test_cases(self):
        return TestGPTPomptSystem(num_cases=12).ask(self.prompt)


class IntGPTPromptSystem(GPTPromptSystem):
    prompt_part = """"You are IntegerGPT4 a mathematician who's only job is to output the integer representation of the 
    input. Only include the digits 0 to 9 in your output string."""

    max_tokens = 10

    def ask(self, user_prompt: str) -> int:
        if user_prompt.strip().isnumeric():
            try:
                integer = int(user_prompt.strip())
                return integer
            except ValueError:
                pass
        gpt_text = super().ask(user_prompt)
        debug(f"GPT Integer Response: {gpt_text}")
        try:
            integer = int(gpt_text)
        except ValueError:
            integer = None
        return integer
