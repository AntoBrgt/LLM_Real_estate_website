from langchain_ollama import ChatOllama

OLLAMA_MODEL = "llama3.1:8b"
LLM_TEMPERATURE = 0.4

llm = ChatOllama(model=OLLAMA_MODEL, temperature=LLM_TEMPERATURE)

def invoke_llm(prompt: str) -> str:
    """
    Invoke the LLM

    Args:
        prompt (str): Prompt

    Returns:
        str: The LLM's answer
    """
    return llm.invoke(prompt)