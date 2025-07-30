import logging
from twitchio.ext import commands
from interaction_manager import InteractionManager

class TwitchHandler(commands.Bot):
    """
    Handles the connection to Twitch and routes events to the InteractionManager.
    """
    def __init__(self, config_manager, interaction_manager: InteractionManager):
        """
        Initializes the TwitchHandler bot.

        Args:
            config_manager: The application's configuration manager.
            interaction_manager: An instance of InteractionManager.
        """
        self.interaction_manager = interaction_manager
        self.config = config_manager.get_twitch_config()
        self.channel_name = self.config['channel']

        # In test mode, we don't want to connect to Twitch.
        # The super().__init__() is what establishes the connection.
        # We will call it later when we are not in test mode.
        logging.info("TwitchHandler initialized.")

    async def event_ready(self):
        """Called once the bot goes online."""
        logging.info(f"Twitch bot has connected as {self.nick}.")
        logging.info(f"Joining channel: {self.channel_name}")
        await self.join_channels([self.channel_name])
        logging.info(f"Successfully joined {self.channel_name}.")

    async def event_message(self, message):
        """Runs every time a message is sent in chat."""
        # Make sure the bot ignores itself
        if message.echo:
            return

        logging.info(f"Received message from {message.author.name}: {message.content}")

        # Here we would check for triggers (mentions, etc.)
        # For now, we'll just pass it to the interaction manager if it's a command.
        if message.content.startswith('!hello'):
             self.interaction_manager.handle_interaction(message.author.name, message.content)

        # This is required to handle commands
        await self.handle_commands(message)

    # --- Test Method ---
    def simulate_trigger(self, user: str, prompt: str):
        """
        A method for testing the full interaction flow without a live Twitch connection.
        """
        logging.info(f"--- SIMULATING TWITCH TRIGGER ---")
        logging.info(f"Simulated user: {user}")
        logging.info(f"Simulated prompt: {prompt}")
        self.interaction_manager.handle_interaction(user, prompt)
        logging.info(f"--- SIMULATION COMPLETE ---")

    def run_bot(self):
        """Starts the Twitch bot."""
        token = self.config.get('oauth_token')
        if not token:
            logging.error("Twitch OAuth token is missing from config.ini. Cannot start bot.")
            return

        super().__init__(token=token, prefix='!', initial_channels=[self.channel_name])
        logging.info("Starting Twitch bot...")
        self.run()
