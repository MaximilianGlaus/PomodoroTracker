import core
from pathlib import Path


@pytest.fixture
def test_core():
    """An Pomodoro Core that's accessible to all the functions"""
    tmp_path = Path("tmp_sessions.csv")
    test_core = core.PomodoroTracker(tmp_path)
    return test_core

def test_correct_start_state(test_core):
    """Tests wheter the initial state is "inactive"."""
    assert test_core.state == "inactive"

def test_start(test_core):
    """Tests wheter the star"""
    test_core.start()
    assert test_core.state == "work"
