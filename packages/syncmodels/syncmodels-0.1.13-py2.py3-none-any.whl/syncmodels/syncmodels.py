"""Main module."""

# library modules
import asyncio
import os
import pickle
import re

# import time


import uvloop

# import ryaml
import yaml

# library partial
# from time import sleep


# local imports
from .helpers import expandpath
from .storage import SurrealStorage,  SurrealistStorage
# from .parallel import  AsyncParallel

# 3rd party libraries
# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------
from agptools.containers import walk, rebuild, deep_chain




# ---------------------------------------------------------
# storage
# ---------------------------------------------------------
# from .storage import Storage
from .storage import Storage, iCRUD

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)

# subloger = logger(f'{__name__}.subloger')


# =========================================================
# syncmodels
# =========================================================


class COPY:
    pass


class SyncMode_old:
    MAPPERS = {}
    RESTRUCT_DATA = {}
    RETAG_DATA = {}
    REFERENCE_MATCHES = []
    KINDS_UID = {}
    MODEL = None  # calleable to create a Model instance

    def __init__(
        self,
        config_path=None,
        overwrite=False,
        save_model=True,
        num_threads=None,
        db_url=None,
    ):
        if not config_path:
            config_path = "config.yaml"
        config_path = expandpath(config_path)
        self.root = os.path.dirname(config_path)
        self.stats_path = os.path.join(self.root, "stats.yaml")

        # env_path = os.path.join(self.root, '.env')
        # log.info(f"loading ENV from: {env_path}")
        # load_dotenv(env_path)

        self.cfg = yaml.load(
            open(config_path, "rt", encoding="utf-8"), Loader=yaml.Loader
        )

        # runner / threads
        num_threads = num_threads or self.cfg.get("threads", 8)
        # self.runner = Parallel(num_threads=num_threads)
        self.runner = AsyncParallel(num_threads=num_threads)
        self._add_task = self.runner.add_task

        self.model = None

        # storage
        db_url = db_url or self.cfg.get("db_url", "./data")
        self.db = Storage(url=db_url)

        self._save_model = save_model
        self._overwrite = overwrite

    def save_model(self, table="model", data=None):
        if data is None:
            if isinstance(self.model, dict):
                data = self.model
            else:
                data = self.model.model_dump()

        asyncio.run(self.db.set(table, data))

    def load_model(self):
        try:
            self.model = pickle.load(open("model.pickle", "rb"))
            # self.model = yaml.load(open("model.yaml", "r"), Loader=yaml.Loader)
        except Exception as why:
            log.error(f"can't load model from disk: {why}")

    def sync(self):
        for func, args, kwargs in self._bootstrap():
            self._add_task(func, *args, **kwargs)

        uvloop.install()
        asyncio.run(self.runner.run())

        print(f"elapsed: {self.runner.elapsed}")
        self._build_items()
        if self._save_model:
            self.save_model()
        return self.model

    def _bootstrap(self):
        raise NotImplementedError()

    def _build_items(self):
        # _model = self.MODEL()
        model = self.model
        for kind, holder in model.__dict__.items():
            # holder = getattr(model, kind)
            for uid, data in holder.items():
                item = self.new(kind, data)
                holder[uid] = item
        foo = 1

    def new(self, type_, data):
        data = self.convert_into_references(data)

        klass = self.MAPPERS.get(type_)
        if not klass:
            log.warning(f"missing MAPPERS[{type_}] class!")
            return

        item = klass.pydantic(data)
        return item

    def _clean(self, kind, data):
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip()
        return data

    def _restruct(self, kind, data, reveal):
        restruct = {}
        info = self.RESTRUCT_DATA.get("default", {})
        info.update(self.RESTRUCT_DATA.get(kind, {}))
        for path, value in reveal.items():
            for pattern, (new_path, new_value) in info.items():
                m = re.match(pattern, path)
                if m:
                    d = m.groupdict()
                    d["value"] = value
                    key = tuple(new_path.format_map(d).split("/"))
                    _value = value if new_value == COPY else new_value.format_map(d)
                    restruct[key] = _value

        restruct = rebuild(restruct, result={})
        data = {**data, **restruct}

        return data

        # expand all tagging info

    def convert_into_references(self, value):
        if self.REFERENCE_MATCHES:
            id_keys = list(
                walk(
                    value,
                    keys_included=self.REFERENCE_MATCHES,
                    include_struct=False,
                )
            )
            for idkey, idval in id_keys:
                # myassign(value, myget(value, idkey), idkey[:-1])
                myassign(value, idval, idkey[:-1])

        return value

    def get_uid(self, kind, item):
        # uid = getattr(item, 'id', None)
        # if uid is None:
        # use render templates
        if kind in self.KINDS_UID:
            uid_key, func, id_key = self.KINDS_UID[kind]
            # uid_key = self.KINDS_UID.get(kind, '{id}')
            if not isinstance(item, dict):
                item = item.dict()
            uid = uid_key.format_map(item)
            # uid = item[uid]
            uid = func(uid)
            item[id_key] = uid
        else:
            uid = item["id"]
        return uid


