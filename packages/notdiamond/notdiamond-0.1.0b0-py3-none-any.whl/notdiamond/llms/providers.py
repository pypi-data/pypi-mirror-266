from notdiamond.llms.provider import NDLLMProvider


class NDLLMProviders:
    """
    NDLLMProviders serves as a registry for the supported LLM models by NotDiamond.
    It allows developers to easily specify available LLM providers for the router.

    Attributes:
        gpt_3_5_turbo (NDLLMProvider): refers to 'gpt-3.5-turbo' model by OpenAI
        gpt_4 (NDLLMProvider): refers to 'gpt-4' model by OpenAI
        gpt_4_1106_preview (NDLLMProvider): refers to 'gpt-4-1106-preview' model by OpenAI
        gpt_4_turbo_preview (NDLLMProvider): refers to 'gpt-4-turbo-preview' model by OpenAI
        claude_2_1 (NDLLMProvider): refers to 'claude-2.1' model by Anthropic
        claude_3_opus_20240229 (NDLLMProvider): refers to 'claude-3-opus-20240229' model by Anthropic
        claude_3_sonnet_20240229 (NDLLMProvider): refers to 'claude-3-sonnet-20240229' model by Anthropic
        gemini_pro (NDLLMProvider): refers to 'gemini-pro' model by Google
        command (NDLLMProvider): refers to 'command' model by Cohere
        mistral_large_latest (NDLLMProvider): refers to 'mistral-large-latest' model by Mistral AI
        mistral_medium_latest (NDLLMProvider): refers to 'mistral-medium-latest' model by Mistral AI
        mistral_small_latest (NDLLMProvider): refers to 'mistral-small-latest' model by Mistral AI
        open_mistral_7b (NDLLMProvider): refers to 'open-mistral-7b' model by Mistral AI
        open_mixtral_8x7b (NDLLMProvider): refers to 'open-mixtral-8x7b' model by Mistral AI
        codellama_34b_instruct_hf (NDLLMProvider): refers to 'CodeLlama-34b-Instruct-hf' model served via TogetherAI
        phind_codellama_34b_v2 (NDLLMProvider): refers to 'Phind-CodeLlama-34B-v2' model served via TogetherAI
        mistral_7b_instruct_v0_2 (NDLLMProvider): refers to 'Mistral-7B-Instruct-v0.2' model served via TogetherAI
        mixtral_8x7b_instruct_v0_1 (NDLLMProvider): refers to 'Mixtral-8x7B-Instruct-v0.1' model served via TogetherAI

    Note:
        This class is static and designed to be used without instantiation.
        Access its attributes directly to obtain configurations for specific LLM providers.
    """

    gpt_3_5_turbo = NDLLMProvider(
        provider="openai",
        model="gpt-3.5-turbo",
    )

    gpt_4 = NDLLMProvider(
        provider="openai",
        model="gpt-4",
    )

    gpt_4_1106_preview = NDLLMProvider(
        provider="openai",
        model="gpt-4-1106-preview",
    )

    gpt_4_turbo_preview = NDLLMProvider(
        provider="openai",
        model="gpt-4-turbo-preview",
    )

    claude_2_1 = NDLLMProvider(
        provider="anthropic",
        model="claude-2.1",
    )

    claude_3_opus_20240229 = NDLLMProvider(
        provider="anthropic",
        model="claude-3-opus-20240229",
    )

    claude_3_sonnet_20240229 = NDLLMProvider(
        provider="anthropic",
        model="claude-3-sonnet-20240229",
    )

    gemini_pro = NDLLMProvider(
        provider="google",
        model="gemini-pro",
    )

    command = NDLLMProvider(
        provider="cohere",
        model="command",
    )

    mistral_large_latest = NDLLMProvider(
        provider="mistral",
        model="mistral-large-latest",
    )

    mistral_medium_latest = NDLLMProvider(
        provider="mistral",
        model="mistral-medium-latest",
    )

    mistral_small_latest = NDLLMProvider(
        provider="mistral",
        model="mistral-small-latest",
    )

    open_mistral_7b = NDLLMProvider(
        provider="mistral",
        model="open-mistral-7b",
    )

    open_mixtral_8x7b = NDLLMProvider(
        provider="mistral",
        model="open-mixtral-8x7b",
    )

    codellama_34b_instruct_hf = NDLLMProvider(
        provider="togetherai",
        model="CodeLlama-34b-Instruct-hf",
    )

    phind_codellama_34b_v2 = NDLLMProvider(
        provider="togetherai",
        model="Phind-CodeLlama-34B-v2",
    )

    mistral_7b_instruct_v0_2 = NDLLMProvider(
        provider="togetherai",
        model="Mistral-7B-Instruct-v0.2",
    )

    mixtral_8x7b_instruct_v0_1 = NDLLMProvider(
        provider="togetherai",
        model="Mixtral-8x7B-Instruct-v0.1",
    )
