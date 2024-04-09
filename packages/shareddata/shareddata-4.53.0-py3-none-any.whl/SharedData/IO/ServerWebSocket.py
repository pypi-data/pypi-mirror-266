
import time
import sys
import time
import select
import numpy as np
import pandas as pd
import asyncio
import websockets
import json
import os
from cryptography.fernet import Fernet
import lz4.frame as lz4f
import struct

# TODO: DONT SERVE DATA IF TABLE IS NOT IN MEMORY


class ServerWebSocket():

    BUFF_SIZE = 65536
    RATE_LIMIT = 1e6  # 1MB/s
    # Dict to keep track of all connected client sockets
    clients = {}
    # Create a lock to protect access to the clients Dict
    lock = asyncio.Lock()

    server = None
    shdata = None
    accept_clients = None

    @staticmethod
    async def runserver(shdata, host, port):

        Logger.log.info(f'Listening on {host}:{port}')

        ServerWebSocket.shdata = shdata

        ServerWebSocket.server = await websockets.serve(ServerWebSocket.handle_client_thread, host, port)

        await ServerWebSocket.server.wait_closed()

    @staticmethod
    async def handle_client_thread(conn, path):
        addr = conn.remote_address
        Logger.log.info(f"New client connected: {addr}")
        # conn.settimeout(60.0)

        # Add the client socket to the list of connected clients
        async with ServerWebSocket.lock:
            ServerWebSocket.clients[conn] = {
                'watchdog': time.time_ns(),
                'transfer_rate': 0.0,
            }

        client = ServerWebSocket.clients[conn]
        client['conn'] = conn
        client['addr'] = addr

        try:
            await ServerWebSocket.handle_client_websocket(client)
        except Exception as e:
            Logger.log.error(f"Client {addr} disconnected with error: {e}")
        finally:
            async with ServerWebSocket.lock:
                ServerWebSocket.clients.pop(conn)
            Logger.log.info(f"Client {addr} disconnected.")
            conn.close()

    @staticmethod
    async def handle_client_websocket(client):

        client['authenticated'] = False
        conn = client['conn']

        # Receive data from the client
        data = await conn.recv()
        if data:
            # clear watchdog
            client['watchdog'] = time.time_ns()
            data = data.decode()
            login_msg = json.loads(data)
            # authenticate
            key = os.environ['SHAREDDATA_SECRET_KEY'].encode()
            token = os.environ['SHAREDDATA_SOCKET_TOKEN']
            cipher_suite = Fernet(key)
            received_token = cipher_suite.decrypt(login_msg['token'].encode())
            if received_token.decode() != token:
                errmsg = 'Client %s authentication failed!' % (
                    client['addr'][0])
                Logger.log.error(errmsg)
                raise Exception(errmsg)
            else:
                client['authenticated'] = True
                Logger.log.info('Client %s authenticated' %
                                (client['addr'][0]))

                client.update(login_msg)
                if client['action'] == 'subscribe':
                    if client['container'] == 'table':
                        await ServerWebSocket.send_table_updates(client)
                elif client['action'] == 'update':
                    if client['container'] == 'table':
                        await ServerWebSocket.receive_table_updates(client)

    @staticmethod
    async def send_table_updates(client):
        conn = client['conn']
        addr = client['addr']

        Logger.log.info('Serving updates of %s/%s/%s/%s -> %s' %
                        (client['database'], client['period'],
                         client['source'], client['tablename'], addr[0]))

        client['table'] = ServerWebSocket.shdata.table(
            client['database'], client['period'],
            client['source'], client['tablename'])
        table = client['table']

        timestamp = float(client['mtime'])
        datetime_ns = np.datetime64(int(timestamp), 's')
        datetime_ns += np.timedelta64(int((timestamp % 1)*1e9), 'ns')
        client['mtime'] = datetime_ns

        client['maxrows'] = int(
            np.floor(ServerWebSocket.BUFF_SIZE/table.itemsize))
        lookbacklines = int(client['lookbacklines'])
        lookbackfromid = None
        if 'lookbackdate' in client:
            lookbackfromdate = pd.Timestamp(client['lookbackdate'])
            lookbackfromid, _ = table.get_date_loc(lookbackfromdate)
            if lookbackfromid == -1:
                lookbackfromid = table.count
        snapshot = False
        if 'snapshot' in client:
            snapshot = client['snapshot']

        transfer_rate = 0
        maxrows = client['maxrows']

        while True:
            try:
                ids2send = []

                if lookbackfromid is not None:
                    lookbackid = lookbackfromid
                else:
                    lookbackid = table.count-lookbacklines
                if lookbackid < 0:
                    lookbackid = 0

                if len(table[lookbackid:])>0:
                    maxtime = max(table[lookbackid:]['mtime'])
                    updtidx = table[lookbackid:]['mtime'] >= client['mtime']
                    if updtidx.any():
                        updtids = np.where(updtidx)
                        if len(updtids) > 0:
                            ids2send.extend(updtids[0]+lookbackid)
                            client['mtime'] = maxtime

                lastcount = client['count']
                if snapshot:
                    snapshot = False
                    lastcount = lookbackid

                curcount = table.count.copy()
                if curcount > lastcount:
                    newids = np.arange(lastcount, curcount)
                    ids2send.extend(newids)
                    client['count'] = curcount

                if len(ids2send) > 0:
                    ids2send = np.unique(ids2send)
                    ids2send = np.sort(ids2send)

                    rows2send = len(ids2send)
                    sentrows = 0
                    tini = time.time_ns()
                    while sentrows < rows2send:
                        msgsize = min(maxrows, rows2send)
                        t = time.time_ns()
                        message = table[ids2send[sentrows:sentrows +
                                                 msgsize]].tobytes()
                        compressed = lz4f.compress(message)
                        msgbytes = len(compressed)
                        # msgbytes = msgsize*table.itemsize
                        msgmintime = msgbytes/ServerWebSocket.RATE_LIMIT
                        length = struct.pack('!I', len(compressed))
                        # await conn.sendall(length)
                        conn.send(compressed)
                        sentrows += msgsize
                        msgtime = (time.time_ns()-t)*1e-9
                        ratelimtime = max(msgmintime-msgtime, 0)
                        if ratelimtime > 0:
                            await asyncio.sleep(ratelimtime)

                    totalsize = (sentrows*table.itemsize)/1e6
                    totaltime = (time.time_ns()-tini)*1e-9
                    if totaltime > 0:
                        transfer_rate = totalsize/totaltime
                    else:
                        transfer_rate = 0
                    client['transfer_rate'] = transfer_rate

                # clear watchdog
                client['watchdog'] = time.time_ns()
                await asyncio.sleep(0.001)
            except Exception as e:
                Logger.log.error(
                    'Client %s disconnected with error:%s' % (addr, e))
                time.sleep(5)
                break

    @staticmethod
    async def receive_table_updates(client):
        
        shdata = ServerWebSocket.shdata

        table = shdata.table(client['database'], client['period'],
                             client['source'], client['tablename'])
        shnumpy = table.records
        bytes_buffer = bytearray()

        websocket = client['conn']
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
    
