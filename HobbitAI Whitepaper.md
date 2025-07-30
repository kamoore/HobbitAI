# **Project Whitepaper: HobbitTrash AI VTuber**

Version: 1.2  
Date: July 29, 2025  
Author: Keith

## **1\. Executive Summary**

This document outlines the technical and functional specifications for the "HobbitTrash AI VTuber," a desktop application designed to create an interactive AI personality for a Twitch live stream.

The primary objective is to develop a highly customizable and engaging "AI co-host" that can interact with the streamer's community in real-time. The application will listen for specific triggers in Twitch chat (mentions, channel points, donations), process them through a sophisticated personality and memory engine, and generate a spoken response using a custom-cloned voice.

The system is designed with a modular Python architecture to facilitate maintainability and future expansion. The end-user experience for the streamer is prioritized, emphasizing ease of installation, a **modern, comprehensive graphical user interface (GUI)** for live control, and seamless integration with standard streaming software (OBS). This document also specifies a **Testing & Development Mode** to ensure the application framework can be built and tested without external dependencies.

## **2\. System Architecture**

The application will be a single, monolithic desktop application composed of several distinct, interconnected modules. This architecture ensures that concerns are separated, making development, debugging, and future feature additions more manageable.

### **2.1. High-Level Architecture Diagram**

graph TD  
    subgraph External Services  
        Twitch\_Platform\[Twitch API \<br/\>(IRC & PubSub)\]  
        LLM\_APIs\[LLM APIs \<br/\>(OpenAI, Gemini, Groq)\]  
        ElevenLabs\_API\[ElevenLabs API\]  
    end

    subgraph HobbitAI Application (Python)  
        A\[Event Router\] \--\> B{Interaction Manager}  
        B \--\> C{Personality Manager}  
        C \--\> D\[LLM & TTS Handlers\]  
        B \--\> E{Command Executor}  
        F\[GUI (CustomTkinter)\] \<--\> B  
        F \<--\> E  
        F \<--\> H  
        G\[Animation Server (Flask)\]  
    end  
      
    subgraph Data Stores  
        H\[config.ini\]  
        I\[RAG Vector DB \<br/\>(FAISS)\]  
        J\[Knowledge Base \<br/\>(.txt files)\]  
    end

    Twitch\_Platform \--\> A  
    D \--\> LLM\_APIs  
    D \--\> ElevenLabs\_API  
    C \--\> I  
    I \<--\> J  
    A \--\> E  
    subgraph OBS  
        OBS\_Source\[OBS Browser Source\]  
    end

    G \--\> OBS\_Source

### **2.2. Core Modules**

* **Main Application (hobbit\_ai.py):** The entry point. Initializes the GUI and starts all other modules in separate threads.  
* **GUI (gui.py):** A **modern, multi-tabbed interface built with customtkinter**. It provides comprehensive live control over the application's status, settings, and memory.  
* **Event Router (twitch\_handler.py):** Connects to Twitch services and routes incoming events.  
* **Interaction Manager (interaction\_manager.py):** Enforces cooldowns and manages conversational memory.  
* **Personality Manager (persona\_manager.py):** Crafts the final prompt sent to the LLM using the RAG database.  
* **Command Executor (command\_executor.py):** Processes privileged commands from moderators.  
* **API Handlers (api\_handlers.py):** Contains modular classes for interacting with external LLM and TTS APIs, **including mock versions for testing.**  
* **Animation Server (animation\_server.py):** A Flask app that serves the visual component for OBS.

## **3\. Functional Specifications**

### **3.1. Twitch Integration & Event Handling**

* The **Event Router** must connect to Twitch using the twitchio library.  
* It must listen to IRC for chat messages and subscribe to the correct PubSub topics for Channel Point redemptions and Cheers/donations for the channel specified in config.ini.  
* **Triggers:** The application will act upon the following events, if enabled in the GUI/config:  
  * **Mentions:** Any chat message containing @hobbittrash.  
  * **Channel Points:** A specific redeem name, defined in config.ini.  
  * **Donations/Cheers:** Any event exceeding a minimum amount defined in config.ini.  
* The router must parse all triggered events to extract username and prompt.

### **3.2. AI Personality & Memory System**

* **System Prompt:** The **Personality Manager** will load a core personality from a system\_prompt.txt file. This prompt defines the AI's base character, speaking style, and safety guardrails.  
* **RAG Database:**  
  * On startup, the application will index all .txt files from the knowledge\_base/ directory into a FAISS vector database.  
  * This includes general lore, inside jokes, and moderator-defined concepts to avoid.  
* **Memory Layers:** The **Interaction Manager** must implement a three-layer memory system:  
  1. **Long-Term (Chatter Profiles):** For a given user, retrieve relevant facts from their dedicated file in knowledge\_base/chatter\_profiles/.  
  2. **Mid-Term (Crosstalk):** Maintain a rolling log of the last 30-50 chat messages. When triggered, generate a concise summary of the current conversation to provide context.  
  3. **Short-Term (Direct History):** Maintain a deque for each user, storing the last 3-5 direct interactions (prompt and response).  
* **Prompt Assembly:** The **Personality Manager** must assemble a final prompt for the LLM containing the system prompt, retrieved RAG context, crosstalk summary, and direct conversation history.

### **3.3. Live Control & Moderation**

