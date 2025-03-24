from ollama import chat

stream = chat(
    model='medllama2',
    messages=[{'role': 'user', 'content': 'why is the sky blue?'}],
    stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)
# from ollama import chat
# from ollama import ChatResponse

# response: ChatResponse = chat(model='medllama2', messages=[
#   {
#     'role': 'user',
#     'content': 'Why is sky blue?',
#   },
# ])
# print(response['message']['content'])
# # or access fields directly from the response object
# print(response.message.content)