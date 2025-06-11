# import json
# from dashscope.threads import Messages

# msgs = Messages.list(
#     api_key="sk-8448e25c726e45b2ac57fbc1b801aa7d", 
#     thread_id="thread_4543250e-560f-4ae0-a8e7-2d26b37eb674",
#     limit=3,
#     order='desc'
# ).data

# # print(msgs)

# if msgs:
#     # last_msg = msgs[0]
#     for msg in msgs:
#         print(msg.content)
#         # print(msg.content[0].text.value)
# else:
#     print("====")

ddd = {
    "limit": 324
}
print(ddd.get("limit3", 111))