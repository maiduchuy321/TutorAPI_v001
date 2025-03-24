from openai import OpenAI
from app.config import settings
from langfuse.openai import OpenAI
from langfuse.decorators import observe
import os
from prompt.theory_prompt import AITutorPrompt
from app.controllers.conversation_controller import ConversationController
from app.controllers.lesson_controller import LessonController
from app.models.models import Message
from app.schemas.message import MessageCreate
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.utils.prompt_manager import PromptManager

os.environ["LANGFUSE_SECRET_KEY"]=settings.LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_PUBLIC_KEY"]=settings.LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST


@observe()
class questionsAndAnswers:
    def __init__(self, db: Session):
        self.db = db,
        self.prompt = AITutorPrompt()
        self.model = settings.OPENAI_MODEL,
        self.max_tokens = settings.MAX_TOKEN,
        self.api_key = settings.OPENAI_API_KEY,
        self.url = settings.OPENAI_API_URL


    def generate_response(prompt: str,
                      model: str = settings.OPENAI_MODEL,
                      max_tokens: int = settings.MAX_TOKEN,
                      api_key: str = settings.OPENAI_API_KEY,
                      url: str = settings.OPENAI_API_URL):


        client = OpenAI(
            base_url=url,
            api_key=api_key
        )

        stream = client.completions.create(
            model=model,
            prompt=prompt,
            stream=True,
            max_tokens=max_tokens
        )
        return stream

