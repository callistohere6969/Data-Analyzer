"""OpenRouter LLM initialization and management"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm(model_name: str = None, temperature: float = 0.0, max_tokens: int = 500):
    """
    Initialize OpenRouter LLM via LangChain
    
    OpenRouter uses OpenAI-compatible API, so we use ChatOpenAI
    with custom base_url
    
    Args:
        model_name: Model identifier (e.g., "openai/gpt-4-turbo-preview")
        temperature: Temperature for response variability (0-1)
    
    Returns:
        ChatOpenAI LLM instance
    
    Raises:
        ValueError: If OPENROUTER_API_KEY not found in environment
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in .env file")
    
    model = model_name or os.getenv("DEFAULT_MODEL", "openai/gpt-4-turbo-preview")
    
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/your-username/multi-agent-analyzer",
            "X-Title": "Multi-Agent Data Analyzer"
        }
    )
    
    return llm


def test_llm() -> None:
    """Test LLM connection"""
    try:
        llm = get_llm()
        response = llm.invoke("Say 'LLM is working!' in 5 words")
        print(f"✓ LLM Connection Successful!\nResponse: {response.content}")
    except Exception as e:
        print(f"✗ LLM Connection Failed: {str(e)}")


if __name__ == "__main__":
    test_llm()
