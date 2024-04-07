import argparse
import json
import websocket
import time
import signal


class QianluService(object):
    def __init__(self):
        super(QianluService, self).__init__()
        self.ws = None
        self.isRun = True
        self.parser = argparse.ArgumentParser(description="cv")
        self.parser.add_argument('-a', '--appdata', type=str, default='default', help='用户数据路径')
        self.parser.add_argument('-i', '--id', type=str, default='local_cv', help='id')
        self.services = {}
        self.onMessageFunction = None

    def register(self, key, service, force=False):
        if key not in self.services or force:
            self.services[key] = service
        else:
            print("service has register")

    def unregister(self, key):
        if key in self.services.keys():
            del self.services[key]

    def onMsg(self, func):
        self.onMessageFunction = func

    def clearMsg(self):
        self.onMessageFunction = None

    def on_message(self, client, message):
        msg = json.loads(message)
        dataObj = {}
        try:
            dataObj = json.loads(msg["data"])
        except ValueError as e:
            pass

        print("on_message：%s" % msg)
        to = msg['to']
        msg['to'] = msg['from']
        msg['from'] = to
        if len(dataObj) > 0:
            if "serviceID" in dataObj and 'functionName' in dataObj and dataObj['serviceID'] == "onMsg":
                try:
                    if self.onMessageFunction is not None:
                        result = self.onMessageFunction(dataObj['functionName'], dataObj['args'])
                        msg['data'] = json.dumps(result)
                        client.send(json.dumps(msg))
                        return
                    else:
                        msg['data'] = json.dumps({"code": -3002, "msg": "功能未发现", "data": ""})
                        client.send(json.dumps(msg))
                        return
                except ValueError as e:
                    msg['data'] = json.dumps({"code": -3005, "msg": "执行功能异常", "data": ""})
                    client.send(json.dumps(msg))
                    return
            if "serviceID" in dataObj and dataObj['serviceID'] in self.services:
                try:
                    method = getattr(self.services[dataObj["serviceID"]], dataObj["functionName"])
                    init = getattr(self.services[dataObj["serviceID"]], "init")
                    if init is not None and "config" in dataObj:
                        init(dataObj['config'])

                    if method is not None:
                        result = method(dataObj['args'])
                        msg['data'] = json.dumps(result)
                        client.send(json.dumps(msg))
                        return
                    else:
                        msg['data'] = json.dumps({"code": -3002, "msg": "功能未发现", "data": ""})
                        client.send(json.dumps(msg))
                        return
                except ValueError as e:
                    msg['data'] = json.dumps({"code": -3003, "msg": "执行异常", "data": ""})
                    client.send(json.dumps(msg))
                    return
            else:
                msg['data'] = json.dumps({"code": -3001, "msg": "服务未发现", "data": ""})
                client.send(json.dumps(msg))
                return

    def on_error(self, ws, error):
        print("####### on_error #######")
        print("error：%s" % error)

    def on_close(self, ws, close_status_code, close_msg):
        print("####### on_close #######")

    def on_open(self, ws):
        print("####### on_open #######")

    def getParser(self):
        return self.parser

    def init(self):
        self.args = self.parser.parse_args()
        self.url = f"ws://localhost:61601?id={self.args.id}"

    def run(self):

        def close(signum, frame):
            print("close")
            self.isRun = False
            self.ws.close()

        signal.signal(signal.SIGTERM, close)
        signal.signal(signal.SIGINT, close)

        websocket.enableTrace(True)

        while self.isRun:
            try:
                print("run_forever")
                self.ws = websocket.WebSocketApp(self.url,
                                                 on_open=self.on_open,
                                                 on_message=self.on_message,
                                                 on_error=self.on_error,
                                                 on_close=self.on_close)
                self.ws.run_forever(ping_interval=3)
            except Exception as e:
                print(f"error：{e}")
            time.sleep(3)
