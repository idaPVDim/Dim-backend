

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idav.settings')
django.setup()

# Application Django standard pour HTTP
django_application = get_asgi_application()

# Pour les WebSockets (si vous en avez besoin)
async def application(scope, receive, send):
    if scope['type'] == 'http':
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        # Ici vous pouvez ajouter la gestion des WebSockets
        # Pour l'instant, on rejette les connexions WebSocket
        await send({
            'type': 'websocket.close',
            'code': 1000
        })
    else:
        raise NotImplementedError(f"Unknown scope type: {scope['type']}")