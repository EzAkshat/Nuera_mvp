from dotenv import load_dotenv
import os
from sst import SST
from llm import get_llm_response
from file_search import FileSearch
from open_app import get_start_menu_apps, launch_application
from tts import text_to_speech
import json
import threading
from datetime import datetime, timedelta
from plyer import notification

def trigger_reminder(message, api_key):
    notification.notify(
        title="Nuera Reminder",
        message=message,
        app_name="Nuera"
    )
    text_to_speech(f"Reminder: {message}", api_key)

def main():
    load_dotenv()
    PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

    if not PORCUPINE_ACCESS_KEY or not GEMINI_API_KEY or not ELEVENLABS_API_KEY:
        raise ValueError("Missing API keys in .env file")

    with open("config.json", "r") as f:
        config = json.load(f)
    system_prompt = config["system_prompt"]

    keyword_path = "NUERA-wake-up_en_windows_v3_0_0.ppn"
    sst = SST(PORCUPINE_ACCESS_KEY, keyword_path)
    file_search = FileSearch()
    apps = get_start_menu_apps()

    try:
        while True:
            if sst.listen_for_wake_word():
                print("START_LISTENING")
                command = sst.listen_for_command()
                if command is not None:
                    if command.lower() == "exit":
                        text_to_speech("Catch ya later, fam!", ELEVENLABS_API_KEY)
                        print("STOP_LISTENING")
                        return
                    llm_response = get_llm_response(command, GEMINI_API_KEY, system_prompt)
                    action_type = llm_response.get("type")
                    response_text = llm_response.get("response", "Uh, what now?")

                    if action_type == "open_app":
                        app_name = llm_response.get("app_name")
                        action = llm_response.get("action")
                        parameter = llm_response.get("parameter")
                        result = launch_application(app_name, action, parameter, apps)
                        response_text = result if result else response_text
                    elif action_type == "search_file":
                        query = llm_response.get("query") or llm_response.get("parameter")
                        if query:
                            results = file_search.search(query)
                            if results:
                                response_text = f"Found '{query}' at: {results[0]}" if len(results) == 1 else f"Found {len(results)} hits for '{query}'!"
                            else:
                                response_text = f"No luck finding '{query}'—sorry, bud!"
                        else:
                            response_text = "Hmm, I need a file name to search for. Try again with more details!"
                    elif action_type == "set_reminder":
                        time_str = llm_response.get("time")
                        message = llm_response.get("message")
                        try:
                            reminder_time = datetime.strptime(time_str, "%H:%M").replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
                            if reminder_time < datetime.now():
                                reminder_time += timedelta(days=1)
                            delay = (reminder_time - datetime.now()).total_seconds()
                            if delay > 0:
                                threading.Timer(delay, trigger_reminder, args=[message, ELEVENLABS_API_KEY]).start()
                                response_text = f"Reminder set for {time_str}: {message}"
                            else:
                                response_text = "That time has already passed!"
                        except ValueError:
                            response_text = "Invalid time format for reminder. Use HH:MM."

                    text_to_speech(response_text, ELEVENLABS_API_KEY)
                print("STOP_LISTENING")
    finally:
        sst.close()

if __name__ == "__main__":
    main()