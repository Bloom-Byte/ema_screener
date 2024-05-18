from channels.generic.websocket import AsyncJsonWebsocketConsumer



class EMARecordEventsConsumer(AsyncJsonWebsocketConsumer):
    """Websocket consumer for EMA record events"""
    channel_layer_alias = 'default'
      
    async def connect(self):
        self.group_name = 'ema_record_updates'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


    async def receive_json(self, content, **kwargs):
        await self.send_json(content=content)
    

    async def send_ema_record_update(self, event):
        await self.send_json(content=event['data'])



ema_records_events_consumer = EMARecordEventsConsumer.as_asgi()
