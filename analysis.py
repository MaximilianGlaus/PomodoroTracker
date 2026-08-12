from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, date
from pathlib import Path
import csv

@dataclass
class SessionRecord:
    type: str
    start: datetime
    end: datetime
    duration_sec: int
    category_id: int

@dataclass
class Day:
    date: datetime.date
    weekday: str
    duration_total: int
    duration_per_category: {}



class SessionsAnalysis:
    def __init__(self, storage_path= Path("/tmp/pomodoro-dev")):
        self.session_records = None
        self.storage_path = storage_path / "sessions.csv"
        self.target_by_day = 22_500
        self.today = None
        self.todays_progess = 0
        self.sessions_by_days = {}
        self.days = {}
        self.last_week = {}

    def _load_session_records_csv(self):
        if self.storage_path.exists():
            records = []
            with open(self.storage_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["category_id"] != "":
                        category_id = int(row["category_id"])
                    else: 
                        category_id = None
                    records.append({
                        "type" : row["type"], 
                        "start" : datetime.strptime(row["start"], "%Y-%m-%d %H:%M:%S"), 
                        "end" : datetime.strptime(row["end"], "%Y-%m-%d %H:%M:%S"), 
                        "duration_sec" : int(float(row["duration_sec"])),
                        "category_id" : category_id})
            self.session_records = [SessionRecord(**session_record) for session_record in records]

    def _update_days(self):
        for day in self.sessions_by_days:
            duration_total = 0
            duration_per_category = {}
            for session in self.sessions_by_days[day]:
                duration_total +=session.duration_sec
                if session.category_id in duration_per_category:
                    duration_per_category[session.category_id] +=session.duration_sec
                else: 
                    duration_per_category[session.category_id] = session.duration_sec

            date= datetime.strptime(day, "%Y-%m-%d")
            weekdays =["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekday = weekdays[date.weekday()]
            self.days[day] = Day(date=date, weekday=weekday, duration_total=duration_total, duration_per_category=duration_per_category)

    def _session_records_group_by_days(self):
        for session_record in self.session_records:
            date = datetime.date(session_record.start)
            if str(date) in self.sessions_by_days:
                self.sessions_by_days[str(date)].append(session_record)
            else: 
                self.sessions_by_days[f"{date}"] = [session_record]


    def _update_days_worked_last_week(self):
        today = datetime.today()
        for days_ago in range(1,8):
            days_ago=timedelta(days_ago)
            past_day=(today-days_ago)
            if past_day.strftime("%Y-%m-%d") in list(self.days.keys()):
                self.last_week[f"{past_day.strftime('%Y-%m-%d')}"] = self.days[past_day.strftime("%Y-%m-%d")]

    def _update_today(self):
        today = datetime.today()
        if today.strftime("%Y-%m-%d") in list(self.sessions_by_days.keys()):
            self.today = self.sessions_by_days[today.strftime("%Y-%m-%d")]
        print(type(self.today))

    def _update_todays_progess(self):
        today = datetime.today()
        if today.strftime("%Y-%m-%d") in list(self.days.keys()):
            self.todays_progess = self.days[today.strftime("%Y-%m-%d")].duration_total
        print(self.todays_progess)



   

            

if __name__ == "__main__":
    sessions_analysis = SessionsAnalysis(Path("."))
    sessions_analysis._load_session_records_csv()
    sessions_analysis._session_records_group_by_days()
    sessions_analysis._update_days()
    sessions_analysis._update_days_worked_last_week()
    sessions_analysis._update_today()
    sessions_analysis._update_todays_progess()



