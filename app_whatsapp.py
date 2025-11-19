import uvicorn
import asyncio
import sqlite3
from fastapi import FastAPI, Form, HTTPException
from dotenv import load_dotenv
from src.channels.whatsapp import WhatsAppChannel
from src.agents.personal_assistant import PersonalAssistant
from src.utils import get_current_date_time

# Load .env variables from the environment file
load_dotenv()

# Initiate FastAPI app
app = FastAPI()

# Initialize sqlite3 DB for saving agent memory
conn = sqlite3.connect("db/checkpoints.sqlite", check_same_thread=False)

# Initiate personal assistant instance
personal_assistant = PersonalAssistant(db_connection=conn)

# Configuration for the Langgraph agent, specifying thread ID
config = {"configurable": {"thread_id": "1"}}


async def process_message_async(to_whatsapp_number, incoming_message):
    """
    Processes the incoming message asynchronously:
    1. Formats the message with the current date and time.
    2. Invokes the personal assistant to get a response.
    3. Sends the response to the provided WhatsApp number.
    """
    print(f"--- DEBUG: process_message_async started ---")
    # Format the message with current date/time
    message = (
        f"Message: {incoming_message}\n"
        f"Current Date/time: {get_current_date_time()}"
    )

    # Invoke the personal assistant to generate a response
    answer = personal_assistant.invoke(message, config=config)
    print(f"--- DEBUG: AI response received: {answer} ---")

    # Send the response via Twilio WhatsApp
    whatsapp = WhatsAppChannel()
    await asyncio.to_thread(
        whatsapp.send_message,
        to_number=to_whatsapp_number,
        body=answer
    )
    print(f"--- DEBUG: WhatsApp response sent ---")


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Webhook endpoint that handles incoming messages from WhatsApp.
    Receives the message and triggers an asynchronous task to process it.
    """
    incoming_message = Body
    from_number = From
    print(f"Message received from {from_number}: {incoming_message}")

    # For debugging, let's make the call synchronous to see any errors
    try:
        await process_message_async(from_number, incoming_message)
    except Exception as e:
        print(f"!!! AN ERROR OCCURRED IN process_message_async !!!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        # Optionally, you could return a 500 error to Twilio so they know it failed
        # raise HTTPException(status_code=500, detail=str(e))

    # Respond with a status indicating that the message was received
    return "Message received", 200


@app.post("/test")
async def test_endpoint(message: str = Form(...)):
    """
    Test endpoint to directly interact with the PersonalAssistant.
    """
    print(f"Test message received: {message}")

    # Format the message with current date/time
    formatted_message = (
        f"Message: {message}\n"
        f"Current Date/time: {get_current_date_time()}"
    )

    # Invoke the personal assistant to generate a response
    answer = personal_assistant.invoke(formatted_message, config=config)

    # Return the response
    return {"response": answer}


if __name__ == "__main__":
    # Start the FastAPI application on the specified host and port
    uvicorn.run(app, host="0.0.0.0", port=5000)