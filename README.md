# FRIDAY AI Assistant 🤖
 
An Iron Man–inspired AI personal assistant powered by **LiveKit Agents** and **Google Realtime LLM**.

## ✨ Features
- 🎤 Real-time voice and video with LiveKit
- 🌦️ Weather updates
- 🔎 Web search (DuckDuckGo)
- 📧 Gmail integration for sending emails
- 🔊 Noise cancellation for clarity
- 🧑‍💻 FRIDAY persona (witty + futuristic)

## 📂 Project Structure
- `agent.py` → Main entry point
- `prompts.py` → Persona & session instructions
- `tools.py` → Custom tools (weather, search, email)
- `requirements.txt` → Dependencies
- `.env` → Secrets (NOT uploaded) (create when processing)
- `FRIDAY_Project_Documentation.pdf` → Full project documentation 

## Install dependencies:
pip install -r requirements.txt

## Add your .env file:
LIVEKIT_URL=...
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
GOOGLE_API_KEY=...
GMAIL_USER=...
GMAIL_APP_PASSWORD=...


## Run the assistant:
python agent.py
































































## Credits
This project is based on the tutorial by Thanh-y David Nguyen ( https://youtu.be/An4NwL8QSQ4 ).
