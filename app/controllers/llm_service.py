from openai import OpenAI
from app.config import settings
from app.models.chat_model import ChatHistory


def generate_response(prompt: str,
                      model: str = settings.OPENAI_MODEL,
                      max_tokens: int = settings.MAX_TOKEN,
                      api_key: str = settings.OPENAI_API_KEY,
                      url: str = settings.OPENAI_API_URL):
    """
    Gọi API OpenAI để tạo phản hồi.

    Args:
        prompt: Prompt gửi đến LLM.
        model: Model LLM sử dụng.
        max_tokens: Số lượng token tối đa.
        api_key: API key.
        url: URL của API.

    Returns:
        Stream phản hồi từ LLM.
    """
    client = OpenAI(
        base_url=url,
        api_key=api_key
    )
    stream = client.completions.create(
        model=model,
        prompt=prompt,
        stream=False,
        max_tokens=max_tokens
    )
    return stream


def process_stream(stream) -> str:
    """
    Xử lý stream từ API và trả về kết quả hoàn chỉnh.

    Args:
        stream: Stream từ API OpenAI.

    Returns:
        Văn bản hoàn chỉnh từ stream.
    """
    response_text = ""
    # print(stream)
    response_text = stream.choices[0].text if stream.choices else ""
    # print(response_text)
    return response_text