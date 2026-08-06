from core import PomodoroTracker
from categories import CategoryStore
import sys
import tkinter as tk
from pathlib import Path

class GuiPomodoroTracker:
    def __init__(self):
        self._compute_storage_path()
        self.core = PomodoroTracker(self.storage_path)
        self.category_store = CategoryStore(self.storage_path)
        self.root = tk.Tk()
        self.root.title(f"Pomodorotracker V{self.core.version_number}")
        self.previous_state = self.core.state
        self.main_font = ("Helvetica", 15)
        self.display_time = "--:--"
        self.display_text = "Inactive"

        self.active_categories = []



        #Widgets
        self.state_label = tk.Label(self.root, text=self.core.state, font=self.main_font)
        self.state_label.pack(padx=5,pady=5)

        self.time_label = tk.Label(self.root, text=self.core.remaining_seconds, font=self.main_font)
        self.time_label.pack(padx=5,pady=5)

        buttonframe = tk.Frame(self.root)

        commands = [["Start", self.core.start],
                    ["Pause", self.core.pause],
                    ["Resume", self.core.resume],
                    ["Acknowledge", self.core.acknowledge],
                    ["Abort", self.core.abort]
        ]

        for column, [name, method] in enumerate(commands):
            button = tk.Button(buttonframe, text=name, command=self._make_handler(method), font=self.main_font)
            button.grid(row=0,column=column, sticky=tk.W+tk.E)
        
        buttonframe.pack(padx=5, pady=5)

        self._heartbeat()

    def _update_active_categories(self):
        """Returns a filtered list of non-merged pairs of id and name of the categories."""
        for id in self.category_store.categories:
            if self.category_store.categories[id].merged_into == None:
                self.active_categories.append((self.category_store.categories[id].id, self.category_store.categories[id].name))
    
    def _make_handler(self,method):
        def handler():
            self.core.update_time()
            self.core.tick()
            method()
            self.core.tick()
            self._render()
            #print(f"handler fired, earlier state was:", self.core.earlier_state)
            #print(f"handler fired, state is now:", self.core.state)
        return handler
    
    def _heartbeat(self):
        self.core.update_time()
        self.core.tick()
        self._render()
        self.root.after(500, self._heartbeat)

    def _format_text(self):
        if self.core.state == "inactive":
            self.display_text = "No work session active"
        elif self.core.state == "work":
            self.display_text = f"{(self.core.pomodoro_length_sec/60):.2f} min work session"
        elif self.core.state == "break":
            self.display_text = f"{(self.core.break_length_sec/60):.2f}min break session"
        elif self.core.state == "break_overtime":
            self.display_text = "Break session overtime"
        elif self.core.state == "work_overtime":
            self.display_text = "Work session overtime:"


    def _format_time(self):
        if self.core.state == "inactive":
            self.display_time = "--:--"
        elif self.core.state == "work" or self.core.state == "break":
            min, sec = divmod(int(self.core.remaining_seconds), 60)
            self.display_time = f"{min:02d}:{sec:02d}"
        elif self.core.state == "work_overtime" or self.core.state == "break_overtime":
            min, sec = divmod(abs(int(self.core.remaining_seconds)), 60)
            self.display_time = f"{min:02d}:{sec:02d}"
   

    def _render(self):
        self._format_text()
        self.state_label.config(text=self.display_text, font=self.main_font)
        self._format_time()
        self.time_label.config(text=self.display_time, font=self.main_font)

        if self.core.state != self.previous_state:
            self.root.bell()
        self.previous_state = self.core.state

    def _compute_storage_path(self):
        import os

        env_override = os.environ.get("POMODORO_DATA_DIR")
        if env_override:
            data_dir = Path(env_override)
        elif getattr(sys, "frozen", False):
            data_dir = Path.home() / "Library" / "Application Support" / "PomodoroTracker" 
        else:
            data_dir = Path("/tmp/pomodoro-dev")

        data_dir.mkdir(parents=True, exist_ok=True)
        self.storage_path = data_dir 
        print(f"[path] {self.storage_path}")




if __name__ == "__main__":
    gui = GuiPomodoroTracker()

    gui.category_store.create_new_category("first_category")
    gui.category_store.create_new_category("second_category")   
    gui.category_store.create_new_category("third_category")
    gui.category_store.create_new_category("fourth_category")
    gui.category_store.merge_category(0,1)
    gui._update_active_categories()
    print(gui.active_categories)
    # gui.root.mainloop()