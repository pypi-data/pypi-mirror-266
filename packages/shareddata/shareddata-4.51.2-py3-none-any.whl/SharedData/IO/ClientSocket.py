import time
import sys
import socket
import numpy as np
import pandas as pd
import json
import os
from cryptography.fernet import Fernet
import lz4.frame as lz4f
import struct

from SharedData.Logger import Logger
from SharedData.IO.ServerSocket import ServerSocket


class ClientSocket():
    @staticmethod
    def table_subscribe_thread(table, host, port, 
        lookbacklines=1000, lookbackdate=None, snapshot=False):
        
        while True:
            try:
                # Connect to the server
                client_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((host, port))

                # Send the subscription message
                msg = ClientSocket.table_subscribe_message(
                    table, lookbacklines, lookbackdate, snapshot)
                msgb = msg.encode('utf-8')
                bytes_sent = client_socket.send(msgb)

                # Subscription loop
                ClientSocket.table_subscription_loop(table, client_socket)
                time.sleep(15)

            except Exception as e:
                msg = 'Retrying subscription %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                     table.source, table.tablename, str(e))
                Logger.log.warning(msg)
                time.sleep(15)

    @staticmethod
    def table_subscribe_message(table, lookbacklines, lookbackdate, snapshot):
        shnumpy = table.records        
                
        key = os.environ['SHAREDDATA_SECRET_KEY'].encode()        
        cipher_suite = Fernet(key)
        cipher_token = cipher_suite.encrypt(os.environ['SHAREDDATA_SOCKET_TOKEN'].encode())
        msg = {
            'token': cipher_token.decode(),
            'action': 'subscribe',
            'database': table.database,
            'period': table.period,
            'source': table.source,
            'container': 'table',
            'tablename': table.tablename,
            'count': int(shnumpy.count),
            'mtime': float(shnumpy.mtime),
            'lookbacklines': lookbacklines
        }                    
        if isinstance(lookbackdate, pd.Timestamp):            
            msg['lookbackdate'] = lookbackdate.strftime('%Y-%m-%d')
        if snapshot:
            msg['snapshot'] = True
        msg = json.dumps(msg)
        return msg

    @staticmethod
    def table_subscription_loop(table, client_socket):
        shnumpy = table.records        
        bytes_buffer = bytearray()
        
        while True:
            try:
                # Receive data from the server
                data = client_socket.recv(4)                
                if data == b'':
                    msg = 'Subscription %s,%s,%s,table,%s closed !' % \
                        (table.database, table.period,
                            table.source, table.tablename)
                    Logger.log.warning(msg)
                    client_socket.close()
                else:  
                    length = struct.unpack('!I', data)[0]
                    
                    compressed = b''
                    while len(compressed) < length:
                        chunk = client_socket.recv(length - len(compressed))
                        if chunk == b'':
                            msg = 'Subscription %s,%s,%s,table,%s closed !' % \
                                (table.database, table.period,
                                    table.source, table.tablename)
                            Logger.log.warning(msg)
                            client_socket.close()
                            raise Exception(msg)
                        compressed += chunk

                    data = lz4f.decompress(compressed)
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
                client_socket.close()                
                break


if __name__ == '__main__':
    import sys
    from SharedData.Logger import Logger
    from SharedData.SharedData import SharedData
    shdata = SharedData('SharedData.IO.ClientSocket', user='master')

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

    table = shdata.table(database,period,source,tablename)
    table.subscribe(host,port,lookbacklines=1000,snapshot=True)