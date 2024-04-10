class Msg:
  def mes(self, data, prefix):
    msg = data['content']
    executor = msg.split()[0]
    return executor.replace(prefix,"")