import analysis, pytest, csv, unittest, httpx2, openai
from unittest.mock import patch, MagicMock





@pytest.fixture
def sessions_analysis(tmp_path):
    sessions_analysis = analysis.SessionsAnalysis(storage_path=tmp_path)
    return sessions_analysis

def write_sessions_csv(path, rows):
    """Creates a .csv file from given rows in tmp and returns the path to it"""
    with open(path, "w", newline="") as f:
          fieldnames=["type", "start", "end", "duration_sec", "category_id"]
          writer = csv.DictWriter(f, fieldnames=fieldnames)
          writer.writeheader()
          for row in rows:
              writer.writerow(row)
    
    return path



@pytest.fixture
def mock_llm_client():
    """Mock of the OpenAI client."""
    client = MagicMock()
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = "LLM Response"
    completion.usage.completion_tokens = 500
    completion.usage.prompt_tokens = 450


    client.chat.completions.create.return_value = completion
    return client

@pytest.fixture
def mock_llm_client_auth_error():
    """Mock of the OpenAI client."""
    client = MagicMock()
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = "LLM Response"
    completion.usage.completion_tokens = 500
    completion.usage.prompt_tokens = 450

    fake_request =  httpx2.Request("POST", "https://api.openai.com/v1/chat/completions")
    fake_response = httpx2.Response(401, request=fake_request)
    fake_error = openai.AuthenticationError("bad key", response=fake_response, body=None)

    client.chat.completions.create.side_effect = fake_error
    return client

@pytest.fixture
def mock_llm_client_rate_limit_error():
    """Mock of the OpenAI client."""
    client = MagicMock()
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = "LLM Response"
    completion.usage.completion_tokens = 500
    completion.usage.prompt_tokens = 450

    fake_request =  httpx2.Request("POST", "https://api.openai.com/v1/chat/completions")
    fake_response = httpx2.Response(429, request=fake_request)
    fake_error = openai.RateLimitError("Too Many Requests", response=fake_response,  body=None)

    client.chat.completions.create.side_effect = fake_error
    return client


@pytest.fixture
def mock_llm_client_connection_error():
    """Mock of the OpenAI client."""
    client = MagicMock()
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = "LLM Response"
    completion.usage.completion_tokens = 500
    completion.usage.prompt_tokens = 450

    fake_request =  httpx2.Request("POST", "https://api.openai.com/v1/chat/completions")
    fake_response = httpx2.Response(401, request=fake_request)
    fake_error = openai.APIConnectionError(request=fake_request)

    client.chat.completions.create.side_effect = fake_error
    return client


def test_sessions_by_days_idempotent(sessions_analysis):
    """Tests that sessions_by_days does not double on repeated update"""
    rows=[
        {
                "type": "work", 
                "start": "2026-08-10 09:00:00", 
                "end": "2026-08-10 09:25:00",
                "duration_sec": "1500", 
                "category_id": "1"
                }, 
        {
                "type": "work", 
                "start": "2026-08-11 09:00:00", 
                "end": "2026-08-11 09:25:00",
                "duration_sec": "1500", 
                "category_id": "1"
                },
                ]
    sessions_analysis.session_storage_path = write_sessions_csv(sessions_analysis.session_storage_path, rows)

    sessions_analysis.update_sessions_analysis()
    days_1 = sessions_analysis.days.copy()
    sessions_analysis.update_sessions_analysis()
    days_2 = sessions_analysis.days.copy()

    assert days_1 == days_2

def test_update_days_duration_aggregation(sessions_analysis):
    """Tests the aggregation of duration for each category during the day."""
    rows=[
        {
                "type": "work", 
                "start": "2026-08-10 09:00:00", 
                "end": "2026-08-10 09:25:00",
                "duration_sec": "1500", 
                "category_id": "1"
                }, 
        {
                "type": "work", 
                "start": "2026-08-10 09:30:00", 
                "end": "2026-08-10 09:55:00",
                "duration_sec": "1500", 
                "category_id": "2"
                },
                ]
    sessions_analysis.session_storage_path = write_sessions_csv(sessions_analysis.session_storage_path, rows)
    sessions_analysis.update_sessions_analysis()
    duration_cat_1_1 = sessions_analysis.days["2026-08-10"].duration_per_category[1]

    rows=[
        {
                "type": "work", 
                "start": "2026-08-10 09:00:00", 
                "end": "2026-08-10 09:25:00",
                "duration_sec": "1500", 
                "category_id": "1"
                }, 
        {
                "type": "work", 
                "start": "2026-08-10 09:30:00", 
                "end": "2026-08-10 09:55:00",
                "duration_sec": "1500", 
                "category_id": "2"
                },
        {
                "type": "work", 
                "start": "2026-08-10 10:00:00", 
                "end": "2026-08-10 10:25:00",
                "duration_sec": "1500", 
                "category_id": "1"
                },
                ]
    sessions_analysis.session_storage_path = write_sessions_csv(sessions_analysis.session_storage_path, rows)

    sessions_analysis.update_sessions_analysis()
    duration_cat_1_2 = sessions_analysis.days["2026-08-10"].duration_per_category[1]
    assert duration_cat_1_1 + 1500 == duration_cat_1_2


