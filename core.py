import time
from datetime import datetime
from pathlib import Path
import csv


class PomodoroTracker():
    """ A pomodoro style studying/work tracking app."""
    def __init__(self):
        # Initializes the app.
        self.state = "inactive"
        self.earlier_state = None
        self.pomodoro_length_sec = 14
        self.break_length_sec = 5
        self.duration_sec = None

        self.end_monotonic = 0
        self.start_pause = 0
        self.start_datetime = None
        self.end_datetime = None

        

        self.remaining_seconds = 0
        self.now_monotonic = time.monotonic()
        self.now_datetime = datetime.now()

        self.dataline = None

        self.path = Path("session_storage.csv")

        self.version_number = "0.1.0"




    def start(self):
        # Changes the state to work and starts the timer.
        self.state = "work"
        self._setup_timer()

    def pause(self):
        # Pauses the work or break state.
        self.earlier_state = self.state
        self.state = "paused"
        self.start_pause = self.now_monotonic
    
    def resume(self):
        # Resumes the work or break state.
        self.state = self.earlier_state
        self.end_monotonic = self.end_monotonic + (self.now_monotonic - self.start_pause)

    def acknowledge(self):
        # Changes the states when ending the work or break session.
        if self.state == "work_overtime":
            self.end_datetime = self.now_datetime
            self.save_session()
            self.state = "break"
        elif self.state == "break" or self.state == "break_overtime":
            self.state = "work"

        self._setup_timer()


    def abort(self):
        # Resets the state to inactive.
        if self.state == "work_overtime":
            self.end_datetime = self.now_datetime
            self.save_session()
        self.state = "inactive"

    def tick(self):
        # Timer that tracks work or breaks.
        self._update_remaining_seconds()
        self._go_overtime() 

    def save_session(self):
        # Saves the dataline to the csv repository.
        self._calculate_duration_sec()
        self._construct_dataline()
        self._save_csv()
        
    def update_time(self):
        self.now_monotonic = time.monotonic()
        self.now_datetime = datetime.now()



    def _save_csv(self):
        with open(self.path, "a", newline ="") as session_storage:
            csv.writer(session_storage).writerow(self.dataline)


    def _calculate_duration_sec(self):
        # Returns the duration of the work session.
        if self.state == "work":
            self.duration_sec = self.pomodoro_length_sec
        elif self.state == "work_overtime":
            self.duration_sec = 0 - self.remaining_seconds


    def _construct_dataline(self):
        # Returns the .csv dataline
        self.dataline = [self.state, self.start_datetime, self.end_datetime, self.duration_sec]

    def _go_overtime(self):
        # Changes the state of break and work to it's overtime counterparts.
        if self.remaining_seconds > 0:
            return self.remaining_seconds
        elif self.remaining_seconds < 0:
            if self.state == "work":
                self.end_datetime = self.now_datetime
                self.save_session()
                self.state = "work_overtime"
                self.start_datetime = self.now_datetime
            elif self.state == "break":
                self.state = "break_overtime"

    def _setup_timer(self):
        # Sets the end of the timer respective of either work or break state
        self.start_datetime = self.now_datetime
        if self.state == "work":
            self.end_monotonic = self.now_monotonic + self.pomodoro_length_sec
        elif self.state == "break":
            self.end_monotonic = self.now_monotonic + self.break_length_sec

    def _update_remaining_seconds(self):
        # Moves the second counter forward
        self.remaining_seconds = self.end_monotonic - self.now_monotonic


def main():
    app = PomodoroTracker()

    while True:
        if app.state == "inactive":
            print(f"{app.state}")
        else:
            print(f"{app.state} remaining: {app.remaining_seconds}")    

        
        command = input(("command (start/pause/resume/acknowledge/abort/quit) > "))
        
        app.update_time()
        app.tick()

        if command == "start":
            app.start()
        elif command == "pause":
            app.pause()
        elif command == "resume":
            app.resume()
        elif command == "acknowledge":
            app.acknowledge()
        elif command == "abort":
            app.abort()
        elif command == "quit":
            break
        
        app.update_time()
        app.tick()


if __name__ == "__main__":
    main()