import logging
from api_handlers import BaseLLMProvider

class PersonaManager:
    """
    Manages the AI's personality, crafts prompts, and interacts with the LLM.
    """
    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initializes the PersonaManager.

        Args:
            llm_provider: An instance of a class that inherits from BaseLLMProvider.
        """
        self.llm_provider = llm_provider
        # In the future, this will load system prompts, RAG DBs, etc.
        logging.info("PersonaManager initialized.")

    def craft_response(self, user: str, prompt: str) -> str:
        """
        Crafts a response by assembling a prompt and querying the LLM.

        For this initial wire-up, it's a very simple pass-through.
        """
        logging.info(f"PersonaManager: Crafting response for user '{user}'.")

        # This will become much more complex with memory and RAG.
        final_prompt = f"The user '{user}' said: '{prompt}'. Respond in a funny way."

        logging.info("PersonaManager: Sending final prompt to LLM provider.")
        response = self.llm_provider.get_response(final_prompt)

        logging.info("PersonaManager: Received response from LLM provider.")
        return response
