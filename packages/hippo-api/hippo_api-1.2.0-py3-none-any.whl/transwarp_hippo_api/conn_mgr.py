import random
import threading
import time
from enum import Enum

import requests
from typing import List


class ConnState(Enum):
    NO_CHECK_YET = 0
    ACTIVE = 1
    FAILED = 2


def check_hippo_host_port_alive(hp: str) -> bool:
    resp = None
    try:
        url = f"http://{hp}"
        resp = requests.get(url)
    except BaseException as e:
        return False
    if resp is not None:
        return True
    else:
        return False


class ConnManager:
    def check_all_url(self):
        with self.lock:
            all_host_ports = list(self.conns)
        for hp in all_host_ports:
            if check_hippo_host_port_alive(hp):
                self.mark_conn_state(hp, ConnState.ACTIVE)
            else:
                self.mark_conn_state(hp, ConnState.FAILED)

    def background_period_check(self):
        while True:
            try:
                self.check_all_url()
                time.sleep(self.check_period)
            except BaseException as e:
                pass

    def __init__(self, check_period: int = 6):
        self.lock = threading.Lock()
        self.conns = {}
        self.check_period = check_period
        self.bgr_thread = threading.Thread(target=self.background_period_check)
        self.bgr_thread.name = "ConnMgr Background Check Thread"
        self.bgr_thread.daemon = True
        self.bgr_thread.start()

    def add_conn(self, url: str, with_state: ConnState = ConnState.NO_CHECK_YET):
        with self.lock:
            if url not in self.conns:
                self.conns[url] = with_state

    def mark_conn_state(self, url: str, st: ConnState):
        with self.lock:
            self.conns[url] = st

    def get_available_conns(self) -> List[str]:
        with self.lock:
            return [u for u, s in self.conns.items() if s == ConnState.ACTIVE or s == ConnState.NO_CHECK_YET]

    def get_available_conn_from_view(self, view: List[str]) -> str:
        ret = []
        with self.lock:
            for u in view:
                if u in self.conns and self.conns[u] == ConnState.ACTIVE or self.conns[u] == ConnState.NO_CHECK_YET:
                    ret.append(u)
        if len(ret) > 0:
            random.shuffle(ret)
            return ret[0]
        else:
            raise ValueError(f"Can not connect with hippo {view}.")


globalConnManager = ConnManager()

if __name__ == "__main__":
    test_cm = ConnManager(2)
    test_cm.add_conn("http://tw-node45:9500")
    test_cm.add_conn("http://tw-node46:9500")
    print(test_cm.get_avaiable_url())

    for i in range(10):
        time.sleep(1)
        print(test_cm.get_avaiable_url())
