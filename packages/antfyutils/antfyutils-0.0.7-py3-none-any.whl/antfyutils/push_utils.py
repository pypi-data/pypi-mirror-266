from asyncio import AbstractEventLoop, AbstractEventLoopPolicy, Task
import asyncio
from collections import deque
import logging
from queue import LifoQueue
from threading import Thread
import threading
from typing import Deque, Set

import aiohttp
from .data_obj import CfgDcNtfy, SendNtfyMessage
from .format import seconds_to_time, 秒转时间


class PushUtils:
    cfg: CfgDcNtfy
    pool: asyncio.Queue
    thread: Thread
    eventloop: AbstractEventLoop
    cn: bool
    info: bool
    # lock: threading.RLock
    def __init__(self, cfg: CfgDcNtfy, queue_size=30, cn=False, info=True) -> None:
        self.cfg = cfg
        self.pool = asyncio.Queue(maxsize=queue_size)
        self.thread = None
        self.cn = cn
        self.info = info
        self.eventloop = asyncio.new_event_loop()
        pass
    async def __run_loop(self):
        asyncio.set_event_loop(self.eventloop)
        s = set()
        while True:
            msg = await self.pool.get()
            if not msg:
                return
            while msg:
                s.add(asyncio.create_task(self.__push(msg)))
                if self.pool.empty():
                    break
                msg = self.pool.get_nowait()
            await asyncio.gather(*s)
            await asyncio.sleep(0.1)
        pass
    def __run_thread(self):
        self.eventloop.run_until_complete(self.__run_loop())
        pass
    def startServer(self):
        self.thread = Thread(name="Push Thread", target=self.__run_thread)
        self.thread.start()
        pass
    def stopServer(self):
        if self.thread:
            self.pool.put_nowait(None)
            self.eventloop.stop()
            self.thread.join(timeout=5)
        pass
    def push(self, msg:SendNtfyMessage):
        def put():
            self.pool.put_nowait(msg)
        self.eventloop.call_soon_threadsafe(put)
    async def __push(self, msg: SendNtfyMessage):
        if not msg.topic:
            msg.topic = self.cfg.topic
        count = 0
        while True:
            count += 1
            if count >=3:
                return
            async with aiohttp.ClientSession(headers={'User-Agent': 'antfyutils/1.0 aiohttp python', "Authorization": f"Bearer {self.cfg.token}"}) as session:
                try:
                    async with session.post(f"{self.cfg.url}", json=msg.to_dict()) as req:
                        ret =await req.read()
                        if ret:
                            logging.debug(ret.decode())
                        if self.cn:
                            if self.info:
                                logging.info(f"消息推送成功！{msg.to_json(ensure_ascii=False)}")
                            else:
                                logging.debug(f"消息推送成功！{msg.to_json(ensure_ascii=False)}")

                        else:
                            if self.info:
                                logging.info(f"Message push success! {msg.to_json(ensure_ascii=False)}")
                            else:
                                logging.debug(f"Message push success! {msg.to_json(ensure_ascii=False)}")
                        pass
                    break
                except aiohttp.ClientConnectorError as e:
                    logging.exception(e)
                    wait = count * 10
                    if self.cn:
                        logging.error(f"推送失败！尝试重新推送,{秒转时间(wait)}秒后再试。")
                    else:
                        logging.error(f"Push failed! Attempting to push again. Retry after {seconds_to_time(wait)}.")
                    await asyncio.sleep(wait)
                    pass
    pass