"""Wrapper around OpenAI APIs."""
from __future__ import annotations
import openai
import logging
import sys
from kolibri.llms.base import LLMResult
import warnings
from typing import Any
import tiktoken
from kolibri.llms.base import Response
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


from kolibri.llms.base import BaseLLM
from kolibri.utils.environement import get_from_dict_or_env


logger = logging.getLogger(__name__)


def update_token_usage(
    keys , response, token_usage
):
    """Update token usage."""
    _keys_to_use = keys.intersection(response["usage"])
    for _key in _keys_to_use:
        if _key not in token_usage:
            token_usage[_key] = response["usage"][_key]
        else:
            token_usage[_key] += response["usage"][_key]


def _update_response(response, stream_response):
    """Update response from the stream response."""
    response["choices"][0]["text"] += stream_response["choices"][0]["text"]
    response["choices"][0]["finish_reason"] = stream_response["choices"][0][
        "finish_reason"
    ]
    response["choices"][0]["logprobs"] = stream_response["choices"][0]["logprobs"]

def _create_retry_decorator(llm):
    import openai

    min_seconds = 4
    max_seconds = 10
    # Wait 2^x * 1 second between each retry starting with
    # 4 seconds, then up to 10 seconds, then 10 seconds afterwards
    return retry(
        reraise=True,
        stop=stop_after_attempt(llm.max_retries),
        wait=wait_exponential(multiplier=1, min=min_seconds, max=max_seconds),
        retry=(
            retry_if_exception_type(openai.error.Timeout)
            | retry_if_exception_type(openai.error.APIError)
            | retry_if_exception_type(openai.error.APIConnectionError)
            | retry_if_exception_type(openai.error.RateLimitError)
            | retry_if_exception_type(openai.error.ServiceUnavailableError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )

def completion_with_retry(llm, **kwargs):
    """Use tenacity to retry the completion call."""
    retry_decorator = _create_retry_decorator(llm)

    @retry_decorator
    def _completion_with_retry(**kwargs):
        return llm.client.create(**kwargs)

    return _completion_with_retry(**kwargs)



class BaseOpenAI(BaseLLM):
    """Wrapper around OpenAI large language models."""

    def __init__(self, cache=None,    client=None, model_name: str = "text-davinci-003", temperature: float = 0.7,
                 max_tokens: int = 256,top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, n:int = 1,best_of: int = 1,model_kwargs = {},openai_api_key = None, openai_api_base = None,openai_organization = None,
                openai_proxy = None, batch_size: int = 20 ,request_timeout = None ,logit_bias = {} , max_retries: int = 6, **kwargs):
        super().__init__(cache)
        """Initialize the OpenAI object."""
        self.model_name = kwargs.get("model_name", "text-davinci-003")
        if self.model_name.startswith("gpt-3.5-turbo") or self.model_name.startswith("gpt-4"):
            warnings.warn(
                "You are trying to use a chat model. This way of initializing it is "
                "no longer supported. Instead, please use: "
                "`from langchain.chat_models import ChatOpenAI`"
            )
        self.validate_environment(kwargs)
        self.client=client
        self.model_name=model_name
        """Model name to use."""
        self.temperature=temperature
        """What sampling temperature to use."""
        self.max_tokens=max_tokens
        """The maximum number of tokens to generate in the completion.
        -1 returns as many tokens as possible given the prompt and
        the models maximal context size."""
        self.top_p=top_p
        """Total probability mass of tokens to consider at each step."""
        self.frequency_penalty=frequency_penalty
        """Penalizes repeated tokens according to frequency."""
        self.presence_penalty=presence_penalty
        """Penalizes repeated tokens."""
        self.n=n
        """How many completions to generate for each prompt."""
        self.best_of=best_of
        """Generates best_of completions server-side and returns the "best"."""
        self.model_kwargs = model_kwargs
        """Holds any model parameters valid for `create` call not explicitly specified."""
        self.openai_api_key = openai_api_key
        self.openai_api_base = openai_api_base
        self.openai_organization = openai_organization
        # to support explicit proxy for OpenAI
        self.openai_proxy = openai_proxy
        self.batch_size=batch_size
        """Batch size to use when passing multiple documents to generate."""
        self.request_timeout = request_timeout
        """Timeout for requests to OpenAI completion API. Default is 600 seconds."""
        self.logit_bias = logit_bias
        """Adjust the probability of specific tokens being generated."""
        self.max_retries=max_retries
        """Maximum number of retries to make when generating."""


    @property
    def lc_secrets(self):
        return {"openai_api_key": "OPENAI_API_KEY"}

    @property
    def lc_serializable(self):
        return True



    def _get_invocation_params(
        self,
        stop = None,
        **kwargs: Any,
    ) -> dict:
        params = self.dict()
        params["stop"] = stop
        return {**params, **kwargs}
    def validate_environment(self, values):
        """Validate that api key and python package exists in environment."""
        self.openai_api_key = get_from_dict_or_env(
            values, "openai_api_key", "OPENAI_API_KEY"
        )
        self.openai_api_base = get_from_dict_or_env(
            values,
            "openai_api_base",
            "OPENAI_API_BASE",
            default="",
        )
        self.openai_proxy = get_from_dict_or_env(
            values,
            "openai_proxy",
            "OPENAI_PROXY",
            default="",
        )
        self.openai_organization= get_from_dict_or_env(
            values,
            "openai_organization",
            "OPENAI_ORGANIZATION",
            default="",
        )
        try:
            self.client = openai.Completion
        except ImportError:
            raise ImportError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )

    @property
    def _default_params(self):
        """Get the default parameters for calling OpenAI API."""
        normal_params = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "n": self.n,
            "request_timeout": self.request_timeout,
            "logit_bias": self.logit_bias,
        }

        # Azure gpt-35-turbo doesn't support best_of
        # don't specify best_of if it is 1
        if self.best_of > 1:
            normal_params["best_of"] = self.best_of

        return {**normal_params, **self.model_kwargs}

    def _generate(
        self,
        prompts ,
        **kwargs,
    ) :
        """Call out to OpenAI's endpoint with k unique prompts.

        Args:
            prompts: The prompts to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The full LLM output.

        Example:
            .. code-block:: python

                response = openai.generate(["Tell me a joke."])
        """
        # TODO: write a unit test for this
        params = self._invocation_params
        params = {**params, **kwargs}
        sub_prompts = self.get_sub_prompts(params, prompts)
        choices = []
        token_usage  = {}
        # Get the token usage from the response.
        # Includes prompt, completion, and total tokens used.
        _keys = {"completion_tokens", "prompt_tokens", "total_tokens"}
        for _prompts in sub_prompts:
            # list models
            response = completion_with_retry(self, prompt=_prompts, **params)
            choices.extend(response["choices"])
            update_token_usage(_keys, response, token_usage)
        return self.create_llm_result(choices, prompts, token_usage)

    def get_sub_prompts(
        self,
        params,
        prompts,
    ):
        """Get the sub prompts for llm call."""

        if params["max_tokens"] == -1:
            if len(prompts) != 1:
                raise ValueError(
                    "max_tokens set to -1 not supported for multiple inputs."
                )
            params["max_tokens"] = self.max_tokens_for_prompt(prompts[0])
        sub_prompts = [
            prompts[i : i + self.batch_size]
            for i in range(0, len(prompts), self.batch_size)
        ]
        return sub_prompts

    def create_llm_result(
        self, choices, prompts, token_usage
    ):
        """Create the LLMResult from the choices and prompts."""
        generations = []
        for i, _ in enumerate(prompts):
            sub_choices = choices[i * self.n : (i + 1) * self.n]
            generations.append(
                [
                    Response(
                        text=choice.text,
                        response_info=dict(
                            finish_reason=choice.get("finish_reason"),
                            logprobs=choice.get("logprobs"),
                        ),
                    )
                    for choice in sub_choices
                ]
            )
        llm_output = {"token_usage": token_usage, "model_name": self.model_name}
        return LLMResult(responses=generations, llm_output=llm_output)

    def prep_streaming_params(self, stop = None):
        """Prepare the params for streaming."""
        params = self._invocation_params
        if "best_of" in params and params["best_of"] != 1:
            raise ValueError("OpenAI only supports best_of == 1 for streaming")
        if stop is not None:
            if "stop" in params:
                raise ValueError("`stop` found in both the input and default params.")
            params["stop"] = stop
        params["stream"] = True
        return params

    @property
    def _invocation_params(self):
        """Get the parameters used to invoke the model."""
        openai_creds = {
            "api_key": self.openai_api_key,
            "api_base": self.openai_api_base,
            "organization": self.openai_organization,
        }
        if self.openai_proxy:
            import openai

            openai.proxy = {"http": self.openai_proxy, "https": self.openai_proxy}  # type: ignore[assignment]  # noqa: E501
        return {**openai_creds, **self._default_params}

    @property
    def _identifying_params(self):
        """Get the identifying parameters."""
        return {**{"model_name": self.model_name}, **self._default_params}

    @property
    def _llm_type(self):
        """Return type of llm."""
        return "openai"

    def get_token_ids(self, text: str):
        """Get the token IDs using the tiktoken package."""
        # tiktoken NOT supported for Python < 3.8
        if sys.version_info[1] < 8:
            return super().get_num_tokens(text)
        try:
            import tiktoken
        except ImportError:
            raise ImportError(
                "Could not import tiktoken python package. "
                "This is needed in order to calculate get_num_tokens. "
                "Please install it with `pip install tiktoken`."
            )

        enc = tiktoken.encoding_for_model(self.model_name)

        return enc.encode(text)

    @staticmethod
    def modelname_to_contextsize(modelname: str):
        """Calculate the maximum number of tokens possible to generate for a model.

        Args:
            modelname: The modelname we want to know the context size for.

        Returns:
            The maximum context size

        Example:
            .. code-block:: python

                max_tokens = openai.modelname_to_contextsize("text-davinci-003")
        """
        model_token_mapping = {
            "gpt-4": 8192,
            "gpt-4-0314": 8192,
            "gpt-4-0613": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-32k-0314": 32768,
            "gpt-4-32k-0613": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-0301": 4096,
            "gpt-3.5-turbo-0613": 4096,
            "gpt-3.5-turbo-16k": 16385,
            "gpt-3.5-turbo-16k-0613": 16385,
            "text-ada-001": 2049,
            "ada": 2049,
            "text-babbage-001": 2040,
            "babbage": 2049,
            "text-curie-001": 2049,
            "curie": 2049,
            "davinci": 2049,
            "text-davinci-003": 4097,
            "text-davinci-002": 4097,
            "code-davinci-002": 8001,
            "code-davinci-001": 8001,
            "code-cushman-002": 2048,
            "code-cushman-001": 2048,
        }

        # handling finetuned models
        if "ft-" in modelname:
            modelname = modelname.split(":")[0]

        context_size = model_token_mapping.get(modelname, None)

        if context_size is None:
            raise ValueError(
                f"Unknown model: {modelname}. Please provide a valid OpenAI model name."
                "Known models are: " + ", ".join(model_token_mapping.keys())
            )

        return context_size


    @property
    def max_context_size(self):
        """Get max context size for this model."""
        return self.modelname_to_contextsize(self.model_name)

    def max_tokens_for_prompt(self, prompt: str):
        """Calculate the maximum number of tokens possible to generate for a prompt.

        Args:
            prompt: The prompt to pass into the model.

        Returns:
            The maximum number of tokens to generate for a prompt.

        Example:
            .. code-block:: python

                max_tokens = openai.max_token_for_prompt("Tell me a joke.")
        """
        num_tokens = self.get_num_tokens(prompt)
        return self.max_context_size - num_tokens



