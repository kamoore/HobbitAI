import logging
import httpx
from persona_manager import PersonaManager
from api_handlers import BaseTTSProvider

def set_animation_state(state: str):
    """
    Sends a request to the animation server to change the animation state.
    """
    try:
        # The animation server runs on localhost, so this is an internal call.
        url = "http://127.0.0.1:8080/set_state"
        payload = {"state": state}
        # Use a short timeout as this is a local call
        response = httpx.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        logging.info(f"Successfully set animation state to '{state}'.")
    except httpx.RequestError as e:
        # This can happen if the animation server isn't running.
        # It's not a critical failure, so we just log it.
        logging.warning(f"Could not set animation state to '{state}'. Is the server running? Error: {e}")

class InteractionManager:
    """
    Manages the overall flow of a single user interaction, including cooldowns and memory.
    """
    def __init__(self, persona_manager: PersonaManager, tts_provider: BaseTTSProvider):
        """
        Initializes the InteractionManager.

        Args:
            persona_manager: An instance of PersonaManager.
            tts_provider: An instance of a class that inherits from BaseTTSProvider.
        """
        self.persona_manager = persona_manager
        self.tts_provider = tts_provider
        # Cooldown and memory management will be added later.
        logging.info("InteractionManager initialized.")

    def handle_interaction(self, user: str, prompt: str):
        """
        Handles a single interaction event from start to finish.
        """
        logging.info(f"InteractionManager: Handling interaction for user '{user}'.")

        # 1. Get a response from the persona manager
        response_text = self.persona_manager.craft_response(user, prompt)
        logging.info(f"InteractionManager: Received response text: '{response_text}'")

        # 2. Set animation to "speaking" and send the response to the TTS provider
        set_animation_state('speaking')
        try:
            success = self.tts_provider.synthesize_speech(response_text)
            if success:
                logging.info("InteractionManager: TTS synthesis completed successfully.")
            else:
                logging.error("InteractionManager: TTS synthesis failed.")
        finally:
            # 3. Always set animation back to "idle" when done
            set_animation_state('idle')
