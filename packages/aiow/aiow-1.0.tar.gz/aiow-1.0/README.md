<div align="center">
<h1>Aiow</h1>
Aiohttp based wrapper
<br/><br/><img src="https://static.pepy.tech/personalized-badge/aiow?period=total&amp;units=none&amp;left_color=black&amp;right_color=blue&amp;left_text=Total Downloads" alt="Downloads">
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
    
    
asyncio.run(my_test())
```
