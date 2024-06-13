from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOllama(model="Llama-3-8B-Instruct:latest")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI Assistant. You must answer in Korean.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | llm | StrOutputParser()