* **GUI (Graphical User Interface):**  
  * The GUI will be built using the customtkinter library to achieve a modern, clean, dark-themed aesthetic.  
  * The interface will be tab-based to organize functionality cleanly.  
  * **Dashboard Tab:**  
    * A main "Start/Stop AI" button.  
    * A prominent status indicator (e.g., "Offline," "Listening," "Thinking," "Speaking").  
    * A live log view showing recent triggers and AI responses.  
    * A frame with toggles for the primary response triggers (Mentions, Channel Points, Donations).  
  * **Settings Tab:**  
    * This tab will provide a user-friendly interface to edit all parameters from config.ini.  
    * Fields will be organized into sections: Twitch, LLM Provider, ElevenLabs, Interaction Rules.  
    * **Sensitive fields** (API Keys, OAuth Token) **must be implemented as password fields** (e.g., show="\*"\_).  
    * A "Save Settings" button will write any changes back to the config.ini file.  
  * **Memory Manager Tab:**  
    * An interface for managing the AI's long-term memory.  
    * A searchable dropdown/list to select a chatter's username.  
    * A text area displaying the existing memos for the selected user from their .txt file.  
    * An input field and "Add Memo" button to append new information to the selected user's profile.  
* **Moderator Commands:**  
  * The **Command Executor** will process any chat message starting with \!aicmd from an authorized user (defined in config.ini).  
  * It must support the commands as specified in the README.md, performing the necessary file I/O and updating the in-memory state.  
  * After executing a command, it must send a confirmation message back to the Twitch chat.

### **3.4. OBS Integration**

* The **Animation Server** will be a lightweight Flask application.  
* It will serve a single HTML page at http://127.0.0.1:8080.  
* This page will display a simple character animation (e.g., two images for "mouth open" and "mouth closed") controlled via JavaScript.  
* The state of the animation (speaking vs. idle) will be updated by the main application when the TTS audio starts and stops playing.

## **4\. Technical Specifications**

### **4.1. Technology Stack**

* **Backend:** Python 3.8+  
* **GUI:** customtkinter (for modern themed widgets)  
* **Web Server:** Flask  
* **Twitch API:** twitchio  
* **AI APIs:** openai, google-generativeai, groq  
* **TTS API:** elevenlabs  
* **Vector DB:** faiss-cpu  
* **Text Processing:** sentence-transformers (for RAG embeddings)

### **4.2. Project File Structure**

/hobbittrash-ai-vtuber  
|-- hobbit\_ai.py             \# Main application entry point  
|-- gui.py  
|-- twitch\_handler.py  
|-- interaction\_manager.py  
|-- persona\_manager.py  
|-- command\_executor.py  
|-- api\_handlers.py  
|-- animation\_server.py  
|  
|-- config.ini               \# User configuration  
|-- requirements.txt         \# Project dependencies  
|  
|-- /assets  
|   |-- mouth\_open.png  
|   |-- mouth\_closed.png  
|   |-- body.png  
|  
|-- /knowledge\_base  
|   |-- inside\_jokes.txt  
|   |-- concepts\_to\_avoid.txt  
|   |-- /chatter\_profiles  
|       |-- some\_user.txt  
|  
|-- /templates  
    |-- index.html           \# HTML for the animation server

### **4.3. Testing & Development Mode**

To facilitate development and testing in an environment without access to all assets or external APIs (e.g., a VM), the application must support a test\_mode.

* **Configuration:** A flag in config.ini will control this mode.  
  \[System\]  
  test\_mode \= true

* **Mock API Handlers:**  
  * The api\_handlers.py module must include mock classes (MockLLMProvider, MockTTSProvider) that are used when test\_mode is true.  
  * MockLLMProvider will not call an external API. It will return a hardcoded string response (e.g., "This is a mock response.") and should print the received prompt to the console for debugging.  
  * MockTTSProvider will not call an external API. It will simulate the duration of an audio clip (e.g., time.sleep(3)) and return a completion status. It should print the text it would have synthesized.  
* **Asset & Data Fallbacks:** The application must handle missing files gracefully when in test\_mode.  
  * **Animation Server:** If image assets in /assets are not found, it must fall back to drawing simple colored rectangles (e.g., using Pygame) to represent the "idle" and "speaking" states.  
  * **RAG Knowledge Base:** If the /knowledge\_base directory or its subdirectories are empty, the RAG indexing process must be skipped, and any function attempting to retrieve context from it should return an empty string.  
  * **System Prompt:** If system\_prompt.txt is missing, a default, hardcoded string (e.g., "You are a test AI.") must be used.

## **5\. Implementation Plan (Suggested Order)**

1. **Module Scaffolding:** Create all the Python files with basic class structures.  
2. **Configuration & Test Mode:** Implement logic to read config.ini, including the test\_mode flag. Build the mock API handlers.  
3. **API Handlers:** Build the real classes for interacting with the LLM and ElevenLabs APIs.  
4. **Core Twitch Connection:** Implement the basic twitchio listener in twitch\_handler.py to connect and read chat.  
5. **Basic Response Flow:** Wire up the simplest path using the mock providers: Event Router \-\> Interaction Manager \-\> Personality Manager \-\> API Handlers.  
6. **GUI (Phase 1 \- Dashboard):** Develop the main dashboard tab of the customtkinter interface with start/stop functionality and status indicators.  
7. **Animation Server:** Build the Flask server and the simple mouth-flap animation, including the asset fallback logic for test mode.  
8. **GUI (Phase 2 \- Settings & Memory):** Implement the Settings and Memory Manager tabs, connecting them to the configuration file and RAG system.  
9. **Advanced Memory:** Implement the RAG database and the three layers of memory in the Interaction Manager, including the fallback logic for test mode.  
10. **Moderator Commands:** Build out the Command Executor and link it to the Event Router.  
11. **Packaging:** Create instructions or a script to package the application for easier distribution.