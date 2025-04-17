import os
import subprocess
import pythoncom
from win32com.shell import shell
from urllib.parse import quote_plus
import json

def get_start_menu_apps():
    if os.path.exists("apps.json"):
        with open("apps.json", "r") as f:
            apps = json.load(f)
    else:
        start_menu_paths = [
            os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        ]
        apps = {}
        for path in start_menu_paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.lnk'):
                        shortcut_path = os.path.join(root, file)
                        shell_link = pythoncom.CoCreateInstance(
                            shell.CLSID_ShellLink, None,
                            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
                        )
                        shell_link.QueryInterface(pythoncom.IID_IPersistFile).Load(shortcut_path)
                        target, _ = shell_link.GetPath(shell.SLGP_SHORTPATH)
                        name = os.path.splitext(file)[0].lower()
                        apps[name] = target
        with open("apps.json", "w") as f:
            json.dump(apps, f)
    return apps

def launch_application(app_name, action, parameter, apps):
    matching_apps = [name for name in apps if app_name.lower() in name.lower()]
    if not matching_apps:
        return f"Whoops! Can't find '{app_name}' anywhere!"
    if len(matching_apps) > 1:
        return f"Hmm, too many '{app_name}'s: {', '.join(matching_apps)}. Pick one!"
    app_path = apps[matching_apps[0]]
    app_display_name = matching_apps[0]

    if action and not is_browser(app_display_name):
        return f"'{app_display_name}' isn’t a browser, so no '{action}' for you!"

    try:
        if action == "go_to" and parameter:
            subprocess.Popen([app_path, parameter])
            return f"Zooming to '{parameter}' in '{app_display_name}'!"
        elif action == "search" and parameter:
            search_url = f"https://www.google.com/search?q={quote_plus(parameter)}"
            subprocess.Popen([app_path, search_url])
            return f"Searching '{parameter}' in '{app_display_name}'—hold tight!"
        else:
            subprocess.Popen([app_path])
            return f"Launching '{app_display_name}' like a rocket!"
    except OSError as e:
        return f"Oof, '{app_display_name}' didn’t want to launch. Sad times."

def is_browser(app_name):
    browser_keywords = ["chrome", "brave", "firefox", "edge", "opera", "safari"]
    return any(keyword in app_name.lower() for keyword in browser_keywords)