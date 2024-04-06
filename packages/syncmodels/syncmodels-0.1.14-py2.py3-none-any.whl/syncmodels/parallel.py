import asyncio
import os
import pickle
import random
import sys
import traceback
import yaml

# ---------------------------------------------------------
# concurrent data gathering
import concurrent.futures
import threading
import multiprocessing
import queue
import time

# ---------------------------------------------------------


from .helpers import expandpath
from .syncmodels import SyncModel

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------
from agptools.containers import walk, myassign
from agptools.logs import logger
from agptools.progress import Progress

log = logger(__name__)


def nop(*args, **kw):
    pass


async def anop(*args, **kw):
    pass


class Parallel:
    def __init__(self, num_threads=3, dispatch=None):
        self.num_threads = num_threads
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self._wip = []
        self.show_stats = True
        self.dispatch = dispatch or nop

        self.workers = []
        self.pool = None

    def bootstrap(self):
        self.pool = multiprocessing.Pool(processes=self.num_threads)

    def _create_executor_pool(self):
        if True:
            self.workers = [
                threading.Thread(target=self.worker) for _ in range(self.num_threads)
            ]

            for worker in self.workers:
                worker.start()

        else:
            self.worker = multiprocessing.Pool(processes=self.num_threads)

    def _stop_executor_pool(self):
        # Add sentinel values to signal worker threads to exit
        for _ in range(self.num_threads):
            self.task_queue.put(None)

        # Wait for all worker threads to complete
        for worker in self.workers:
            worker.join()

    def run(self):
        self.t0 = time.time()
        self.elapsed = 0.0

        # Create a thread pool with a specified number of threads
        self._create_executor_pool()
        # Start worker threads

        # wait until all work is done
        shows = 0
        while remain := self.remain_tasks():
            try:
                result = self.result_queue.get(timeout=1)
                self.dispatch(*result)
            except queue.Empty as why:
                foo = 1

            shows -= 1
            if self.show_stats and shows <= 0:
                log.warning(f"remain tasks: {remain} : {self.num_threads} threads")
                shows = 50
            # time.sleep(0.25)
            self.elapsed = time.time() - self.t0

        self._stop_executor_pool()

    def add_task(self, func, *args, **kw):
        self.task_queue.put_nowait((func, args, kw))

    def remain_tasks(self):
        return (
            len(self._wip) + len(self.task_queue.queue) + len(self.result_queue.queue)
        )

    def worker(self):
        while True:
            try:
                # Get a task from the queue
                task = self.task_queue.get(block=True, timeout=1)
                if task is None:
                    break  # Break the loop
                self._wip.append(1)
                func, args, kwargs = task
                # print(f">> Processing task: {func}")
                result = func(*args, **kwargs)
                item = task, result
                self.result_queue.put(item)
                self._wip.pop()
                # print(f"<< Processing task: {func}")
            except queue.Empty:
                pass


class AsyncParallel:
    def __init__(self, num_threads=3, dispatch=None):
        self.num_threads = num_threads
        self.task_queue = asyncio.queues.Queue()
        self.result_queue = asyncio.queues.Queue()
        self._wip = []
        self.show_stats = True
        self.dispatch = dispatch or anop

        self.workers = []  # tasks
        # self.pool = None
        self.loop = None

    def bootstrap(self):
        "Provide the initial tasks to ignite the process"
        # self.pool = multiprocessing.Pool(processes=self.num_threads)

    async def _create_executor_pool(self):

        self.workers = [
            self.loop.create_task(self.worker(), name=f"worker-{n}")
            for n in range(self.num_threads)
        ]

    async def _stop_executor_pool(self):
        # Add sentinel values to signal worker threads to exit
        for _ in range(self.num_threads):
            self.task_queue.put_nowait(None)

        # Wait for all worker threads to complete
        # for worker in self.workers:
        # worker.join()

    async def run(self):
        self.t0 = time.time()
        self.elapsed = 0.0
        self.loop = asyncio.get_running_loop()

        # Create a worker pool with a specified number of 'fibers'
        await self._create_executor_pool()

        # wait until all work is done
        last = 0
        while remain := self.remain_tasks():
            try:
                # result = await asyncio.wait_for(self.result_queue.get(), timeout=2)
                result = await self.result_queue.get()
                await self.dispatch(*result)
            except queue.Empty as why:
                foo = 1
            except asyncio.exceptions.TimeoutError as why:
                foo = 1

            t1 = time.time()
            self.elapsed = t1 - self.t0
            # print("foo")
            if self.show_stats and t1 - last > 10:
                log.info(f"remain tasks: {remain} : {self.num_threads} fibers")
                last = t1
            # time.sleep(0.25)

        await self._stop_executor_pool()

    def add_task(self, func, *args, **kw):
        self.task_queue.put_nowait((func, args, kw))

    def remain_tasks(self):
        return len(self._wip) + self.task_queue.qsize() + self.result_queue.qsize()

    async def worker(self):
        while True:
            try:
                # Get a task from the queue
                while remaining := self.remain_tasks() < 1000:
                    print(f"Pause worker due too much remainin task: {remaining}")
                    await asyncio.sleep(1)
                    foo = 1
                task = await asyncio.wait_for(self.task_queue.get(), timeout=2)
                if task is None:
                    break  # Break the loop
                self._wip.append(1)
                func, args, kwargs = task
                # print(f">> Processing task: {args}: {kwargs}")
                result = await func(*args, **kwargs)
                item = task, result
                self.result_queue.put_nowait(item)
                self._wip.pop()
                # print(f"<< Processing task: {func}")
            except queue.Empty:
                foo = 1
            except asyncio.exceptions.TimeoutError as why:
                foo = 1
            except Exception as why:
                log.error(why)
                log.error("".join(traceback.format_exception(*sys.exc_info())))
                foo = 1
                print(tb)
                foo = 1


