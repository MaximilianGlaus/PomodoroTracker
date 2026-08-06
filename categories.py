from dataclasses import dataclass, asdict

from pathlib import Path
import json

class CircularMergeError(Exception):
    pass

class CategoryStore:
    def __init__(self, storage_path=Path("/tmp/pomodoro-dev")):
        """Initializes the categroy store."""
        self.ids_saved = 0
        self.categories = {}
        self.storage_path = storage_path / "category_storage.json"
        self.load_categories()

    def save_categories(self):
        data = [asdict(c) for c in self.categories.values()]
        self.storage_path.write_text(json.dumps(data))

    def load_categories(self):
        if self.storage_path.exists():
            data = json.loads(self.storage_path.read_text())
            self.categories = {d["id"]:Category(**d) for d in data}
            self.ids_saved = (max(self.categories.keys())+1)


    def create_new_category(self, category_name):
        new_category = Category(category_name, self._create_category_id())
        self.categories[new_category.id]= new_category
        return new_category

    def get(self, id):
        return self.categories[id]

    def merge_category(self, category_id_to_merge, new_category_id):
        if self.resolve(new_category_id) == category_id_to_merge:
             raise CircularMergeError(f"merging {category_id_to_merge} into {new_category_id} would create a cycle")
        self.categories[category_id_to_merge].merged_into = new_category_id

    def resolve(self, id):
        visited_categories = []
        current_category = self.categories[id]
        while current_category.merged_into is not None:     
            if current_category.id in visited_categories:
                raise CircularMergeError(f"category {id} is part of a merge cycle")
            visited_categories.append(current_category.id)
            current_category = self.categories[current_category.merged_into]
        return current_category.id

            
    def _create_category_id(self):
        """Assign and return the next sequential ID, incrementing by one each call."""
        new_id = int(self.ids_saved)
        self.ids_saved += 1
        return new_id



@dataclass
class Category:
    """Class to label the  content of a pomodoro session"""
    name: str
    id: int 
    merged_into: int = None


    def rename(self, new_name):
        """Renames category, retaining the ID"""
        self.name = new_name
        return self.name


def main():
    category_store = CategoryStore()
    category_store.create_new_category("first_category")
    category_store.create_new_category("second_category")   
    category_store.create_new_category("third_category")
    category_store.create_new_category("fourth_category") 
    category_store.merge_category(0, 1)
    category_store.save_categories()
    print(category_store.storage_path.parent)
    
    fresh_category_store = CategoryStore()
    fresh_category_store.load_categories
    print(fresh_category_store.categories[0].name)



    


if __name__ == "__main__":
    main()
    

    