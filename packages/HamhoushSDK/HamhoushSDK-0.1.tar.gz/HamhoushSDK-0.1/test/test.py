from Hamhoush import ApiClient

api_client = ApiClient()
api_client.login("Hamhoush1@gmail.com", "Hamhoush@123")
response = api_client.chat(bot_id="65df0ebe2891bf64b970ceca",message="سلام")
print("Chat response:", response)

history = api_client.bots()
print("Chat history:", history)