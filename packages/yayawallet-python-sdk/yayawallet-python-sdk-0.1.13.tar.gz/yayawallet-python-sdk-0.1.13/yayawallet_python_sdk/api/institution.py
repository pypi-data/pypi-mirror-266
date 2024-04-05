from ..functions.api_request import api_request

async def list_institution(country: str):
  api_response = await api_request("POST", "/financial-institution/list", "", {"country": country})
  return api_response