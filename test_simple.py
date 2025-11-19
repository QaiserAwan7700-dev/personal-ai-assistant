import sqlite3
from src.utils import get_current_date_time
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# Initialize sqlite3 DB for saving agent memory
conn = sqlite3.connect("db/checkpoints.sqlite", check_same_thread=False)

# Initialize a simple OpenAI model without tools
model = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key="YOUR_OPENAI_API_KEY")

# Test message
message = "Hello, how are you today?"

# Format the message with current date/time
formatted_message = (
    f"Message: {message}\n"
    f"Current Date/time: {get_current_date_time()}"
)

# Create a simple message and get a response
response = model.invoke([HumanMessage(content=formatted_message)])

print(f"Question: {message}")
print(f"Answer: {response.content}")