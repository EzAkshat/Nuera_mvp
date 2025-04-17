import os
import platform
from collections import defaultdict
import json

class FileSearch:
    def __init__(self):
        if os.path.exists("file_index.json"):
            with open("file_index.json", "r") as f:
                self.index = json.load(f)
        else:
            self.index = self.build_index()
            with open("file_index.json", "w") as f:
                json.dump(self.index, f)

    def get_excluded_dirs(self):
        system = platform.system()
        if system == "Windows":
            excluded = [
                "C:\\Windows",
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                os.path.join(os.path.expanduser("~"), "AppData")
            ]
        else:
            excluded = []
        excluded_normalized = [os.path.normcase(d) for d in excluded]
        return excluded_normalized

    def get_root_directories(self):
        if platform.system() == "Windows":
            roots = ["C:\\"]
        else:
            roots = ["/"]
        return roots

    def build_index(self):
        excluded_dirs = self.get_excluded_dirs()
        index = defaultdict(list)
        root_directories = self.get_root_directories()

        for root_dir in root_directories:
            for root, dirs, files in os.walk(root_dir, topdown=True, onerror=self.handle_error):
                dirs[:] = [d for d in dirs if not any(
                    os.path.normcase(os.path.join(root, d)).startswith(excluded)
                    for excluded in excluded_dirs
                )]
                dir_name = os.path.basename(root).lower()
                if dir_name:
                    index[dir_name].append(root)
                for file in files:
                    file_name = file.lower()
                    index[file_name].append(os.path.join(root, file))
        return dict(index)

    def handle_error(self, err):
        pass

    def search(self, query):
        query_lower = query.lower()
        results = self.index.get(query_lower, [])
        return results