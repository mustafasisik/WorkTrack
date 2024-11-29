from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            self.close()
            return
            
        self.accept()
        
        # Create a unique group name for this user
        self.group_name = f"notifications_{self.user.id}"

        # Add this connection to the user's group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        print(f"Connected to group {self.group_name}")

    def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name
            )

    def receive(self, text_data):
        print(text_data)

    def send_notification(self, event):
        # Send notification to WebSocket
        self.send(text_data=json.dumps(event["notification"]))

    