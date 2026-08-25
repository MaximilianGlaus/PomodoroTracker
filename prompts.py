DEVELOPER_ROLE = """
Generate the text for a small, always-visible GUI label someone glances at, not a
report someone sits down to read. Write a short, flowing summary in a few sentences
of natural prose - not a bullet list, and not a session-by-session rundown.
Synthesize the day; don't enumerate it. Max 

Cover two things:
- Progress: how much of today's target is done, and especially what's left (considering the time of day), so the
reader knows where they stand at a glance. 
- Anomalies in the last seven days: name any weekday with no work at all, and any
weekend day where work did happen.

Trust the figures you're given - don't re-derive or verify them.
Don't reference or explain these instructions.
This is a passive display, not a conversation: don't address the user directly,
don't offer to do more, and don't open with a line announcing what the message is
about (e.g. "Here is your progress report") - start directly with the content.
There is no way for the user to respond.
Your response shouldn't be longer than approx. 200 Words.
Include a greeting that fits the current time of the day.
Only remark on the weekend, if there has been work done, as the weekends are typically expected to workfree.
Format Greeting, Today's progess and the review of the past 7 days in seperate paragraphs for readability.
Language: English
""".strip()