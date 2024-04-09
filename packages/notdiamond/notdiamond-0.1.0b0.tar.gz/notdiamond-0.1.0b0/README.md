# Getting started with Not Diamond

Not Diamond automatically determines which model is best-suited to respond to any query. Unlike any other model router, Not Diamond is **fully privacy-preserving** and **continuously adapts to your preferences**.

# Key features

- **Maintain privacy**: All inputs are [fuzzy hashed](https://en.wikipedia.org/wiki/Fuzzy_hashing) before being sent to the Not Diamond API. We return a label for the recommended model and LLM calls go out client-side. _This means we never see your raw query strings or response outputs._
- **Maximize performance**: Not Diamond [outperforms foundation models](https://notdiamond.readme.io/v0.1.0-beta/docs/how-not-diamond-works#not-diamond-vs-claude-3-opus) out of the box. Our cold-start recommendations are based on hundreds of thousands of data points from rigorous evaluation benchmarks and real-world data.
- **Continuously improve**: By [providing feedback on routing decisions](https://notdiamond.readme.io/v0.1.0-beta/docs/personalization), Not Diamond _continuously learns_ a hyper-personalized routing algorithm optimized to your preferences and your application's requirements.
- **Reduce cost and latency**: Define explicit quality, cost, and latency tradeoffs to cut down your inference costs and achieve blazing fast speeds. Not Diamond determines which model to call in under 40ms—less than the time it takes an LLM to stream a single token.

> 🚧 Beta testing ahead
>
> Not Diamond is still in beta! Please let us know if you have any feedback or ideas on how we can improve. Tomás is at [t5@notdiamond.ai](mailto:t5@notdiamond.ai) or 917 725 2192.

> 👍 Free to use!
>
> Not Diamond is 100% free to use during beta ♡

# Installation

Requires **Python 3.9+**

```shell
pip install notdiamond
```

# API keys

> 👍 [Sign up](https://app.notdiamond.ai/) and get a Not Diamond API key.

Create a `.env` file with your Not Diamond API key, and the API keys of the models you want to route between.

```shell
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
MISTRAL_API_KEY="YOUR_MISTRAL_API_KEY"
COHERE_API_KEY="YOUR_COHERE_API_KEY"
NOTDIAMOND_API_KEY="YOUR_NOTDIAMOND_API_KEY"
```

Alternatively, you can also set API keys programmatically as described further below.

> 📘 API keys
>
> The `notdiamond` library uses your API keys to call the highest-quality LLM client-side. **We never pass your keys to our servers.** This means `notdiamond` will only call models you have access to. You can also use our router to determine the best model to call regardless of whether you have access or not ([example](https://notdiamond.readme.io/v0.1.0-beta/docs/fallbacks-and-custom-routing-logic#custom-routing-logic)). Our router supports most of the popular open and proprietary models ([full list](https://notdiamond.readme.io/v0.1.0-beta/docs/supported-models)).
>
> [Drop me a line](mailto:t5@notdiamond.ai) if you have a specific model requirement and we're happy to work with you to support it.

# Example

_If you already have existing projects in LangChain, check out our [Langchain integration guide](https://notdiamond.readme.io/v0.1.0-beta/docs/langchain-integration). An integration for OpenAI is also coming soon._

Create a `main.py` file in the same folder as the [`.env`](#api-keys) file you created earlier, or **[try it in Colab](https://colab.research.google.com/drive/1Ao-YhYF_S6QP5UGp_kYhgKps_Sw3a2RO?usp=sharing).**

```python
from notdiamond.llms.llm import NDLLM
from notdiamond.prompts.prompt import NDPromptTemplate


# Define the prompt template -> the string that will be routed to the best LLM
prompt_template = NDPromptTemplate("Write a merge sort in Python.")

# Define the available LLMs you'd like to route between
llm_providers = ['openai/gpt-3.5-turbo', 'openai/gpt-4','openai/gpt-4-1106-preview', 'openai/gpt-4-turbo-preview',
                 'anthropic/claude-2.1', 'anthropic/claude-3-sonnet-20240229', 'anthropic/claude-3-opus-20240229',
                 'google/gemini-pro']

# Create the NDLLM object -> like a 'meta-LLM' combining all of the specified models
nd_llm = NDLLM(llm_providers=llm_providers)

# After fuzzy hashing the inputs, the best LLM is determined by the ND API and the LLM is called client-side
result, session_id, provider = nd_llm.invoke(prompt_template=prompt_template)


print("ND session ID: ", session_id)  # A unique ID of the invoke. Important for personalizing ND to your use-case
print("LLM called: ", provider.model)  # The LLM routed to
print("LLM output: ", result.content)  # The LLM response
```

> 👍 **Run it!**
>
> `python main.py`