class iCrawler:
    "Interface for a crawler"

    def __init__(self, config_path=None):
        self.progress = Progress()
        self.task_queue = asyncio.queues.Queue()
        self.result_queue = asyncio.queues.Queue()
        self._wip = []

        if not config_path:
            config_path = "config.yaml"
        config_path = expandpath(config_path)
        self.root = os.path.dirname(config_path)
        self.stats_path = os.path.join(self.root, "stats.yaml")

        if not config_path:
            config_path = "config.yaml"
        config_path = expandpath(config_path)

        try:
            with open(config_path, "rt", encoding="utf-8") as f:
                self.cfg = yaml.load(f, Loader=yaml.Loader)
        except Exception:
            self.cfg = {}

    def _bootstrap(self):
        "Provide the initial tasks to ignite the process"

    async def bootstrap(self):
        "Add the initial tasks to be executed by crawler"
        for func, args, kwargs in self._bootstrap():
            self.add_task(func, *args, **kwargs)

    def add_task(self, func, *args, **kw):
        "add a new pending task to be executed by crawler"
        self.task_queue.put_nowait((func, args, kw))

    def remain_tasks(self):
        "compute how many pending tasks still remains"
        return len(self._wip) + self.task_queue.qsize() + self.result_queue.qsize()

    async def dispatch(self, *args, **kw):
        "do nothing"
        pass


class AsyncCrawler(iCrawler):
    """A crawler that uses asyncio"""

    MAPPERS = {}
    RESTRUCT_DATA = {}
    RETAG_DATA = {}
    REFERENCE_MATCHES = []
    KINDS_UID = {}

    def __init__(self, syncmodel: SyncModel, fibers=3):
        super().__init__()
        self.syncmodel = syncmodel
        self.fibers = fibers
        self.show_stats = True
        self.workers = []  # tasks
        self.loop = None

    async def _create_pool(self):
        self.workers = [
            self.loop.create_task(self.worker(), name=f"worker-{n}")
            for n in range(self.fibers)
        ]

    async def _stop_pool(self):
        # Add sentinel values to signal worker threads to exit
        for _ in range(self.fibers):
            self.task_queue.put_nowait(None)

        # Wait for all worker threads to complete
        # for worker in self.workers:
        # worker.join()

    async def run(self):
        """Execute a full crawling loop"""
        self.loop = asyncio.get_running_loop()

        # Create a worker pool with a specified number of 'fibers'
        await self._create_pool()

        await self.bootstrap()

        # wait until all work is done
        while remain := self.remain_tasks():
            try:
                # result = await asyncio.wait_for(self.result_queue.get(), timeout=2)
                #result = await self.result_queue.get()
                result = await asyncio.wait_for(self.result_queue.get(), timeout=2)
                if result[0][2]['kind'] not in ('groups', 'users','users-single', 'projects', 'issues', 'wikis', 'wikis-single', 'milestones', 'milestones-single', 'notes', ):
                    foo = 1
                res = await self.dispatch(*result)
            except queue.Empty:
                pass
            except asyncio.exceptions.TimeoutError:
                pass
            except Exception as why:
                log.error(why)
                log.error("".join(traceback.format_exception(*sys.exc_info())))
                foo = 1
                
                
            self.progress.update(remain)

        await self._stop_pool()

    async def worker(self):
        "the main loop of a single `fiber`"
        while True:
            try:
                while (pending := self.result_queue.qsize()) > 200:
                    print(f"Pause worker due too much results pending in queue: {pending}")
                    await asyncio.sleep(1)
                    
                if random.random() < 0.10:
                    print(f"pending: {pending}")
                    
                # Get a task from the queue
                task = await asyncio.wait_for(self.task_queue.get(), timeout=2)
                if task is None:
                    break  # Break the loop
                self._wip.append(1)
                func, args, kwargs = task
                # print(f">> Processing task: {args}: {kwargs}")
                async for data in func(*args, **kwargs):
                    item = task, data
                    await self.result_queue.put(item)
                self._wip.pop()
                # print(f"<< Processing task: {func}")
            except queue.Empty:
                pass
            except asyncio.exceptions.TimeoutError:
                pass
            except Exception as why:
                log.error(why)
                log.error("".join(traceback.format_exception(*sys.exc_info())))

    def get_uid(self, kind, data):
        "Try to guess the `uid` of an item of `type_` class"
        if kind in self.KINDS_UID:
            uid_key, func, id_key = self.KINDS_UID[kind]
            # uid_key = self.KINDS_UID.get(kind, '{id}')
            if not isinstance(data, dict):
                data = data.model_dump()
            uid = uid_key.format_map(data)
            # uid = item[uid]
            fquid = func(uid)
            data[id_key] = fquid
            data['_fquid'] = fquid
            data['_uid'] = uid
        else:
            uid = data["id"]
        return uid

    def convert_into_references(self, data):
        """Search for nested objects in `value` and convert them into references"""
        if self.REFERENCE_MATCHES:
            id_keys = list(
                walk(
                    data,
                    keys_included=self.REFERENCE_MATCHES,
                    include_struct=False,
                )
            )
            for idkey, idval in id_keys:
                # myassign(value, myget(value, idkey), idkey[:-1])
                myassign(data, idval, idkey[:-1])

        return data


