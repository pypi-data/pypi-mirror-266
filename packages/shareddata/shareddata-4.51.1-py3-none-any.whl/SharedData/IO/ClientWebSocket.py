import time
import websockets
import numpy as np
import lz4.frame as lz4f


from SharedData.Logger import Logger
from SharedData.IO.ServerWebSocket import ServerWebSocket
from SharedData.IO.ClientSocket import ClientSocket


class ClientWebSocket():

    @staticmethod
    async def table_subscribe_thread(table, host, port,
                                     lookbacklines=1000, lookbackdate=None, snapshot=False):

        while True:
            try:
                # Connect to the server
                async with websockets.connect(f"ws://{host}:{port}") as websocket:

                    # Send the subscription message
                    msg = ClientSocket.table_subscribe_message(
                        table, lookbacklines, lookbackdate, snapshot)
                    msgb = msg.encode('utf-8')
                    await websocket.send(msgb)

                    # Subscription loop
                    await ClientWebSocket.table_subscription_loop(table, websocket)
                    time.sleep(15)

            except Exception as e:
                msg = 'Retrying subscription %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                     table.source, table.tablename, str(e))
                Logger.log.warning(msg)
                time.sleep(15)

    @staticmethod
    async def table_subscription_loop(table, websocket):
        shnumpy = table.records
        bytes_buffer = bytearray()

        while True:
            try:
                # Receive data from the server
                data = await websocket.recv()
                if data == b'':
                    msg = 'Subscription %s,%s,%s,table,%s closed !' % \
                        (table.database, table.period,
                            table.source, table.tablename)
                    Logger.log.warning(msg)
                    websocket.close()
                else:
                    # Decompress the data                    
                    data = lz4f.decompress(data)
                    bytes_buffer.extend(data)

                    if len(bytes_buffer) >= shnumpy.itemsize:
                        # Determine how many complete records are in the buffer
                        num_records = len(
                            bytes_buffer) // shnumpy.itemsize
                        # Take the first num_records worth of bytes
                        record_data = bytes_buffer[:num_records *
                                                   shnumpy.itemsize]
                        # And remove them from the buffer
                        del bytes_buffer[:num_records *
                                         shnumpy.itemsize]
                        # Convert the bytes to a NumPy array of records
                        rec = np.frombuffer(
                            record_data, dtype=shnumpy.dtype)
                        # Upsert all records at once
                        shnumpy.upsert(rec)

            except Exception as e:
                msg = 'Subscription %s,%s,%s,table,%s error!\n%s' % \
                    (table.database, table.period,
                     table.source, table.tablename, str(e))
                Logger.log.error(msg)
                websocket.close()
                break


if __name__ == '__main__':
    import sys
    from SharedData.Logger import Logger
    from SharedData.SharedData import SharedData
    shdata = SharedData('SharedData.IO.ClientWebSocket', user='master')

    if len(sys.argv) >= 2:
        _argv = sys.argv[1:]
    else:
        msg = 'Please specify IP and port to bind!'
        Logger.log.error(msg)
        raise Exception(msg)

    args = _argv[0].split(',')
    host = args[0]
    port = int(args[1])
    database = args[2]
    period = args[3]
    source = args[4]
    tablename = args[5]
    table = shdata.table(database, period, source, tablename)
    
    table.subscribe(host, port, lookbacklines=1000, method='websocket')
