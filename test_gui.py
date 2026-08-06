import pytest

import gui_max

@pytest.fixture
def gui(tmp_path):
    gui = gui_max.GuiPomodoroTracker(tmp_path)
    gui.category_store.create_new_category("first_category")
    gui.category_store.create_new_category("second_category")   
    gui.category_store.create_new_category("third_category")
    gui.category_store.create_new_category("fourth_category")
    gui.category_store.merge_category(0,1)
    return gui

def test_update_active_categories(gui):
    gui._update_active_categories()
    assert gui.active_categories == [(1, 'second_category'), (2, 'third_category'), (3, 'fourth_category')]



def test_get_combobox_values(gui):
    gui._update_active_categories()
    assert gui._get_combobox_values() == ['- none -', 'second_category', 'third_category', 'fourth_category']

def test_resolve_category_id(gui):
    gui._update_active_categories()
    selected_category_name = '- none -'
    assert gui._resolve_category_id(selected_category_name) == None
    selected_category_name = "second_category"
    assert gui._resolve_category_id(selected_category_name) == 1


    




