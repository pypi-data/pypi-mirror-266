<div align="center">
<h1>Aiow</h1>
<p>Aiohttp based wrapper</p>
</div>


<h2>Installation:</h2>

```bash
python3 -m pip install aiow
```

<h2>Examples:</h2>

```python
import asyncio
from aiow import Aiow

async def my_test():
    # Post(url, args)
    await Aiow.Post('https://google.com', asjson=False)
    # Get(url, args)
    await Aiow.Get('https://google.com', asjson=False)
#Run
asyncio.run(my_test())
```
