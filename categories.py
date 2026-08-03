from dataclasses import dataclass

class CircularMergeError(Exception):
    pass

class CategoryStore:
    def __init__(self):
        self.ids_saved = 0
        self.categories = {}

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
    category_store.create_new_category("Admin")
    category_store.create_new_category("Python")
    category_store.categories[0].merged_into = 1

    category_store.merge_category(1, 0)
    print(category_store.categories[1].merged_into)

    


if __name__ == "__main__":
    main()
    

    