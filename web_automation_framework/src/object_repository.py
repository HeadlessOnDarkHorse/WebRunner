import json
from typing import List, Dict, Set

class ObjectRepository:
    def __init__(self, filepath: str = "object_repository.json"):
        self.filepath = filepath
        self.objects: Dict[str, Dict] = {}

    def add_object(self, obj: Dict, page_url: str):
        """Adds a new object to the repository."""
        # Use a unique key for each object to avoid duplicates
        key = f"{obj['tag']}_{obj['name']}_{obj['text']}"

        if key not in self.objects:
            self.objects[key] = {
                "tag": obj["tag"],
                "name": obj["name"],
                "text": obj["text"],
                "roles": set([obj["role"]]),
                "pages": set([page_url]),
                "assertions": []
            }
        else:
            self.objects[key]["pages"].add(page_url)
            self.objects[key]["roles"].add(obj["role"])

    def save(self):
        """Saves the object repository to a JSON file."""
        # Convert sets to lists for JSON serialization
        serializable_objects = []
        for obj in self.objects.values():
            obj["pages"] = list(obj["pages"])
            obj["roles"] = list(obj["roles"])
            serializable_objects.append(obj)

        with open(self.filepath, "w") as f:
            json.dump(serializable_objects, f, indent=4)
        print(f"Saved object repository to: {self.filepath}")
