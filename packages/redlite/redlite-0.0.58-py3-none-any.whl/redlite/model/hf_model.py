from .._core import NamedModel, Message, MissingDependencyError, log
from .._util import sha_digest

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
    import torch
except ImportError as err:
    raise MissingDependencyError("Please install transformers and torch libraries") from err


class HFModel(NamedModel):
    """
    Model loaded from HuggingFace hub.

    - **hf_name** (`str`): name of the model on HuggingFace hub.
    - **device** (`str | None`): which device to use for inference. If left
            unset, will not attempt to move model to accelerator. See also `device_map` parameter.
    - **device_map** (`str | None`): defines how to map model shards to devices. Use `"auto"`
            to automatically place model shards (recommended). This option can not be used
            together with the `device` option.
    - **token** (`str | None`): HuggingFace authorization token. May be needed
            for some models (e.g. Mistral).
    - **max_length** (`int`): Largest number of tokens that model can handle.
            If prompt is too big, model will output an empty string.
    - **chat_template** (`str | None`): Custom chat template.
    - **model_params** (`dict[str,Any]`): Other model params, will be passed as-is to the
            HF model constructor.
    """

    def __init__(
        self,
        hf_name: str,
        device: str | None = None,
        device_map: str | None = None,
        token: str | None = None,
        max_length: int = 8192,
        chat_template: str | None = None,
        **model_params,
    ):
        if device is not None and device_map is not None:
            raise ValueError("You can set 'device' or 'device_map', but not both!")

        config = AutoConfig.from_pretrained(hf_name, token=token)

        model_args = dict(model_params)
        if device_map is not None:
            model_args["device_map"] = device_map

        model = AutoModelForCausalLM.from_pretrained(
            hf_name,
            token=token,
            config=config,
            **model_args,
        )
        if device is not None:
            model = model.to(device)

        self.__model = model.eval()

        self.__tokenizer = AutoTokenizer.from_pretrained(
            hf_name,
            model_max_length=max_length,
            use_fast=False,
            token=token,
            trust_remote_code=True,
        )
        self.max_length = max_length

        if chat_template is not None:
            self.__tokenizer.chat_template = chat_template

        name = "hf:" + hf_name
        if chat_template is not None or len(model_params) > 0:
            obj = {x: str(model_params[x]) for x in model_params}
            if chat_template is not None:
                obj["chat_template"] = chat_template
            name += "@" + sha_digest(obj)[:6]

        super().__init__(name, self.__predict)
        print(f"HFModel {hf_name} placed on device {self.__model.device}")

    def __predict(self, messages: list[Message]) -> str:
        prompt = self.__tokenizer.apply_chat_template(messages, tokenize=False)
        inputs = self.__tokenizer(prompt, return_tensors="pt").to(self.__model.device)
        prompt_tokens = inputs["input_ids"].shape[1]
        if prompt_tokens >= self.max_length:
            log.warn(
                f"Prompt of size {prompt_tokens} does not fit into "
                + f"model max_length of {self.max_length}. Returning empty string!"
            )
            return ""

        with torch.no_grad():
            outputs = self.__model.generate(
                **inputs,
                max_new_tokens=self.max_length - prompt_tokens,
                pad_token_id=self.__tokenizer.eos_token_id,
            )

        response = outputs[0][prompt_tokens:]
        return self.__tokenizer.decode(response, skip_special_tokens=True)
