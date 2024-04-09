from .channel import Channel
from .message import Message
from .user import User

class Msg:
  def __init__(self, message_data, client):
    self.id = message_data['id']
    self.message = Message(message_data, client)
    self.author = User(message_data['author'], client)
    self.channel = Channel(message_data['channel_id'], client)
    
  async def send(self, content):
    await self.channel.send(content)

  async def reply(self, content):
    await self.channel.send(content, reference=self.id)