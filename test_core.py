import pytest
import csv
import core
from datetime import datetime


@pytest.fixture
def tracker(tmp_path):
    """An Pomodoro Core that's accessible to all the functions"""
    path = tmp_path / "sessions.csv"
    return core.PomodoroTracker(path)


def test_correct_start_state(tracker):
    """Tests wheter the initial state is "inactive"."""
    assert tracker.state == "inactive"

def test_start(tracker):
    """Tests wheter the start function changes the state und remaining seconds is positive"""
    tracker.now_monotonic = 1000
    tracker.start()
    tracker.tick()
    assert tracker.remaining_seconds > 0
    assert tracker.state == "work"


def test_elapsing_duration(tracker):
    """Test the state change after a elapsed pomodoro."""
    tracker.now_monotonic = 1_000
    tracker.start()
    tracker.now_monotonic += (tracker.pomodoro_length_sec + 1)
    tracker.tick()
    assert tracker.state == "work_overtime"

def test_overtime_does_not_drift_into_break_overtime(tracker):
    """Regression: once in work_overtime, further ticks must NOT change the state.

    The old _go_overtime had a catch-all `else` that fired on every tick with a
    negative remaining, so the second tick after elapsing silently flipped
    work_overtime -> break_overtime.
    """
    tracker.now_monotonic = 1_000
    tracker.start()
    tracker.now_monotonic += (tracker.pomodoro_length_sec + 1)
    tracker.tick()
    assert tracker.state == "work_overtime"

    for _ in range(5):
        tracker.now_monotonic += 1
        tracker.tick()
    assert tracker.state == "work_overtime"

def test_work_overtime_to_break(tracker):
    """Test the correct state change from work_overtime to break"""
    tracker.state = "work_overtime"
    tracker.acknowledge()
    assert tracker.state == "break"

def test_paused_time_does_not_accure(tracker):
    """Test the correct function of pausing/resuming"""
    tracker.now_monotonic = 1_000
    tracker.start()
    for n in range(30):
        tracker.now_monotonic += 1
        tracker.tick()
    tracker.pause()
    original_seconds = tracker.remaining_seconds
    original_end_monotonic = tracker.end_monotonic
    advanced_time = 0
    for n in range(30):
        advanced_time += 1
        tracker.now_monotonic += 1
        tracker.tick()
    tracker.resume()
    tracker.tick()
    assert tracker.remaining_seconds == original_seconds
    assert tracker.end_monotonic == original_end_monotonic + advanced_time

def test_csv_storage(tracker):
    tracker.now_monotonic = 1_000
    tracker.pomodoro_length_sec = 15
    tracker.now_datetime = datetime(2026, 7, 30, 9, 29, 41)
    tracker.start()
    tracker.now_datetime = datetime(2026, 7, 30, 9, 54, 41)
    for n in range(tracker.pomodoro_length_sec + 1):
        tracker.now_monotonic += 1
        tracker.tick()
    with open(tracker.storage_path, "r") as f:
        csv_list = list(csv.DictReader(f))

        assert csv_list[0]["type"] ==  "work"
        assert csv_list[0]["start"] == "2026-07-30 09:29:41"
        assert csv_list[0]["end"] == "2026-07-30 09:54:41"
        assert csv_list[0]["duration_sec"] == "15"

def test_csv_storage_over_time_acknowledge(tracker):
    tracker.now_monotonic = 1_000
    tracker.pomodoro_length_sec = 15
    tracker.now_datetime = datetime(2026, 7, 30, 9, 29, 41)
    tracker.start()
    tracker.now_datetime = datetime(2026, 7, 30, 9, 54, 41)
    for n in range(tracker.pomodoro_length_sec + 1):
        tracker.now_monotonic += 1
        tracker.tick() 
    for n in range(1_000):
        tracker.now_monotonic += 1
        tracker.tick()

    tracker.now_datetime = datetime(2026, 7, 30, 10, 54, 41)
    tracker.acknowledge()

    with open(tracker.storage_path, "r") as f:
        csv_list = list(csv.DictReader(f))

        assert csv_list[1]["type"] ==  "work_overtime"
        assert csv_list[1]["start"] == "2026-07-30 09:54:41"
        assert csv_list[1]["end"] == "2026-07-30 10:54:41"
        assert csv_list[1]["duration_sec"] == "1001"

def test_csv_storage_over_time_abort(tracker):
    tracker.now_monotonic = 1_000
    tracker.pomodoro_length_sec = 15
    tracker.now_datetime = datetime(2026, 7, 30, 9, 29, 41)
    tracker.start()
    tracker.now_datetime = datetime(2026, 7, 30, 9, 54, 41)
    for n in range(tracker.pomodoro_length_sec + 1):
        tracker.now_monotonic += 1
        tracker.tick()
    for n in range(1_000):
        tracker.now_monotonic += 1
        tracker.tick()
    tracker.now_datetime = datetime(2026, 7, 30, 10, 54, 41)


    tracker.abort()

    with open(tracker.storage_path, "r") as f:
        csv_list = list(csv.DictReader(f))

        assert csv_list[1]["type"] ==  "work_overtime"
        assert csv_list[1]["start"] == "2026-07-30 09:54:41"
        assert csv_list[1]["end"] == "2026-07-30 10:54:41"
        assert csv_list[1]["duration_sec"] == "1001"

    
    
    

  

        


