import aiohttp

apikey = None

def setup(key):
    global apikey
    apikey = key

async def request(user_id, user_name, message):
    
    global apikey
    request_headers = {'Authorization': apikey}
    async with aiohttp.ClientSession() as session:                                     
        api_url = 'https://diai.doggelinc.site/request'
        request_data = {'message': message,'message-author-id': user_id,'message-author-user': user_name,'function': "ai"}
        async with session.post(api_url, json=request_data, headers=request_headers) as response:
            api_response = await response.json()
            return api_response