from core import PomodoroTracker
from categories import CategoryStore
import sys
import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
from analysis import SessionsAnalysis

class GuiPomodoroTracker:
    def __init__(self, storage_path = None):
        if storage_path is None:
            self._compute_storage_path()
        else:
            self.storage_path = storage_path
        self.core = PomodoroTracker(self.storage_path)
        self.category_store = CategoryStore(self.storage_path)
        self.root = tk.Tk()
        self.sessions_analysis = SessionsAnalysis(storage_path=self.storage_path, categories_dict=self.category_store.create_categories_dict())
        self.root.title(f"Pomodorotracker V{self.core.version_number}")
        self.previous_state = "Startup"
        self.main_font = ("Helvetica", 15)
        self.display_time = "--:--"
        self.display_text = "Inactive"
        self.llm_text = self.sessions_analysis.llm_message
        self.active_categories = []


        # Widget llm report

        self.llm_label = tk.Label(self.root, text=self.llm_text, font=self.main_font, wraplength=400)
        self.llm_label.pack(padx=5,pady=5) 


        #Widget State
        self.state_label = tk.Label(self.root, text=self.core.state, font=self.main_font)
        self.state_label.pack(padx=5,pady=5)

        #Widget Time
        self.time_label = tk.Label(self.root, text=self.core.remaining_seconds, font=self.main_font)
        self.time_label.pack(padx=5,pady=5)

        #Widget Category
        category_frame = tk.Frame(self.root)
        tk.Label(category_frame, text="Current category:", font=self.main_font).pack(side=tk.LEFT)

        self.categories_combobox = ttk.Combobox(
            category_frame,
            values=self._get_combobox_values(),
            state="readonly",
            font=self.main_font,
        )
        self.categories_combobox.pack(side=tk.LEFT, padx=5)
        self.categories_combobox.bind("<<ComboboxSelected>>", self._on_category_selected)

        #Widget New Category
        self.new_categories_button = tk.Button(category_frame, text="Add new category", command = self._on_new_category, font=self.main_font)
        self.new_categories_button.pack(side=tk.LEFT, padx=5)
    

        category_frame.pack(padx=5,pady=5)



        #Widget Action Buttons
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
        self._refresh_categories()
        self._heartbeat()

    def _on_new_category(self):
        name = simpledialog.askstring("New category", "Name:")
        if name is None:
            return
        if not name.strip():
            return
        self.category_store.create_new_category(name)
        self.category_store.save_categories()
        self._refresh_categories()

    def _check_for_llm_update(self):
        if self.core.state != self.previous_state and self.core.state == "break" or self.previous_state == "Startup":
            self.sessions_analysis.update_sessions_analysis()
            self.sessions_analysis.update_llm_message()
            self.llm_text = self.sessions_analysis.llm_message
            self.llm_label.config(text=self.llm_text, font=self.main_font)

    def _update_llm_text(self):
        self.sessions_analysis.update_sessions_analysis()
        self.sessions_analysis.update_llm_message()

    def _get_combobox_values(self):
        """Returns the category names, with '- none -' as the uncategorised option."""
        return ["- none -"] + [name for id, name in self.active_categories]

    def _on_category_selected(self, event):
        """Forwards the selected category to the set_category_id function."""
        selected_category_name = self.categories_combobox.get()
        self.core.set_category_id(self._resolve_category_id(selected_category_name))



    def _resolve_category_id(self, selected_category_name):
        """Receives the drop down selection, returns the category_id."""
        if selected_category_name == "- none -":
            return None
        else:
            for id, name in self.active_categories:
                if name == selected_category_name:
                    return id

    def _refresh_categories(self):
        """Updates all occurences of categories in the gui."""
        self._update_active_categories()
        self.categories_combobox["values"] = self._get_combobox_values()

    def _update_active_categories(self):
        """Attributes to self a filtered list of non-merged pairs of id and name of the categories."""
        self.active_categories = [(c.id, c.name) for c in self.category_store.categories.values()  if c.merged_into is None]
        
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
        self._check_for_llm_update()
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
    gui.root.mainloop()