# =========================================================
# syncmodel Namespace and Surreal Storage Support
# =========================================================

def apply_fqui(item):
    if isinstance(item.id, str) and ':' in str(item.id):
        return item.id
    
    klass = item.__class__
    kind = f"{klass.__module__.replace('.', '_')}_{klass.__name__}"
    
    
    uid = str(item.id).replace('/', '_').replace('.', '_')
    fqid = f"{kind}:{uid}"
    item.id = fqid
    
    if 'Wiki' in kind:
        print(item.id)
        
    return item.id
        

class SyncModel(iCRUD):
    MAPPERS = {}
    RESTRUCT_DATA = {}
    RETAG_DATA = {}
    REFERENCE_MATCHES = []
    KINDS_UID = {}
    MODEL = None  # callable to create a Model instance

    def __init__(
        self,
        config_path=None,
        storage: Storage = None,
        surreal_url=None,
        *args,
        **kw, 
    ):
        if not config_path:
            config_path = "config.yaml"
        config_path = expandpath(config_path)
        self.root = os.path.dirname(config_path)
        self.stats_path = os.path.join(self.root, "stats.yaml")

        with open(config_path, "rt", encoding="utf-8") as f:
            self.cfg = yaml.load(f, Loader=yaml.Loader)
        self.model = {}
        # storage
        if storage is None:
            surreal_url = surreal_url or self.cfg.get("surreal_url", "http://localhost:9000")
            #storage = SurrealStorage(url=surreal_url)
            storage = SurrealistStorage(url=surreal_url)
                        
        self.storage = storage

    def _build_items(self):
        # _model = self.MODEL()
        model = self.model
        for kind, holder in model.__dict__.items():
            # holder = getattr(model, kind)
            for uid, data in holder.items():
                item = self.new(kind, data)
                holder[uid] = item

    async def put(self, item) -> bool:
        """Try to create / update an item of `type_` class from raw data

        - get the pydantic item
        - save it to storage in case it have changed

        Returns:
        - bool: True if the item has been saved, False otherwise

        """
        result = False
        if item:
            fqid = apply_fqui(item)
            current = await self.storage.get(fqid)
            if current:
                data = item.model_dump()
                #data.pop('id')
                #current.pop('id')
                if current != data:
                    result = await self.storage.put(item)
                    #await self.storage.update(item) # TODO: use update
            else:
                reault = await self.storage.put(item)

        return result

    

    def _clean(self, data):
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip()
        return data

    def _restruct(self, kind, data, reveal):
        restruct = {}
        info = self.RESTRUCT_DATA.get("default", {})
        info.update(self.RESTRUCT_DATA.get(kind, {}))
        for path, value in reveal.items():
            for pattern, (new_path, new_value) in info.items():
                m = re.match(pattern, path)
                if m:
                    d = m.groupdict()
                    d["value"] = value
                    key = tuple(new_path.format_map(d).split("/"))
                    _value = value if new_value == COPY else new_value.format_map(d)
                    restruct[key] = _value

        restruct = rebuild(restruct, result={})
        data = {**data, **restruct}

        return data

        # expand all tagging info

    

