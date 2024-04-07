from .Utils.formatted_letters import MV_TEXT, MV_CJ

def vijjify(text: str, emoji: str) -> str:
  """
  from MV import vijjify

  s = vijjify("alpha", "❤️")
  print(s)
  """
  to_ret: str = ''
  for x in text.lower():
    if x in MV_TEXT:
      to_ret += MV_CJ[MV_TEXT.index(x)].format(cj=emoji)
  return to_ret
