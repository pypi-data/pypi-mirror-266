from aiohttp import ClientSession
import asyncio
from ..sensor import Sensor
class Device:
    def __init__(self, chipid: int, token: dict, dispname: str = "" ):
        self.chipid = chipid
        self.dispname = dispname
        self.httpheaders = token
        self.sensores = {}

    async def _async_set_sensores(self):
        url = "https://back-prd.bzutech.com.br/dispositivos/canais-list/" + str(
            self.chipid
        )
        sensores = []
        client = ClientSession()
        
        async with client.get(url, headers = self.httpheaders) as resp:
            resposta = await resp.json()
            await client.close()

            for sensor in resposta:
                if sensor["ultima_medicao_sensor"] != None:
                    sensores.append(
                        Sensor
                        (
                            self.chipid,
                            sensor["sensor_nome"].upper(),
                            sensor["apelido_canal"],
                            self.httpheaders
                        )
                    )
            return sensores

    async def initialize(self):
        self.sensores = await self._async_set_sensores()
        flemis = {}
        for sensor in self.sensores:
            flemis[sensor.apelido] = sensor

        self.sensores = flemis

    def get_sensor_names(self):
        return list(self.sensores.keys())

    def get_sensor_names_on(self, port: str):
        sensores = []
        for sensor in self.get_sensor_names():
            if sensor[-1] == port:
                sensores.append(sensor)
        return sensores
    
    def get_ep_on(self, port:int):
        sensors = self.get_sensor_names_on(str(port))
        for sensor in sensors:
            if "ADS7878" in sensor:
                return "EP400"
            if "RTZSBZ" in sensor:
                return "EP300"
            if "SGP30" in sensor:
                return "EP200"
            if "DOOR" in sensor:
                return "EP121"
            if "SHT30" in sensor:
                return "EP111"
        

    async def get_readings(self, nome_sensor):
        return await self.sensores[nome_sensor].get_leitura()

    def get_chipid(self):
        return self.chipid
