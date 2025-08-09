from langchain_ollama import ChatOllama

OLLAMA_MODEL = "llama3.1:8b"
LLM_TEMPERATURE = 0.4

llm = ChatOllama(model=OLLAMA_MODEL, temperature=LLM_TEMPERATURE)

def invoke_llm(prompt: str) -> str:
    return llm.invoke(prompt)