class OpenAI(BaseOpenAI):
    """Wrapper around OpenAI large language models.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.

    Any parameters that are valid to be passed to the openai.create call can be passed
    in, even if not explicitly saved on this class.

    Example:
        .. code-block:: python

            from langchain.llms import OpenAI
            openai = OpenAI(model_name="text-davinci-003")
    """

    def __init__(self, cache, client, model_name: str = "text-davinci-003", temperature: float = 0.7,
                 max_tokens: int = 256, top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0,
                 n: int = 1, best_of: int = 1, model_kwargs={}, openai_api_key=None, openai_api_base=None,
                 openai_organization=None, openai_proxy=None, batch_size: int = 20, request_timeout=None, logit_bias={},
                 max_retries: int = 6, **kwargs):
        super().__init__(cache, client, model_name, temperature, max_tokens, top_p, frequency_penalty, presence_penalty,
                         n, best_of, model_kwargs, openai_api_key, openai_api_base, openai_organization, openai_proxy,
                         batch_size, request_timeout, logit_bias, max_retries, **kwargs)

    @property
    def _invocation_params(self):
        return {**{"model": self.model_name}, **super()._invocation_params}


class OpenAIChat(BaseOpenAI):
    """Wrapper around OpenAI Chat large language models.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.

    Any parameters that are valid to be passed to the openai.create call can be passed
    in, even if not explicitly saved on this class.

    Example:
        .. code-block:: python

            from langchain.llms import OpenAIChat
            openaichat = OpenAIChat(model_name="gpt-3.5-turbo")
    """



    def __init__(self, cache=None, client=None, model_name: str = "gpt-3.5-turbo", model_kwargs={}, openai_api_key=None,
                 openai_api_base=None, openai_proxy=None, max_retries: int = 6, prefix_messages=[],
                 streaming: bool = False, allowed_special=set(), disallowed_special="all", **kwargs):
        super().__init__(cache=cache, client=client, model_name=model_name, model_kwargs=model_kwargs, openai_api_key=openai_api_key, openai_api_base=openai_api_base, openai_proxy=openai_proxy,
                         max_retries=max_retries, **kwargs)
        kwargs["model_name"]="gpt-3.5-turbo"

        """Maximum number of retries to make when generating."""
        self.prefix_messages = prefix_messages
        """Series of messages for Chat input."""
        self.streaming=streaming
        """Whether to stream the results or not."""
        self.allowed_special = allowed_special
        """Set of special tokens that are allowed。"""
        self.disallowed_special = disallowed_special
        """Set of special tokens that are not allowed。"""



    def build_extra(cls, values):
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = {field.alias for field in cls.__fields__.values()}

        extra = values.get("model_kwargs", {})
        for field_name in list(values):
            if field_name not in all_required_field_names:
                if field_name in extra:
                    raise ValueError(f"Found {field_name} supplied twice.")
                extra[field_name] = values.pop(field_name)
        values["model_kwargs"] = extra
        return values


    def validate_environment(self, values):
        """Validate that api key and python package exists in environment."""
        self.openai_api_key = get_from_dict_or_env(
            values, "openai_api_key", "OPENAI_API_KEY"
        )
        self.openai_api_base = get_from_dict_or_env(
            values,
            "openai_api_base",
            "OPENAI_API_BASE",
            default="",
        )
        self.openai_proxy = get_from_dict_or_env(
            values,
            "openai_proxy",
            "OPENAI_PROXY",
            default="",
        )
        self.openai_organization = get_from_dict_or_env(
            values, "openai_organization", "OPENAI_ORGANIZATION", default=""
        )
        try:
            import openai

            openai.api_key = self.openai_api_key
            if self.openai_api_base:
                openai.api_base = self.openai_api_base
            if self.openai_organization:
                openai.organization = self.openai_organization
            if self.openai_proxy:
                self.openai.proxy = {"http": openai_proxy, "https": openai_proxy}  # type: ignore[assignment]  # noqa: E501
        except ImportError:
            raise ImportError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )
        try:
            self.client = openai.ChatCompletion
        except AttributeError:
            raise ValueError(
                "`openai` has no `ChatCompletion` attribute, this is likely "
                "due to an old version of the openai package. Try upgrading it "
                "with `pip install --upgrade openai`."
            )
        warnings.warn(
            "You are trying to use a chat model. This way of initializing it is "
            "no longer supported. Instead, please use: "
            "`from langchain.chat_models import ChatOpenAI`"
        )


    @property
    def _default_params(self):
        """Get the default parameters for calling OpenAI API."""
        return self.model_kwargs

    def _get_invocation_params(
        self, stop = None, **kwargs: Any
    ):
        """Get the parameters used to invoke the model."""
        return {
            "model": self.model_name,
            **super()._get_invocation_params(stop=stop),
            **self._default_params,
            **kwargs,
        }
    def _get_chat_params(self, prompts):
        # if len(prompts) > 1:
        #     raise ValueError(
        #         f"OpenAIChat currently only supports single prompt, got {prompts}"
        #     )
