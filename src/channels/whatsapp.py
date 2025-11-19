import os
from twilio.rest import Client


class WhatsAppChannel:
    def __init__(self):
        """
        Initializes the WhatsAppChannel with Twilio client.
        """
        self.client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    def send_message(self, to_number, body):
        """
        Sends a WhatsApp message via the Twilio API.
        """
        # --- DEBUG: Print the numbers to verify format ---
        from_number = os.getenv('FROM_WHATSAPP_NUMBER')
        print(f"--- DEBUG: Sending WhatsApp ---")
        print(f"From: {from_number}")
        print(f"To (raw): {to_number}")

        # Ensure the 'to' number is prefixed with 'whatsapp:'
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'

        print(f"To (formatted): {to_number}")
        print(f"Body: {body}")
        # --- END DEBUG ---

        try:
            message = self.client.messages.create(
                body=body,
                from_=from_number,
                to=to_number
            )
            print(f"--- DEBUG: Message sent successfully with SID: {message.sid} ---")
            return f"Message sent successfully with SID: {message.sid}"
        except Exception as e:
            print(f"!!! ERROR: Failed to send message: {e} !!!")
            # It's good practice to re-raise the exception so the calling code knows it failed
            raise e

    def receive_messages(self):
        """
        Receiving messages is handled via webhooks.
        """
        pass