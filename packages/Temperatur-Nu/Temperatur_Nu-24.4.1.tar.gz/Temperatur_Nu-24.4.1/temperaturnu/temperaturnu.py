import aiohttp
import requests

class TemperaturNu:

    def get_name(self, station):
        url = "http://api.temperatur.nu/tnu_1.17.php?p=" + station + "&cli=popeensPyPi"
        response = requests.get(url)
        data = response.json()
        if len(data) > 0:
            return data['stations'][0]['title']
        else:
            return None

    def get_temp(self, station):
        url = "http://api.temperatur.nu/tnu_1.17.php?p=" + station + "&cli=popeensPyPi"
        response = requests.get(url)
        data = response.json()
        if len(data) > 0:
            return data['stations'][0]['temp']
        else:
            return None

    def set_temp(self, token, temp):
        url="http://www.temperatur.nu/rapportera.php?hash=" + token + "&t=" + str(temp)
        response = requests.get(url)
        body = response.content
        if str("ok!") in str(body):
            return True
        else:
            return False
        
    async def get_name_async(self, station):
        url = "http://api.temperatur.nu/tnu_1.17.php?p=" + station + "&cli=popeensPyPi"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if len(data) > 0:
                    return data['stations'][0]['title']
                else:
                    return None
        
    async def get_temp_async(self, station):
        url = "http://api.temperatur.nu/tnu_1.17.php?p=" + station + "&cli=popeensPyPi"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if len(data) > 0:
                    return data['stations'][0]['temp']
                else:
                    return None
        

    async def set_temp_async(self, token, temp):
        
        url="http://www.temperatur.nu/rapportera.php?hash=" + token + "&t=" + str(temp)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.content
                if str("ok!") in str(body):
                    return True
                else:
                    return False
                