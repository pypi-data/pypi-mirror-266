from ..functions.api_request import api_request

async def find_by_inviter():    
  api_response = await api_request("GET", "/invitation/find-by-inviter", "", None)
  return api_response

async def create_inivitation(country: str, phone: str, amount: str):
  api_response = await api_request("POST", "/invitation/create", "", {"country": country,"phone": phone,"amount": amount})
  return api_response