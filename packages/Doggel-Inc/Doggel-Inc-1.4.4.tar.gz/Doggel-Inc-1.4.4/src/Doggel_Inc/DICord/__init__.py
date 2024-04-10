import asyncio
import time
import aiohttp
import logging
import json
import websockets
from .message import Message
from .msg import Msg

class Client:
  def __init__(self, token, prefix=None):
    self.token = token
    self.prefix = prefix
    self.event_handlers = {}
    self.commands = {}
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    self.logger = logger
    self.session = None
    
  async def get_session(self):
    self.session = aiohttp.ClientSession()
    self.logger.info("Aiohttp Session started")

  async def close_session(self):
    await self.session.close()
    self.logger.info("Aiohttp Session stopped")

  def event(self, coro):
    if asyncio.iscoroutinefunction(coro):
      self.event_handlers[coro.__name__] = coro
    else:
      raise TypeError('Event handler must be a coroutine function')
    return coro

  def command(self, coro):
    if asyncio.iscoroutinefunction(coro):
      self.commands[coro.__name__] = coro
    else:
      raise TypeError('Command handler must be a coroutine function')
    return coro

  async def latency(self):
    start_time = time.perf_counter()
    async with self.session.get('https://discord.com/api/v9/gateway', headers={'Authorization': f'Bot {self.token}'}) as response:
      if response.status == 200:
        latency = (time.perf_counter() - start_time) * 1000  
        return latency
      else:
        raise Exception(f"HTTP Error: {response.status}")
    
  async def connect(self):
    while True:
      try:
        self.logger.info("Starting Connection to Discord API")
        async with websockets.connect('wss://gateway.discord.gg/?v=6&encoding=json') as ws:
          await self.identify(ws)
          self.logger.info(f"Connection Successful with latency {await self.latency()} MS")
          async for message in ws:
            await self.handle_message(message)

      except websockets.ConnectionClosed as e:
        self.logger.error(f'Connection closed: {e}')
        await asyncio.sleep(1)
        
      except Exception as e:
        self.logger.error(f'An error occurred: {e}')
        await asyncio.sleep(1)
      self.logger.info("Trying to Establish Connection")
        

  async def identify(self, ws):
    await ws.send(json.dumps({
      'op': 2,
      'd': {
        'token': self.token,
        'intents': 32509,
        'properties': {
          '$os': 'linux',
          '$browser': 'DICord',
          '$device': 'DICord'
        }
      }
    }))

  async def handle_message(self, message):
    event = json.loads(message)
    event_name = event.get('t')
    event_data = event.get('d')
    if event_name == 'MESSAGE_CREATE':
      handler = self.event_handlers.get('on_message')
      msg_obj = Message(event_data, self)
      if handler:
        await handler(msg_obj)
      elif self.prefix and event_data['content'].startswith(self.prefix):
        parts = event_data['content'][len(self.prefix):].split()
        command = parts[0]
        args = parts[1:]          
        msg_obj = Msg(event_data, self)
        handler = self.commands.get(command)
        if handler:
          await handler(msg_obj, *args)

  def start(self):
    asyncio.get_event_loop().run_until_complete(self.get_session())
    asyncio.get_event_loop().run_until_complete(self.connect())
    asyncio.get_event_loop().run_forever()