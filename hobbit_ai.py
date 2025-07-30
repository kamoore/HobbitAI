import logging
import queue
import threading
import time

import configparser
from gui import AppGUI, QueueHandler
from api_handlers import get_api_providers
from persona_manager import PersonaManager
from interaction_manager import InteractionManager
from twitch_handler import TwitchHandler
from animation_server import AnimationServer

class ConfigManager:
    """
    Handles loading and accessing configuration from config.ini.
    """
    def __init__(self, filepath='config.ini'):
        self.config = configparser.ConfigParser()
        if not self.config.read(filepath):
            logging.error(f"Configuration file not found at {filepath}")
            raise FileNotFoundError(f"Configuration file not found at {filepath}")
        logging.info(f"Configuration loaded from {filepath}")

    def get_system_config(self):
        return {'test_mode': self.config.getboolean('System', 'test_mode', fallback=True)}
    def get_twitch_config(self):
        return {
            'bot_username': self.config.get('Twitch', 'bot_username'),
            'channel': self.config.get('Twitch', 'channel'),
            'oauth_token': self.config.get('Twitch', 'oauth_token'),
            'moderators': [mod.strip() for mod in self.config.get('Twitch', 'moderators').split(',')]
        }
    def get_llm_config(self):
        return {
            'provider': self.config.get('LLM', 'provider', fallback='mock'),
            'model': self.config.get('LLM', 'model'),
            'api_key': self.config.get('LLM', 'api_key')
        }
    def get_elevenlabs_config(self):
        return {
            'api_key': self.config.get('ElevenLabs', 'api_key'),
            'voice_id': self.config.get('ElevenLabs', 'voice_id')
        }
    def get_interaction_config(self):
        return {
            'global_cooldown': self.config.getint('Interaction', 'global_cooldown', fallback=10),
            'user_cooldown': self.config.getint('Interaction', 'user_cooldown', fallback=30),
            'crosstalk_context_depth': self.config.getint('Interaction', 'crosstalk_context_depth', fallback=50),
            'direct_history_depth': self.config.getint('Interaction', 'direct_history_depth', fallback=3)
        }
    def get_triggers_config(self):
        return {
            'respond_to_mentions': self.config.getboolean('Triggers', 'respond_to_mentions', fallback=True),
            'respond_to_channel_points': self.config.getboolean('Triggers', 'respond_to_channel_points', fallback=True),
            'respond_to_donations': self.config.getboolean('Triggers', 'respond_to_donations', fallback=True),
            'channel_point_name': self.config.get('Triggers', 'channel_point_name'),
            'min_cheer_amount': self.config.getint('Triggers', 'min_cheer_amount', fallback=100),
            'min_donation_amount': self.config.getfloat('Triggers', 'min_donation_amount', fallback=1.00)
        }

class AIBot(threading.Thread):
    """Encapsulates the AI bot's logic in a separate thread."""
    def __init__(self, config_manager, gui):
        super().__init__()
        self.daemon = True
        self.config_manager = config_manager
        self.gui = gui
        self._stop_event = threading.Event()

    def run(self):
        """The main loop for the bot thread."""
        self.gui.update_status("INITIALIZING", "orange")
        try:
            # --- Initialize API Handlers ---
            llm_provider, tts_provider = get_api_providers(self.config_manager)

            # --- Initialize Core Modules ---
            persona_manager = PersonaManager(llm_provider)
            interaction_manager = InteractionManager(persona_manager, tts_provider)
            self.twitch_handler = TwitchHandler(self.config_manager, interaction_manager)

            system_config = self.config_manager.get_system_config()
            self.gui.update_status("READY", "orange")

            if system_config['test_mode']:
                self.gui.update_status("LISTENING (Test Mode)", "yellow")
                # In test mode, we just simulate events periodically
                while not self._stop_event.is_set():
                    logging.info("Test mode: Simulating a trigger.")
                    self.twitch_handler.simulate_trigger(user="TestUser", prompt="This is a test prompt.")
                    self._stop_event.wait(30) # Wait for 30s or until stop is called
            else:
                # This is where the actual bot would run
                self.gui.update_status("LISTENING", "green")
                self.twitch_handler.run_bot() # This will block until the bot is stopped

        except Exception as e:
            logging.error(f"An error occurred in the AI Bot thread: {e}", exc_info=True)
            self.gui.update_status("ERROR", "red")

        logging.info("AI Bot thread has stopped.")
        self.gui.update_status("OFFLINE", "red")

    def stop(self):
        """Signals the bot thread to stop."""
        logging.info("Stopping AI Bot thread...")
        self._stop_event.set()
        # If the real bot is running, we might need a more direct way to stop it
        # For example, twitchio's `close()` method.
        # if hasattr(self, 'twitch_handler'):
        #     self.twitch_handler.close()


import argparse

def main():
    """Main function to initialize and run the HobbitTrash AI application."""
    parser = argparse.ArgumentParser(description="HobbitTrash AI VTuber Control")
    parser.add_argument("--no-gui", action="store_true", help="Run the bot in headless mode without the GUI.")
    args = parser.parse_args()

    # ---- Setup Logging ----
    log_queue = queue.Queue()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')

    logging.info("Starting HobbitTrash AI VTuber...")

    try:
        config_manager = ConfigManager()
        animation_server = AnimationServer()
        animation_server.start_in_thread()
        time.sleep(1)

        if args.no_gui:
            logging.info("Running in headless mode (--no-gui).")
            # In headless mode, we need a dummy GUI object for the bot
            class DummyGUI:
                def update_status(self, text, color):
                    logging.info(f"Headless Status Update: {text} ({color})")

            bot = AIBot(config_manager, DummyGUI())
            bot.start()
            # Keep the main thread alive
            while bot.is_alive():
                bot.join(1)
        else:
            # --- GUI Mode ---
            queue_handler = QueueHandler(log_queue)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            queue_handler.setFormatter(formatter)
            logging.getLogger().addHandler(queue_handler)

            app = AppGUI(log_queue)

            bot_thread = None
            def start_ai():
                nonlocal bot_thread
                if bot_thread is None or not bot_thread.is_alive():
                    logging.info("Starting AI bot thread...")
                    bot_thread = AIBot(config_manager, app)
                    bot_thread.start()
                else:
                    logging.warning("AI bot thread is already running.")

            def stop_ai():
                nonlocal bot_thread
                if bot_thread and bot_thread.is_alive():
                    logging.info("Requesting AI bot to stop...")
                    bot_thread.stop()
                    bot_thread = None
                else:
                    logging.warning("AI bot thread is not running.")

            app.set_callbacks(start_ai, stop_ai)
            app.mainloop()

    except (FileNotFoundError, Exception) as e:
        # Catching the TclError from tkinter if display is not found
        if "no display name" in str(e):
             logging.error("Failed to start GUI: No display environment available.")
             logging.info("You can run the bot in headless mode with the --no-gui flag.")
        else:
            logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