#        messages = prompts#self.prefix_messages + [{"role": "user", "content": prompts[0]}]
        params = {**{"model": self.model_name}, **self._default_params}
        if params.get("max_tokens") == -1:
            # for ChatGPT api, omitting max_tokens is equivalent to having no limit
            del params["max_tokens"]
        return prompts, params

    def _generate(
        self,
        prompts,
        **kwargs,
    ):
        messages, params = self._get_chat_params(prompts)
        params = {**params, **kwargs}
        _keys = {"completion_tokens", "prompt_tokens", "total_tokens"}
        token_usage  = {}
        if self.streaming:
            response = ""
            params["stream"] = True
            for stream_resp in completion_with_retry(self, messages=messages, **params):
                token = stream_resp["choices"][0]["delta"].get("content", "")
                response += token

                update_token_usage(_keys, stream_resp, token_usage)
            return LLMResult(
                responses=[[Response(text=response)]],
            )
        else:
            full_response = completion_with_retry(self, messages=messages, **params)
            update_token_usage(_keys, full_response, token_usage)
            llm_output = {
                "token_usage": full_response["usage"],
                "model_name": self.model_name,
            }

            return LLMResult(
                responses=[
                    [Response(text=full_response["choices"][0]["message"]["content"])]
                ],
                llm_output=llm_output,
            )


    @property
    def _identifying_params(self):
        """Get the identifying parameters."""
        return {**{"model_name": self.model_name}, **self._default_params}

    @property
    def _llm_type(self):
        """Return type of llm."""
        return "openai-chat"

    def get_token_ids(self, text: str):
        """Get the token IDs using the tiktoken package."""
        # tiktoken NOT supported for Python < 3.8
        if sys.version_info[1] < 8:
            return super().get_token_ids(text)
        try:
            import tiktoken
        except ImportError:
            raise ImportError(
                "Could not import tiktoken python package. "
                "This is needed in order to calculate get_num_tokens. "
                "Please install it with `pip install tiktoken`."
            )

        enc = tiktoken.encoding_for_model(self.model_name)
        return enc.encode(
            text,
            allowed_special=self.allowed_special,
            disallowed_special=self.disallowed_special,
        )




def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens