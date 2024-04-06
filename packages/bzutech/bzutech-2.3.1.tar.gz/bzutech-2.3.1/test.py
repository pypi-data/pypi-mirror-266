from bzutech import BzuTech
import asyncio

bzu = BzuTech("admin@email.com", "bzutech123")
asyncio.run(bzu.start())
print(bzu.get_sensors_on("29949", "1"))
print(bzu.get_endpoint_on("29949", 1))
