from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import keyring
from helpers import get_user_decision, Configuration

config = Configuration()

print(f"Slack is set to: {config.get_slack_enabled()}")

class Slack:
    def __init__(self):
        self.init_slack_client()
        config.get_slack_enabled()

    def store_token(self):
        self.slack_token = input("Please enter your Slack API token: ")
        keyring.set_password("slack", "audiotimer_api_token", self.slack_token)
        return self.slack_token

    def store_channel_id(self):
        self.channel_id = input("Please enter channel ID to post messages to: ")
        keyring.set_password("slack", "audiotimer_channel_id", self.channel_id)  # Ensure consistent key names
        return self.channel_id

    def post_message(self, message, force=False):
        if config.get_slack_enabled() == True or force == True:
            try:
                response = self.client.chat_postMessage(channel=self.channel_id, text=message)
            except SlackApiError as e:
                print(f"Error posting message: {e.response['error']}\n")
                decision = get_user_decision("Do you want to edit the Slack credentials?")
                if decision:
                    self.slack_token = self.store_token()
                    self.channel_id = self.store_channel_id()
                    self.client = WebClient(token=self.slack_token)  # Reinitialize the client with the new token
                    self.post_message(self.client, self.channel_id, message)  # Try posting the message again
                else:
                    pass  # Option to disable Slack functionality can be added here

    def init_slack_client(self):
        self.slack_token = keyring.get_password("slack", "audiotimer_api_token")
        if self.slack_token is None:
            self.slack_token = self.store_token()

        self.channel_id = keyring.get_password("slack", "audiotimer_channel_id")
        if self.channel_id is None:
            self.channel_id = self.store_channel_id()

        self.client = WebClient(token=self.slack_token)

if __name__ == "__main__":
    slack = Slack()
    slack.post_message('Test', force=True)