async def send_heartbeat():
    while True:
        n = 0
        sendheartbeat = True
        # Create a list of keys before entering the loop
        client_keys = list(ServerWebSocket.clients.keys())
        for client_key in client_keys:
            n = n+1
            c = ServerWebSocket.clients.get(client_key)
            if c is not None:
                if 'table' in c:
                    table = c['table'].table
                    tf = c['transfer_rate']
                    Logger.log.debug('#heartbeat#%.2fMB/s,%i:%s,%s' %
                                     (tf, n, client_key.remote_address, table.relpath))
                else:
                    Logger.log.debug('#heartbeat# %i:%s' %
                                     (n, client_key.remote_address))
                sendheartbeat = False
        if sendheartbeat:
            Logger.log.debug('#heartbeat#host:%s,port:%i' % (host, port))
        await asyncio.sleep(15)


async def main():
    await asyncio.gather(
        ServerWebSocket.runserver(shdata, host, port),
        send_heartbeat()
    )

if __name__ == '__main__':

    from SharedData.Logger import Logger
    from SharedData.SharedData import SharedData
    shdata = SharedData('SharedData.IO.ServerWebSocket', user='master')
    ServerWebSocket.shdata = shdata 
    
    if len(sys.argv) >= 2:
        _argv = sys.argv[1:]
    else:
        msg = 'Please specify IP and port to bind!'
        Logger.log.error(msg)
        raise Exception(msg)

    args = _argv[0].split(',')
    host = args[0]
    port = int(args[1])

    Logger.log.info('ROUTINE STARTED!')
    
    asyncio.run(main())
