import requests

class TemperaturNu:

    async def get_temp(self, station):
        url = "http://api.temperatur.nu/tnu_1.17.php?p=" + station + "&cli=popeensPyPi"
        async with session.get(url) as resp:
            data = await resp.json()
            if len(data) > 0:
                return data['stations'][0]['temp']
            else:
                return None

    async def set_temp(self, token, temp):
        
        url="http://www.temperatur.nu/rapportera.php?hash=" + token + "&t=" + str(temp)
        async with session.get(url) as resp:
            body = await resp.content
            if str("ok!") in str(body):
                return True
            else:
                return False