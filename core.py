import time

class PomodoroTracker():
    """ A pomodoro style studying/work tracking app."""
    def __init__(self):
        # Initializes the app.
        self.state = "inactive"
        self.earlier_state = None
        self.pomodoro_length_sec = 14
        self.break_length_sec = 5
        self.end_monotonic = 0
        self.start_pause = 0
        self.remaining_seconds = 0
        self.now = time.monotonic()

    def start(self):
        # Changes the state to work and starts the timer.
        self.state = "work"
        self._set_end()

    def pause(self):
        # Pauses the work or break state.
        self.earlier_state = self.state
        self.state = "paused"
        self.start_pause = self.now
    
    def resume(self):
        # Resumes the work or break state.
        self.state = self.earlier_state
        self.end_monotonic = self.end_monotonic + (self.now - self.start_pause)

    def acknowledge(self):
        # Changes the states when ending the work or break session.
        if self.state == "work_overtime":
            self.state = "break"
        elif self.state == "break" or self.state == "break_overtime":
            self.state = "work"
        self._set_end()


    def abort(self):
        # Resets the state to inactive.
        self.state = "inactive"

    def tick(self):
        # Timer that tracks work or breaks.
        self._update_remaining_seconds()
        self._go_overtime() 

    def _go_overtime(self):
        # Changes the state of break and work to it's overtime counterparts.
        if self.remaining_seconds > 0:
            return self.remaining_seconds
        elif self.remaining_seconds < 0:
            if self.state == "work":
                self.state = "work_overtime"
            elif self.state == "break":
                self.state = "break_overtime"

    def _set_end(self):
        # Sets the end of the timer respective of either work or break state
        if self.state == "work":
            self.end_monotonic = self.now + self.pomodoro_length_sec
        elif self.state == "break":
            self.end_monotonic = self.now + self.break_length_sec

    def _update_remaining_seconds(self):
        # Moves the second counter forward
        self.remaining_seconds = self.end_monotonic - self.now

def main():
    app = PomodoroTracker()
    app.start()
    test_timer = 0
    while test_timer <15 :

        app.now = time.monotonic()
        if test_timer > 5:
            app.pause()
            while test_timer <10:
                time.sleep(1)
                test_timer +=1
            app.now = time.monotonic()
            app.resume()
        app.tick()
        print(app.remaining_seconds)
        time.sleep(1)
        test_timer += 1

main()