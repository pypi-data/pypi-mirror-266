from typing import Union, List, Dict, Optional
from openai import OpenAI
import httpx


def build_client(base_url: str, api_key: str, proxy: str):
    """
    base_url:
    api_key:
    proxy:
    """
    if proxy:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.Client(
                base_url=proxy,
                follow_redirects=True,
            ),
        )
    else:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    return client


def predict(client: OpenAI,
            model: str,
            query: str,
            history: Optional[List[Dict[str, str]]] = None, 
            max_tokens: int = 16384,
            temperature: float = 0.95,
            top_p: float = 1.0):
    """"""
    history = history or []

    if query:
        history.append({"role": "user", "content": query})

    history_str = "\n"
    for message in history:
        history_str += f"{message['role']}: {message['content']}\n"

    chat_completion = client.chat.completions.create(
            messages=history,
            model=model,
            max_tokens=max_tokens,
            stream=False,
            temperature=temperature,
            top_p=top_p,
            stop=["<|im_end|>"],
    )

    response = chat_completion.choices[0].message.content.replace('<|im_end|>', '')
    return response


def stream_predict(
        client: OpenAI,
        model: str,
        query: str,
        history: Optional[List[Dict[str, str]]] = None, 
        max_tokens: int = 16384,
        temperature: float = 0.95,
        top_p: float = 1.0):
    history = history or []

    history.append({"role": "user", "content": query})

    history_str = "\n"
    for message in history:
        history_str += f"{message['role']}: {message['content']}\n"

    chat_completion = client.chat.completions.create(
            messages=history,
            model=model,
            max_tokens=max_tokens,
            stream=True,
            temperature=temperature,
            top_p=top_p,
            stop=["<|im_end|>"],
    ) # type: ignore

    for chunk in chat_completion:
        yield chunk


if __name__ == "__main__":
    import httpx
    client = OpenAI(
                api_key='sk-9QT7CG36EPZc0snHF7FfEcCf113c4d678e48C8D97fCa8cFf',
                base_url='https://api.xty.app/v1',
                http_client=httpx.Client(
                    base_url='https://api.xty.app/v1',
                    follow_redirects=True,
                ),
            )
    print(client)
    for s in stream_predict(client, "gpt-3.5-turbo-1106", "What is the meaning of life?"):
        print(s)