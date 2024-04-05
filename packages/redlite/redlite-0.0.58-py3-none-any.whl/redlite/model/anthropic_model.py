from .. import NamedModel, MissingDependencyError

try:
    from anthropic import Anthropic
except ImportError as err:
    raise MissingDependencyError("Please install anthropic library") from err


class AnthropicModel(NamedModel):
    """
    Model that calls Anthropic Completion API.

    - **model** (`str`): Name of the Anthropic model. Default is `"claude-3-opus-20240229"`
    - **max_tokens** (`int`): maximum number of tokens
    - **api_key** (`str | None`): Anthropic API key
    """

    def __init__(self, model="claude-3-opus-20240229", max_tokens=1024, api_key: str | None = None):
        self.model = model
        self.client = Anthropic(api_key=api_key)
        self.max_tokens = max_tokens

        super().__init__(f"anthropic-{model}", self.__chat)

    def __chat(self, messages: list) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
        )

        assert response.type == "message"
        assert response.role == "assistant"

        assert len(response.content) == 1
        assert response.content[0].type == "text"

        return response.content[0].text
