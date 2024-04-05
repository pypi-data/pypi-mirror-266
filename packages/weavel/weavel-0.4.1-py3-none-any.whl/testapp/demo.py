from weavel import create_client, WeavelClient, Trace
from uuid import uuid4

client: WeavelClient = create_client()

user_identifier = "USER IDENTIFIER EXAMPLE"

client.track(user_identifier, "paid", {"amount": "100"})
trace: Trace = client.open_trace(user_identifier, trace_id=str(uuid4())) # -> trace_id

res = "I can assist you with a variety of tasks. I can help answer questions, provide information, give suggestions, assist with research, set reminders, manage your schedule, make reservations, provide translations, and much more. Just let me know what you need help with!"

# print(res.choices[0].message.content)

trace.log_message("assistant", res)

user_message = "How to buy a math textbook?"
trace.log_message("user", user_message)

# res = openai_client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": user_message}
#     ]
# )


# second_trace: Trace = client.open_trace(user_id)
# second_trace.log_message("user", "hello!", unit_name="second_testapp")
# second_trace.log_message("assistant", "I can help you with a variety of tasks.", unit_name="second_testapp")
# second_trace.log_message("system", "you are a helpful assistant.")

client.close()