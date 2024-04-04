import requests
import aiohttp
from trufflepig._constants import SERVER_ADDRESS

def _get_instance_id(instance_name: str, api_key: str):
    response = requests.get(
        f'http://{SERVER_ADDRESS}/v0/instances/name',
        headers={'x-api-key': api_key},
        params={'instance_name': instance_name}
    )

    if response.status_code == 200:
        result = response.json()
        return result['instance_id']
    elif response.status_code == 500:
        return None
    else:
        raise Exception(f'{response.status_code} Error: {response.text}')
        
async def _get_instance_id_async(instance_name: str, api_key: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://{SERVER_ADDRESS}/v0/instances/name',
                            headers={ 'x-api-key': api_key },
                            params={ 'instance_name': instance_name }) as response:
            if response.status == 200:
                result = await response.json()
                return result['instance_id']
            elif response.status == 500:
                return None
            else:
                raise Exception(f'{response.status} Error: {await response.text()}')