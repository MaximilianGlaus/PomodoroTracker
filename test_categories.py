from categories import CategoryStore, Category, CircularMergeError
import pytest

@pytest.fixture()
def category_store():
    """Creates a pomodoro category store"""
    category_store = CategoryStore()
    category_store.create_new_category("first_category")
    category_store.create_new_category("second_category")   
    category_store.create_new_category("third_category")
    category_store.create_new_category("fourth_category")   
    return category_store


def test_category_name(category_store):
    assert category_store.categories[0].name == "first_category"
    assert category_store.categories[1].name == "second_category"    

def test_category_id(category_store):
    assert category_store.categories[0].id == 0
    assert category_store.categories[1].id == 1


def test_rename_category(category_store):
    current_id = category_store.categories[0].id
    new_name = "new_name_of_first_category"
    category_store.categories[0].rename(new_name)
    assert category_store.categories[0].name == new_name
    assert category_store.categories[0].id == current_id

def test_resolve_follows_chain(category_store):
    category_store.merge_category(1, 0)      # merge 1 INTO 0
    assert category_store.resolve(1) == 0    # pins the falsy-0 bug

def test_merge_cycle_raises(category_store):
    category_store.merge_category(0, 1)          # 0 -> 1, fine
    with pytest.raises(CircularMergeError):
        category_store.merge_category(1, 0)      # 1 -> 0 would loop

def test_merge_category(category_store):
    """Redirects to new category_id"""
    category_id_to_merge = 0
    new_category_id = 1
    category_store.merge_category(category_id_to_merge, new_category_id)

    assert category_store.categories[category_id_to_merge].merged_into == new_category_id
