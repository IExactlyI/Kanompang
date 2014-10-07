import tornado.ioloop
import tornado.web
import tornado.websocket as websocket
import socket
import thread
import threading
import json
from protocolHandler import protocolHandler
from deviceHandler import deviceHandler
import signal
import sys

BIND_IP = ''
LISTEN_PORT = 9999
BUFFER_SIZE = 1024
TIMEOUT = 2
MAX_TIMEOUT = 3
MAX_ERROR = 5

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ws_client_list = []
inner_client_list = []
client_on_device = []
client_on_device_sem = threading.Lock()

devHndl = deviceHandler()
devHndl_sem = threading.Lock()
ws_sending_sem = threading.Lock()

'''This routine will occur when user press ctrl+c'''
def signal_handler(signal, frame):
        print('Terminate listener.')
        listener.close()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def updateClient() :
    devHndl_sem.acquire()
    device_list = json.dumps(devHndl.getList())
    devHndl_sem.release()

    ws_sending_sem.acquire()
    for i in range(0, len(ws_client_list)) :
        ws_client_list[i].write_message(device_list)
    ws_sending_sem.release()

def updateClientValue(_id, _value) :
    client_on_device_sem.acquire()
    for i in range(0, len(client_on_device)) :
        if (client_on_device[i][0] == _id) :
            for j in range(0, len(client_on_device[i][1])) :
                client_on_device[i][1][j].write_message('{"Value": ' + str(_value) + '}');
    client_on_device_sem.release()

def WS_ErrMsg(_ws, _msg) :
    _ws.write_message('{"ErrMsg": "' + _msg + '"}')

def createDevice(_id) :
    client_on_device_sem.acquire()
    client_on_device.append([_id, []])
    client_on_device_sem.release()

def removeDevice(_id) :
    client_on_device_sem.acquire()
    for i in range(0, len(client_on_device)) :
        if (client_on_device[i][0] == _id) :
            print "Remove device " + str(_id)

            #Close all websocket connection that depend on this device
            for i in range(0, len(client_on_device[i][1])) :
                WS_ErrMsg(client_on_device[i][1][i], "Device was removed.")
                client_on_device[i][1][i].close()

            del client_on_device[i]
            client_on_device_sem.release()
            return 1
    client_on_device_sem.release()
    return -1

def addClient2Device(_id, _ws) :
    client_on_device_sem.acquire()
    for i in range(0, len(client_on_device)) :
        if (client_on_device[i][0] == _id) :
            client_on_device[i][1].append(_ws)
            client_on_device_sem.release()
            return 1
    client_on_device_sem.release()
    return -1

def removeClientFromDevice(_ws) :
    client_on_device_sem.acquire()
    for i in range(0, len(client_on_device)) :
        print "Remove client from device " + str(client_on_device[i][0])
        try:
            client_on_device[i][1].remove(_ws)
        except ValueError:
            pass
    client_on_device_sem.release()

