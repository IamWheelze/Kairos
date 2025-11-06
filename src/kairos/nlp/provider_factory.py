"""NLP Provider Factory.

Creates and manages different NLP providers based on configuration.
"""

from typing import Optional, Dict, List
from kairos.logging import get_logger
from .provider_base import NLPProvider
from .rule_based_provider import RuleBasedProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider


log = get_logger("kairos.nlp.factory")


# Provider registry
PROVIDERS = {
    "rule-based": RuleBasedProvider,
    "openai-gpt-3.5": lambda config: OpenAIProvider({**config, "model": "gpt-3.5-turbo"}),
    "openai-gpt-4o": lambda config: OpenAIProvider({**config, "model": "gpt-4o"}),
    "openai-gpt-4o-mini": lambda config: OpenAIProvider({**config, "model": "gpt-4o-mini"}),
    "ollama-llama3.2": lambda config: OllamaProvider({**config, "model": "llama3.2"}),
    "ollama-mistral": lambda config: OllamaProvider({**config, "model": "mistral"}),
}


def get_available_providers() -> List[Dict[str, any]]:
    """Get list of available NLP providers with metadata.

    Returns:
        List of provider info dictionaries
    """
    providers_info = []

    for provider_id in PROVIDERS.keys():
        # Create temporary instance to get metadata
        try:
            if "openai" in provider_id:
                provider = PROVIDERS[provider_id]({"api_key": "dummy"})
            else:
                provider = PROVIDERS[provider_id]({})

            providers_info.append({
                "id": provider_id,
                "name": provider.get_provider_name(),
                "cost": provider.get_cost_per_request(),
                "requires_api_key": provider.requires_api_key(),
                "type": "cloud" if provider.requires_api_key() else "local",
            })
        except Exception as e:
            log.warning("Error getting info for provider %s: %s", provider_id, e)
            continue

    return providers_info


def create_provider(provider_id: str, config: Optional[Dict] = None) -> Optional[NLPProvider]:
    """Create an NLP provider instance.

    Args:
        provider_id: Provider identifier (e.g., "rule-based", "openai-gpt-3.5")
        config: Provider-specific configuration (API keys, etc.)

    Returns:
        NLPProvider instance or None if provider not found
    """
    if provider_id not in PROVIDERS:
        log.error("Unknown provider: %s. Available: %s", provider_id, list(PROVIDERS.keys()))
        return None

    try:
        provider_class = PROVIDERS[provider_id]
        provider = provider_class(config or {})

        # Validate configuration
        is_valid, error = provider.validate_config()
        if not is_valid:
            log.error("Provider %s validation failed: %s", provider_id, error)
            return None

        log.info("Created NLP provider: %s", provider_id)
        return provider

    except Exception as e:
        log.error("Error creating provider %s: %s", provider_id, e)
        return None


def get_recommended_provider() -> str:
    """Get recommended provider ID based on what's available.

    Returns:
        Provider ID
    """
    # Try in order of preference:
    # 1. GPT-4o-mini (good balance of cost/quality)
    # 2. GPT-3.5 (cheap and good)
    # 3. Ollama (free local)
    # 4. Rule-based (always works)

    # For now, just return rule-based
    # In a real deployment, you'd check for API keys, etc.
    return "rule-based"