# class BaseSystem:
#     def __init__(self, config_path=None):
#         if not config_path:
#             config_path = "config.yaml"
#         config_path = expandpath(config_path)
#         self.root = os.path.dirname(config_path)
#         self.stats_path = os.path.join(self.root, "stats.yaml")

#         # env_path = os.path.join(self.root, '.env')
#         # log.info(f"loading ENV from: {env_path}")
#         # load_dotenv(env_path)

#         try:
#             self.cfg = yaml.load(open(config_path, "rt"), Loader=yaml.Loader)
#         except Exception:
#             self.cfg = {}

#         # self.db_path = os.path.join(self.root, 'database.pkl')
#         # self.db = {}

#         # gitlab_cfg_path = self.cfg["gitlab_cfg_path"]
#         # gitlab_instance = self.cfg["gitlab_instance"]

#         # self.gl = gitlab.Gitlab.from_config(gitlab_instance, [gitlab_cfg_path])
#         # self.gl.enable_debug()

#         self._interests = ["groups", "projects", "milestones", "issues", "wikis"]
#         self._klass_key = {
#             # gitlab.Gitlab: "root",
#             # Group: "groups",
#             # GroupMilestone: "milestones",
#             # Issue: "issues",
#             # Project: "projects",
#             # ProjectIssue: "issues",
#             # ProjectWiki: "wikis",
#             # User: "users",
#         }
#         self._cache_item = {}
#         self._cache_list = {}
#         self._cache_ok = 0
#         self._cache_attemps = 0

#         self.runner = Parallel(num_threads=20, dispatch=self._process)
#         self._add_task = self.runner.add_task

#         self.model = {}

#     def save_model(self):
#         pickle.dump(self.model, open("model.pickle", "wb"))
#         yaml.dump(self.model, open("model.yaml", "w"), Dumper=yaml.Dumper)

#     def load_model(self):
#         self.model = pickle.load(open("model.pickle", "rb"))
#         # self.model = yaml.load(open("model.yaml", "r"), Loader=yaml.Loader)

#     def _bootstrap(self):
#         """Initial tasks to start to building the model"""
#         self._add_task(self._fact, 0)

#     def _fact(self, x):
#         z = 1
#         for y in range(1, x + 1):
#             z *= y

#         # time.sleep(random.random())

#         log.info(f"FACTORIAL ({x}) = {z}!")

#         if self.runner.elapsed < 5:
#             s0 = random.randint(10, 20)
#             for y in range(s0, s0 + random.randint(1, 4)):
#                 self._add_task(self._fact, x + y)

#         return z

#     def _process(self, task, result, *args, **kw):
#         input_ = task[1]

#         log.info(f"process: {input_} --> {result}")

#     def build(self):
#         self._bootstrap()
#         self.runner.run()
#         log.info(f"elapsed: {self.runner.elapsed}")
#         self.save_model()
#         return self.model