def TCP_Con(conn, addr) :
    global devHndl
    conn_id = None
    m_id = None
    m_type = None
    m_data = None

    m_timeout = 0
    m_error = 0
    m_buffer = []
    raws_list = []

    protocol = protocolHandler()

    print "New connection from : " , addr
    conn.settimeout(TIMEOUT)

    #Clear m_buffer
    del m_buffer[:]

    #Clear raws_data
    raws_data = ""

    #Clear raws_list
    del raws_list[:]


    print "Waiting for sensor infomation : " , addr
    m_timeout = 0
    m_error = 0
    while True:
        try:
            raws_data = conn.recv(BUFFER_SIZE)

            #socket.recv will return None if connection is closed.
            if (not raws_data) :
                print "Client is closed : ", addr
                conn.close()
                print "Close connection from : " , addr
                return

            #Reset m_timeout
            m_timeout = 0

            #Convert char list to int list
            raws_list = list(raws_data)
            for i in range(0, len(raws_list)) :
                m_buffer.append(ord(raws_list[i]))

            #Process income Data
            rslt = 0
            for i in range(0, len(m_buffer)) :
                rslt = protocol.processData(m_buffer[i])
                if (rslt != 0) :
                    break;

            if (rslt > 0) :
                m_error = 0
                m_id = protocol.getID()
                conn_id = m_id
                m_type = protocol.getType()
                m_data = protocol.getData()
                print "Reegister new device id " + str(m_id) + " : ", addr
                devHndl_sem.acquire()
                devHndl.addDevice(m_id, m_type, m_data)
                devHndl_sem.release()
                break
            elif (rslt < 0) :
                m_error = m_error + 1
                print "Process protocol error #" + str(m_error) + " : ", addr

                if (m_error >= MAX_ERROR) :
                    print "Too many error : ", addr
                    conn.close()
                    print "Close connection from : " , addr
                    return

        except socket.timeout, e:
            m_timeout = m_timeout + 1
            print "Receive Timeout #" + str(m_timeout) + " : ",  addr

            if (m_timeout >= MAX_TIMEOUT) :
                print "Too many timeout : ", addr
                conn.close()
                print "Close connection from : " , addr
                return

        except socket.error, e:
            print "Error [" + e.args[0] + "] : ", addr
            return

    updateClient()
    createDevice(conn_id)
    print "Start retrieve data : ", addr

    #Clear all intermediate variable
    raws_data = ""
    del raws_list[:]
    del m_buffer[:]
    rslt = 0
    while True:
        try:
            raws_data = conn.recv(BUFFER_SIZE)

            #socket.recv will return None if connection is closed.
            if (not raws_data) :
                print "Client is closed : ", addr
                break

            m_timeout = 0

            #Clear m_buffer for prepare to receive new data frame
            del m_buffer[:]
            raws_list = list(raws_data)
            for i in range(0, len(raws_list)) :
                m_buffer.append(ord(raws_list[i]))

            print m_buffer

            #Process income Data
            rslt = 0
            for i in range(0, len(m_buffer)) :
                rslt = protocol.processData(m_buffer[i])
                if (rslt != 0) :
                    break;

            if (rslt > 0) :
                m_error = 0
                m_id = protocol.getID()
                m_type = protocol.getType()
                m_data = protocol.getData()

                devHndl_sem.acquire()
                devHndl.setType(m_id, m_type)
                devHndl.setData(m_id, m_data)
                devHndl_sem.release()

                data_pack = [m_id, m_data]

                updateClientValue(conn_id, m_data)
                print "Income data from id " + str(m_id) + ", Type " + str(m_type) + ", Data " + str(m_data) + " : ", addr

            if (rslt < 0) :
                m_error = m_error + 1
                print "Process protocol error #" + str(m_error) + " : ", addr

                if (m_error >= MAX_ERROR) :
                    print "Too many error : ", addr
                    break

        except socket.timeout, e:
            m_timeout = m_timeout + 1
            print "Receive Timeout #" + str(m_timeout) + " : ", addr
            if (m_timeout >= MAX_TIMEOUT) :
                print "Too many timeout : ", addr
                break

        except socket.error, e:
            print "Error [" + e.args[0] + "] : ", addr
            break
            
    conn.close()
    print "Close connection from : " , addr
    devHndl_sem.acquire()
    devHndl.rmDevice(conn_id)
    devHndl_sem.release()
    updateClient()
    removeDevice(conn_id)

def TCP_Thd () :
    listener.bind((BIND_IP, LISTEN_PORT))
    listener.listen(1)

    while True:
        (conn, addr) = listener.accept()
        thread.start_new_thread(TCP_Con, (conn, addr))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class dwSensorLogger(websocket.WebSocketHandler):
    def open(self):
        global ws_client_list
        ws_client_list.append(self)

        devHndl_sem.acquire()
        self.write_message(json.dumps(devHndl.getList()))
        devHndl_sem.release()
        print "There is income ws connection."

    def on_message(self, message):
        print "Received : " + message

    def on_close(self):
        ws_client_list.remove(self)
        print "WebSocket closed"

class dwSensorInner(websocket.WebSocketHandler):
    def open(self):
        global inner_client_list
        inner_client_list.append(self)
        print "There is income ws connection."

    def on_message(self, message):
        print "Received : " + message

        json_obj = json.loads(message)

        if (json_obj['reqid']) :
            rslt = addClient2Device(json_obj['reqid'], self)
            if (rslt > 0) :
                self.write_message('{"Type": ' + str(devHndl.getType(json_obj['reqid'])) + ',' + \
                                    '"Value": ' + str(devHndl.getData(json_obj['reqid'])) + \
                                   '}');
                print "Add Client to device " + str(json_obj['reqid'])
            else :
                print "There isn't device " + str(json_obj['reqid'])
                WS_ErrMsg(self, "There isn't device " + str(json_obj['reqid']))
                #self.write_message("There isn't device " + str(json_obj['reqid']))
                self.close()

    def on_close(self):
        inner_client_list.remove(self)
        removeClientFromDevice(self)
        print "WebSocket closed"

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/dwlogger", dwSensorLogger),
    (r"/dwinner", dwSensorInner),
])

if __name__ == "__main__":
    thread.start_new_thread(TCP_Thd, ())
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
