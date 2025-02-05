import os
from datetime import datetime

# Twilio configuration (These lines remain, but are unused in the modified code)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")


def subscribe_to_updates(phone_number, game_id, frequency):
    """
    Mock subscription function that logs the subscription details
    """
    try:
        subscription_info = {
            'phone': phone_number,
            'game_id': game_id,
            'frequency': frequency,
            'subscribed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        print(f"New subscription: {subscription_info}")
        return True

    except Exception as e:
        print(f"Error in subscription: {str(e)}")
        return False