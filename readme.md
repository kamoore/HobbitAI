# **HobbitTrash AI VTuber**

An interactive, AI-powered VTuber that connects to a Twitch stream, listens for triggers, and responds in a custom-cloned voice. This project is designed to be a highly customizable and engaging "AI co-host" for live streamers.

## **🌟 Features**

* **Real-time Twitch Integration:** Connects to any Twitch channel and listens for mentions, channel point redeems, and donations.  
* **Multi-Provider LLM Support:** Easily switch between **OpenAI**, **Google Gemini**, and **Groq** for response generation.  
* **High-Quality Voice Cloning:** Integrates with **ElevenLabs** to convert text responses into a realistic, custom-cloned voice.  
* **Advanced Memory System:**  
  * **Long-Term Memory:** Remembers facts and details about individual chatters.  
  * **Mid-Term Memory:** Analyzes recent chat "crosstalk" to understand conversational context.  
  * **Short-Term Memory:** Tracks direct back-and-forth conversations with users.  
* **Live Control & Moderation:**  
  * A simple desktop GUI for the streamer to control the AI's triggers and status.  
  * Privileged chat commands for the streamer and moderators to manage the AI live.  
* **Simple OBS Integration:** The animated VTuber is served as a local webpage, allowing for easy, transparent overlay via a Browser Source in OBS.

## **⚙️ Architecture Overview**

The application is built on a modular Python architecture:

1. **Event Router:** Listens to Twitch IRC (chat) and PubSub (channel points, etc.) to catch triggers.  
2. **Interaction Manager:** Enforces user/global cooldowns and manages the three layers of memory.  
3. **Personality Manager:** Uses a detailed system prompt and a Retrieval-Augmented Generation (RAG) database to craft the AI's personality and responses.  
4. **LLM & TTS Handlers:** Modular interfaces to communicate with the AI and voice synthesis APIs.  
5. **Animation Server:** A lightweight Flask server that provides the animated character for OBS.

## **🚀 Getting Started**

### **Prerequisites**

* Python 3.8+  
* An OBS instance for streaming.

### **1\. Clone the Repository**

git clone https://github.com/your-username/hobbittrash-ai-vtuber.git  
cd hobbittrash-ai-vtuber

### **2\. Install Dependencies**

Install all the required Python libraries using pip:

pip install \-r requirements.txt

### **3\. Configure the Application**

All settings are managed in the config.ini file. Make a copy of config.example.ini and name it config.ini. Then, fill out the required fields:

* **\[Twitch\]**: Your bot's username, the channel to join, your OAuth token, and a list of moderators.  
* **\[LLM\]**: Your chosen provider (openai, gemini, or groq), the specific model, and your API key.  
* **\[ElevenLabs\]**: Your ElevenLabs API key and the ID of your cloned voice.  
* **\[Interaction\]**: Set cooldowns and context depth.  
* **\[Triggers\]**: Enable/disable triggers and set values for channel points and donations.

## **▶️ Usage**

1. **Run the Application:**  
   python hobbit\_ai.py

2. **Use the GUI:** The desktop application window will open. Use the "Start AI" button to connect to Twitch.  
3. **Add to OBS:**  
   * Add a new "Browser" source in OBS.  
   * Set the URL to http://127.0.0.1:8080 (or the port specified in your config).  
   * The animated VTuber will now be visible as a transparent overlay.  
   * Ensure your desktop audio is captured in OBS to hear the AI's voice.

## **🛡️ Moderator Commands**

Moderators and the streamer (as defined in config.ini) can use the following commands in Twitch chat:

| Command | Description | Example |
| :---- | :---- | :---- |
| \!aicmd add\_banned\_word \<word\> | Adds a word to the AI's blocklist. | \!aicmd add\_banned\_word politics |
| \!aicmd add\_avoid\_concept \<desc\> | Adds a topic for the AI to avoid. | \!aicmd add\_avoid\_concept drama between streamers |
| \!aicmd add\_memo \<user\> \<memo\> | Adds a fact to a user's long-term memory file. | \!aicmd add\_memo SomeUser loves Elden Ring |
| \!aicmd set\_cooldown \<user|global\> \<sec\> | Adjusts a cooldown timer (in seconds). | \!aicmd set\_cooldown global 15 |
| \!aicmd toggle\_trigger \<mentions|points|donos\> | Toggles a response trigger on or off. | \!aicmd toggle\_trigger mentions |

## **🛠️ Technology Stack**

* **Backend:** Python  
* **GUI:** Tkinter  
* **Twitch Integration:** twitchio  
* **Animation Server:** Flask, Pygame  
* **AI Services:** OpenAI, Google Gemini, Groq  
* **Text-to-Speech:** ElevenLabs  
* **Vector Database (RAG):** FAISS