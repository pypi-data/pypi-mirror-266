from ..functions.api_request import api_request

async def buy_airtime(phone: str, amount:str):
  api_response = await api_request("POST", "/airtime/buy", "", {"phone": phone, "amount": amount})
  return api_response

async def list_recharges():
  api_response = await api_request("GET", "/airtime/", "", None)
  return api_response