def test_write_laod_token_count(sessions_analysis):

    sessions_analysis.used_completion_tokens = 31136
    sessions_analysis.used_prompt_tokens = 26508
    sessions_analysis._save_token_count()
    sessions_analysis.used_completion_tokens = 0
    sessions_analysis.used_prompt_tokens = 0
    sessions_analysis._load_token_count()
    assert sessions_analysis.used_completion_tokens == 31136
    assert sessions_analysis.used_prompt_tokens == 26508

def test_happy_path(sessions_analysis, mock_llm_client):
    sessions_analysis.llm_client = mock_llm_client
    sessions_analysis._launch_llm_call()
    assert sessions_analysis.llm_message == "LLM Response"


def test_401_bad_key(sessions_analysis, mock_llm_client_auth_error):
    sessions_analysis.llm_client = mock_llm_client_auth_error
    sessions_analysis._launch_llm_call()
    assert sessions_analysis.llm_message == "AuthenticationError"

def test_429_rate_limit(sessions_analysis, mock_llm_client_rate_limit_error):
    sessions_analysis.llm_client = mock_llm_client_rate_limit_error
    sessions_analysis._launch_llm_call()
    assert sessions_analysis.llm_message == "RateLimitError"

def test_connection_error(sessions_analysis, mock_llm_client_connection_error):
    sessions_analysis.llm_client = mock_llm_client_connection_error
    sessions_analysis._launch_llm_call()
    assert sessions_analysis.llm_message == "APIConnectionError"

# sessions_analysis.llm_completion.usage.completion_tokens











# class FakeClient():
#     def __init__(self):
#         self.chat = Chat()

# class Chat():
#     def __init__(self):
#             self.completion = ChatCompletion()

# class ChatCompletion():
#     def __init__(self):
#         self.id = None
#         self.model = None
#         self.reasoning_effort = None
#         self.messages = None
#         self.choice =


#     def create(self, model, reasoning_effort, messages):
#             self.model = model
#             self.reasoning_effort = reasoning_effort
#             self.messages = messages


#             return ChatCompletion(
#     id='chatcmpl-EEwnnETGMTX00zRv9sQY1z86c9uDl', 
#     choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Good afternoon.\n\nToday’s progress: 9% of the 15-pomodoro target is done, with 1.5 completed sessions so far today. Remaining work for the day is about 13.5 pomodoros, so pace could shape the rest of the afternoon if continued at the current rhythm.\n\nPast seven days review: Thursday and Friday showed zero work, and Saturday and Sunday also had no activity, marking a quiet weekend. Weekdays resumed with notable productivity: Monday logged 16.6 pomodoros (Output 15.2, Troubleshooting 1.4), Tuesday 12.5 pomodoros (Output 12.5), and Wednesday 12.9 pomodoros (Output 12.9).', refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=None))], created=1787231335, model='gpt-5-nano-2025-08-07', object='chat.completion', moderation=None, service_tier='default', system_fingerprint=None, usage=CompletionUsage(completion_tokens=671, prompt_tokens=856, total_tokens=1527, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=512, rejected_prediction_tokens=0, text_tokens=None), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cache_write_tokens=None, cached_tokens=0, image_tokens=None, text_tokens=None)))

# class Choice():
#       def __init__(self):
#             self.message = ChatCompletionMessage()

# class ChatCompletionMessage():
#       def __init__(self):
#             self.content =

# llm_client = FakeClient()

# llm_completion = llm_client.chat.completion.create(model = "gpt-5-nano", reasoning_effort = "low",
#                 messages= [
#                     {"role": "developer", "content" : "self.developer_role"},
#                     {"role": "user", "content" : "self.prompt"},
#                 ])


#             self.llm_message = self.llm_completion.choices[0].message.content   




# # self.llm_completion = self.llm_client.chat.completions.create(model = "gpt-5-nano", reasoning_effort = "low",
# #     messages= [
# #         {"role": "developer", "content" : self.developer_role},
# #         {"role": "user", "content" : self.prompt},
# #     ]



# # self.llm_message = self.llm_completion.choices[0].message.content      
# # self.used_completion_tokens += self.llm_completion.usage.completion_tokens
# # self.used_prompt_tokens += self.llm_completion.usage.prompt_tokens
# # print(self.llm_message)