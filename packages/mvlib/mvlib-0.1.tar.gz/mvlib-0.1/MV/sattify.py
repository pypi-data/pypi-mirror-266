from .Utils.formatted_letters import MV_TEXT, MV_EMOJI

def sattify(text: str) -> str:
  """
  from MV import sattify
  
  v = sattify("alpha")
  print(v)
  """
  to_ret: str = ''
  for x in text.lower():
    if x in MV_TEXT:
      to_ret += MV_EMOJI[MV_TEXT.index(x)]
  return to_ret
