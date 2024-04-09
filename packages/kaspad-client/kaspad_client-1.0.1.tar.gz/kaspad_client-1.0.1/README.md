This is a simple gRPC client for a python application which communiactes with the Kaspa node called KASPAD.

The module is based on asyncio, since the Kaspa BlockDAG is unbelievable fast and also needs the support of notifications.

# Usage

    import asyncio

    from kaspad_client import KaspadClient
    
    
    async def main():
        kaspad_client = KaspadClient("127.0.0.1", 16110)
        print(await kaspad_client.get_info())
    
    
    asyncio.run(main())


returns

    {'getInfoResponse': {'p2pId': 'd3d2af24-9ddd-4cf8-86eb-d1acd539857a', 'serverVersion': '0.13.4', 'isUtxoIndexed': True, 'isSynced': True, 'hasNotifyCommand': True, 'hasMessageId': True, 'mempoolSize': '0'}, 'id': '0'}

