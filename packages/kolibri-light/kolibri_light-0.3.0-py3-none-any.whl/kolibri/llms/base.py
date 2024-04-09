from abc import ABC
from typing import Optional, List
from abc import abstractmethod
from pathlib import Path
import json, yaml
import warnings
from kolibri.utils.serializable import Serializable



class Response(Serializable):
    """Output of a single response."""

    def __init__(self, text, response_info=None, **kwargs):
        super().__init__(**kwargs)
        self.text=text
        """Generated text output."""

        self.response_info = response_info

    """Raw response info response from the provider"""
    """May include things like reason for finishing (e.g. in OpenAI)"""
    # TODO: add log probs

    @property
    def lc_serializable(self) -> bool:
        """This class is LangChain serializable."""
        return True


class LLMResult:
    """Class that contains all relevant information for an LLM Result."""

    def __init__(self, responses, llm_output=None, run=None):
        self.responses = responses
        """List of the things generated. This is List[List[]] because
        each input could have multiple responses."""
        self.llm_output = llm_output
        """For arbitrary LLM provider specific output."""
        self.run = run
        """Run metadata."""

    def flatten(self):
        """Flatten responses into a single list."""
        llm_results = []
        for i, gen_list in enumerate(self.responses):
            # Avoid double counting tokens in OpenAICallback
            if i == 0:
                llm_results.append(
                    LLMResult(
                        responses=[gen_list],
                        llm_output=self.llm_output,
                    )
                )
            else:
                if self.llm_output is not None:
                    llm_output = self.llm_output.copy()
                    llm_output["token_usage"] = dict()
                else:
                    llm_output = None
                llm_results.append(
                    LLMResult(
                        responses=[gen_list],
                        llm_output=llm_output,
                    )
                )
        return llm_results


class BaseLLM(ABC):
    """LLM wrapper should take in a prompt and return a string."""

    def __init__(self, cache = None):
        self.cache=cache


    @abstractmethod
    def _generate(self, prompts, **kwargs):
        """Run the LLM on the given prompts."""

    def generate_prompt(self, prompts,  **kwargs):
        prompt_strings = [p.to_string() for p in prompts]
        return self.generate(prompt_strings,  **kwargs)

    def generate(self, prompts,  **kwargs):
        """Run the LLM on the given prompt and input."""
        if not isinstance(prompts, list):
            raise ValueError(
                "Argument 'prompts' is expected to be of type List[str], received"
                f" argument of type {type(prompts)}."
            )

        output =self._generate(prompts, **kwargs)

        return output

    def __call__(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """Check Cache and run the LLM on the given prompt and input."""
        if not isinstance(prompt, str):
            raise ValueError(
                "Argument `prompt` is expected to be a string. Instead found "
                f"{type(prompt)}. If you want to run the LLM on multiple prompts, use "
                "`generate` instead."
            )

        return (
            self.generate(prompt, **kwargs)
            .responses[0][0]
            .text
        )

    def predict(self, text: str, **kwargs):
        return self(text, **kwargs)


    @property
    def _identifying_params(self):
        """Get the identifying parameters."""
        return {}

    def __str__(self) -> str:
        """Get a string representation of the object for printing."""
        cls_name = f"\033[1m{self.__class__.__name__}\033[0m"
        return f"{cls_name}\nParams: {self._identifying_params}"

    @property
    @abstractmethod
    def _llm_type(self) -> str:
        """Return type of llm."""

    def dict(self):
        """Return a dictionary of the LLM."""
        starter_dict = dict(self._identifying_params)
        starter_dict["_type"] = self._llm_type
        return starter_dict

    def save(self, file_path):
        """Save the LLM.

        Args:
            file_path: Path to file to save the LLM to.

        Example:
        .. code-block:: python

            llm.save(file_path="path/llm.yaml")
        """
        # Convert file to Path object.
        if isinstance(file_path, str):
            save_path = Path(file_path)
        else:
            save_path = file_path

        directory_path = save_path.parent
        directory_path.mkdir(parents=True, exist_ok=True)

        # Fetch dictionary to save
        prompt_dict = self.dict()

        if save_path.suffix == ".json":
            with open(file_path, "w") as f:
                json.dump(prompt_dict, f, indent=4)
        elif save_path.suffix == ".yaml":
            with open(file_path, "w") as f:
                yaml.dump(prompt_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"{save_path} must be json or yaml")


