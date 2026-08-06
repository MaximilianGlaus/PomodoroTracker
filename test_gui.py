import pytest

import gui_max

@pytest.fixture
def gui():
    gui = gui_max.GuiPomodoroTracker()
    gui.category_store.create_new_category("first_category")
    gui.category_store.create_new_category("second_category")   
    gui.category_store.create_new_category("third_category")
    gui.category_store.create_new_category("fourth_category")
    gui.category_store.merge_category(0,1)
    return gui

def test_update_active_categories(gui):
    gui._update_active_categories()
    assert gui.active_categories == [(1, 'second_category'), (2, 'third_category'), (3, 'fourth_category')]





