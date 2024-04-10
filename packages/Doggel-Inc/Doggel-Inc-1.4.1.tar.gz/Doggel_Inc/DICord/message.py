from .channel import Channel
from .user import User

class Message:
  def __init__(self, message_data, client):
    self.id = message_data['id']
    self.content = message_data['content']
    self.author = User(message_data['author'], client)
    self.channel = Channel(message_data['channel_id'], client)
  
  async def reply(self, content):
    await self.channel.send(content, reference=self.id)