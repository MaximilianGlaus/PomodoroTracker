from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, date
from pathlib import Path
from dotenv import load_dotenv
import csv, json
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
import os
from categories import CategoryStore
from prompts import DEVELOPER_ROLE


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
    duration_total_sec: int
    duration_per_category: {}

class APIkeyError(Exception):
    pass

class SessionsAnalysis:
    def __init__(self, categories_dict = None, storage_path= Path("/tmp/pomodoro-dev"), api_key = None, pomodoro_length_sec = 25 * 60, pomodoro_daily_target = 15, ):
        self.session_records = None
        self.session_storage_path = storage_path / "sessions.csv"
        self.pomodoro_length_sec = pomodoro_length_sec
        self.target_by_day_sec = pomodoro_daily_target * self.pomodoro_length_sec
        self.categories_dict = categories_dict
        self.today = None
        self.todays_duration = 0
        self.todays_progess_in_percent = 0
        self.sessions_by_days = {}
        self.days = {}
        self.last_week = {}
        self.developer_role = DEVELOPER_ROLE
        self.prompt = None
        self.llm_message = None
        self.api_key = api_key
        self.setup_llm()
        self.llm_completion = None

        self.used_completion_tokens = 0
        self.used_prompt_tokens = 0
        self.update_sessions_analysis()

        
    def update_sessions_analysis(self):
        self._load_session_records_csv()
        self._session_records_group_by_days()
        self._update_days()
        self._update_days_worked_last_week()
        self._update_today()
        self._update_todays_duration()
        self._update_todays_progress()

    def update_llm_message(self):
        self._assemble_prompt()
        self._launch_llm_call()

    def setup_llm(self):
        if self._load_api_key():
            if self.api_key is not None:
                self.llm_client = OpenAI(api_key=self.api_key)
            else:
                self.llm_client = OpenAI()
        else:
            self.llm_client = None




    def _load_session_records_csv(self):
        if self.session_storage_path.exists():
            records = []
            with open(self.session_storage_path, "r") as f:
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

    def _session_records_group_by_days(self):
        self.sessions_by_days = {}
        for session_record in self.session_records:
            date = datetime.date(session_record.start)
            
            if str(date) in self.sessions_by_days:
                self.sessions_by_days[str(date)].append(session_record)
            else: 
                self.sessions_by_days[f"{date}"] = [session_record]




    def _update_days(self):
        for day in self.sessions_by_days:
            duration_total_sec = 0
            duration_per_category = {}
            for session in self.sessions_by_days[day]:
                duration_total_sec +=session.duration_sec
                if session.category_id in duration_per_category:
                    duration_per_category[session.category_id] +=session.duration_sec
                else: 
                    duration_per_category[session.category_id] = session.duration_sec

            date= datetime.strptime(day, "%Y-%m-%d")


            self.days[day] = Day(date=date, weekday=self._weekday(date), duration_total_sec=duration_total_sec, duration_per_category=duration_per_category)

    def _weekday(self, date):
        weekdays =["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return weekdays[date.weekday()]

    def _update_days_worked_last_week(self):
        today = datetime.today()
        for days_ago in reversed(range(1,8)):
            days_ago=timedelta(days_ago)
            past_day=(today-days_ago)
            if past_day.strftime("%Y-%m-%d") in list(self.days.keys()):
                self.last_week[f"{past_day.strftime('%Y-%m-%d')}"] = self.days[past_day.strftime("%Y-%m-%d")]
            else:
                self.last_week[f"{past_day.strftime('%Y-%m-%d')}"] = Day(date=past_day.strftime("%Y-%m-%d"), weekday=self._weekday(past_day), duration_total_sec=0, duration_per_category={})


    def _update_today(self):
        today = datetime.today()
        if today.strftime("%Y-%m-%d") in list(self.sessions_by_days.keys()):
            self.today = self.sessions_by_days[today.strftime("%Y-%m-%d")]
        else:
            self.today = []

    def _update_todays_duration(self):
        today = datetime.today()
        if today.strftime("%Y-%m-%d") in list(self.days.keys()):
            self.todays_duration = self.days[today.strftime("%Y-%m-%d")].duration_total_sec

    def _update_todays_progress(self):
        self.todays_progess_in_percent =  int(100*(self.todays_duration / self.target_by_day_sec))


    def _convert_sec_to_pomodoros(self, seconds):
        """Returns number of pomodoros up to one decimal point"""
        pomodoros = round(seconds / self.pomodoro_length_sec,1)
        return pomodoros

    def _convert_pomodoros_to_sec(self, pomodoros):
        """Returns number of pomodors up to one decimal point"""
        seconds = round(pomodoros * self.pomodoro_length_sec,1)
        return seconds

    def _assemble_prompt(self):
        # Adapt today to pomodoros, inject category names
        day_dict = [asdict(c) for c in self.today]
        deletion_list = []
        count = 0
        for session in day_dict:
            duration_pomodoro = self._convert_sec_to_pomodoros(session["duration_sec"])
            del session["duration_sec"]
            if session["category_id"] is not None:
                session["category_name"] = self.categories_dict[session["category_id"]]
            else:
                    session["category_name"] = "No Category"
            session["duration_pomodoro"] = duration_pomodoro
            if duration_pomodoro < 0.1:
                deletion_list.append(count)
            count += 1
        deletion_list = reversed(deletion_list)   
        for index in deletion_list:
            del day_dict[index]       
        day_dict = json.dumps(day_dict, default=str)


        # Adapt last week to pomodoros
        week_dict = {date_key : asdict(day_obj) for date_key, day_obj in self.last_week.items()}
        for day_values in week_dict.values():
            duration_total_pomodoros = self._convert_sec_to_pomodoros(day_values["duration_total_sec"]) 
            day_values.pop("duration_total_sec")
            day_values["duration_total_pomodoros"] = duration_total_pomodoros
            day_categories_dict = {}
            for key, value in day_values['duration_per_category'].items():
                if key is not None:
                    day_categories_dict[self.categories_dict[key]] = value
                else:
                    day_categories_dict["No Category"] = value
            day_values.pop('duration_per_category')
            day_values["duration_per_category"] = day_categories_dict

            for category_name, category_values in day_values["duration_per_category"].items():
                day_values["duration_per_category"][category_name] = self._convert_sec_to_pomodoros(category_values)
        week_dict = json.dumps(week_dict, default=str)

        # Context
        time = "Current time/day: " + str(datetime.now().replace(microsecond=0))
        units = "Pomodoro lenght: " + str(self.pomodoro_length_sec) + " seconds"
        context = "\n".join(["Context: ", time, units])

        # Progess
        todays_progess = f"Today's Progress: {self.todays_progess_in_percent}%\nTarget Number of Pomodoros: {self._convert_sec_to_pomodoros(self.target_by_day_sec)}\nCompleted Sessions: {self._convert_sec_to_pomodoros(self.todays_duration)}"
        todays_sessions = f"Today's Sessions:\n{day_dict}"
        last_week = f"Last seven days:\n{week_dict}"
        self.prompt =  "\n\n".join([context, todays_progess, todays_sessions, last_week])
        print(self.prompt)

    def _launch_llm_call(self):
        try:
            self._create_llm_call()
        except AuthenticationError:
            self.llm_message = "AuthenticationError"
        except RateLimitError:
            self.llm_message = "RateLimitError"
        except APIConnectionError:
            self.llm_message = "APIConnectionError"

    def _create_llm_call(self):
        start_time = datetime.now()
        if self.llm_client is not None:
            self.llm_completion = self.llm_client.chat.completions.create(
                model = "gpt-5-nano",
                reasoning_effort = "low",
                messages= [
                    {"role": "developer", "content" : self.developer_role},
                    {"role": "user", "content" : self.prompt},
                ]
            )
            end_time = datetime.now()

            elapsed_time = end_time - start_time
            self.llm_message = self.llm_completion.choices[0].message.content      
            self.used_completion_tokens += self.llm_completion.usage.completion_tokens
            self.used_prompt_tokens += self.llm_completion.usage.prompt_tokens
            print(self.llm_message)
            print(f"Elapsed time: {elapsed_time}")
            print(f"Completion Tokens: {self.used_completion_tokens}") 
            print(f"Prompt Tokens: {self.used_prompt_tokens}")   
            print(self.llm_completion)    

    def _load_api_key(self):
        load_dotenv()
        if os.getenv("OPENAI_API_KEY") is None:
            if self.api_key is None:
                self.llm_message = "API key value is None!"
            else:
                return True
        elif os.getenv("OPENAI_API_KEY") ==  "":
            if self.api_key is None:
                self.llm_message = "API key is empty!"
            else:
                return True
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            return True




if __name__ == "__main__":
    categories = CategoryStore()
    sessions_analysis = SessionsAnalysis(categories_dict=categories.create_categories_dict())
    sessions_analysis.update_sessions_analysis()
    sessions_analysis.update_llm_message()
    print(sessions_analysis.llm_message)







