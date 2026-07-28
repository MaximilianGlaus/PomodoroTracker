"""Tkinter shell for the Pomodoro Tracker.

This is an ADAPTER (see docs/PORT.md): it turns button clicks into commands the
core understands, and turns the core's state into pixels + a beep. It contains no
timer logic — all of that lives in core.py. The core has no idea this file exists.
"""

import tkinter as tk

from core import PomodoroTracker


def format_time(state, remaining_seconds):
    """Presentation only (ADR-0007): turn the core's raw seconds into a display string.

    The core hands us a signed number of seconds; deciding how to *show* it is the
    shell's job.
    """
    minutes, seconds = divmod(int(abs(remaining_seconds)), 60)
    if state == "inactive":
        return "--:--"
    if state == "paused":
        return "PAUSED"
    if state in ("work_overtime", "break_overtime"):
        return f"+{minutes:02d}:{seconds:02d}"   # negative remaining = counting up into overtime
    return f"{minutes:02d}:{seconds:02d}"          # positive remaining = counting down


class PomodoroGui:
    def __init__(self, root):
        self.app = PomodoroTracker()      # the core, untouched
        self.root = root
        self.previous_state = self.app.state
        root.title("Pomodoro Tracker")

        # --- widgets ---
        self.time_label = tk.Label(root, text="--:--", font=("Helvetica", 48))
        self.time_label.pack(padx=30, pady=(25, 5))

        self.state_label = tk.Label(root, text=self.app.state, font=("Helvetica", 16))
        self.state_label.pack(pady=(0, 15))

        # Each button is the "commands in" half of PORT.md, wired straight to a core method.
        buttons = tk.Frame(root)
        buttons.pack(pady=(0, 25))
        labels = [
            ("Start", self.app.start),
            ("Pause", self.app.pause),
            ("Resume", self.app.resume),
            ("Acknowledge", self.app.acknowledge),
            ("Abort", self.app.abort),
        ]
        for column, (text, method) in enumerate(labels):
            tk.Button(buttons, text=text, command=self._make_handler(method)).grid(
                row=0, column=column, padx=4
            )

        self._heartbeat()   # start the 1-second loop

    def _make_handler(self, method):
        """Return a function that applies one command on the current instant, then redraws."""
        def handler():
            self.app.update_time()   # refresh the clock right before acting
            method()                 # e.g. self.app.acknowledge()
            self.app.tick()
            self._render()
        return handler

    def _heartbeat(self):
        """Runs once a second: advance the clock and redraw.

        This is the loop the framework gives us for free — no threads, no select.
        Because it ticks on its own, a Pomodoro now commits automatically at its
        deadline, even if you never touch a button.
        """
        self.app.update_time()
        self.app.tick()
        self._render()
        self.root.after(1000, self._heartbeat)   # schedule the next beat

    def _render(self):
        self.time_label.config(text=format_time(self.app.state, self.app.remaining_seconds))
        self.state_label.config(text=self.app.state)

        # Beep the instant we cross into an overtime state. We detect the transition by
        # watching the state change (a pragmatic stand-in for a real PORT.md event for now).
        if self.app.state != self.previous_state:
            if self.app.state in ("work_overtime", "break_overtime"):
                self.root.bell()
            self.previous_state = self.app.state


if __name__ == "__main__":
    root = tk.Tk()
    PomodoroGui(root)
    root.mainloop()
