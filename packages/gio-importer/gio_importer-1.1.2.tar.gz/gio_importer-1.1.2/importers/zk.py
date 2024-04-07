from kazoo.client import KazooClient

zk = KazooClient(hosts='127.0.0.1')
zk.start()

zk.stop()