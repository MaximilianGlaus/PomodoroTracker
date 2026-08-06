import pytest

import gui

@pytest.fixture
def gui_pomodoro_tracker(tmp_path):
    gui_pomodoro_tracker = gui.GuiPomodoroTracker(tmp_path)
    gui_pomodoro_tracker.category_store.create_new_category("first_category")
    gui_pomodoro_tracker.category_store.create_new_category("second_category")   
    gui_pomodoro_tracker.category_store.create_new_category("third_category")
    gui_pomodoro_tracker.category_store.create_new_category("fourth_category")
    gui_pomodoro_tracker.category_store.merge_category(0,1)
    return gui_pomodoro_tracker

def test_update_active_categories(gui_pomodoro_tracker):
    gui_pomodoro_tracker._update_active_categories()
    assert gui_pomodoro_tracker.active_categories == [(1, 'second_category'), (2, 'third_category'), (3, 'fourth_category')]



def test_get_combobox_values(gui_pomodoro_tracker):
    gui_pomodoro_tracker._update_active_categories()
    assert gui_pomodoro_tracker._get_combobox_values() == ['- none -', 'second_category', 'third_category', 'fourth_category']

def test_resolve_category_id(gui_pomodoro_tracker):
    gui_pomodoro_tracker._update_active_categories()
    selected_category_name = '- none -'
    assert gui_pomodoro_tracker._resolve_category_id(selected_category_name) is None
    selected_category_name = "second_category"
    assert gui_pomodoro_tracker._resolve_category_id(selected_category_name) == 1


    




