

import os
from twisted import logger
from twisted.internet.task import deferLater
from twisted.internet.defer import CancelledError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

# TODO Detach this
from kivy_garden.ebs.pdfplayer import PDFPlayer

from .resources import GalleryResource
from .models import WebResourceGalleryModel
from .models import metadata

from ebs.linuxnode.core.constants import ASSET
from .constants import WEBRESOURCE
from .constants import SIDEBAR


class BaseGalleryManager(object):
    def __init__(self, node, gmid, widget, default_duration=4):
        self._gmid = gmid
        self._log = None
        self._node = node
        self._widget = widget
        self._default_duration = default_duration
        self._seq = 0
        self._task = None
        self._items = []

    @property
    def log(self):
        if not self._log:
            self._log = logger.Logger(namespace="gallery.{0}".format(self._gmid),
                                      source=self)
        return self._log

    @property
    def default_duration(self):
        return self._default_duration

    @default_duration.setter
    def default_duration(self, value):
        self._default_duration = value

    def flush(self, force=False):
        self.log.debug("Flushing gallery resources")
        self._items = []
        if force:
            self._trigger_transition()

    def _load(self, items):
        return items

    def load(self, items):
        self.log.debug("Loading gallery resource list")
        self.flush()
        self._items = self._load(items)

    def add_item(self, item):
        raise NotImplementedError

    def remove_item(self, item):
        raise NotImplementedError

    @property
    def current_seq(self):
        return self._seq

    @property
    def next_seq(self):
        seq = self._seq + 1
        if seq < len(self._items):
            return seq
        elif len(self._items):
            return 0
        else:
            return -1

    def start(self):
        self.log.info("Starting Gallery Manager {gmid} of {name}",
                      gmid=self._gmid, name=self.__class__.__name__)
        self.step()

    def step(self):
        self._seq = self.next_seq
        duration = self._trigger_transition(stopped=False)
        if not duration:
            duration = self.default_duration
        self._task = deferLater(self._node.reactor, duration, self.step)

        def _cancel_handler(failure):
            failure.trap(CancelledError)
        self._task.addErrback(_cancel_handler)
        return self._task

    def _trigger_transition(self, stopped=False):
        # If current_seq is -1, that means the gallery is empty. This may be
        # called repeatedly with -1. Use the returned duration to slow down
        # unnecessary requests. This function should also appropriately handle
        # creating or destroying gallery components.
        if stopped or self.current_seq == -1:
            self._widget.current = None
            return 30
        target = self._items[self.current_seq]
        duration = target.duration
        if target.rtype == WEBRESOURCE:
            fp = self._node.resource_manager.get(target.resource).filepath

            if not os.path.exists(fp):
                self._widget.current = None
                return 10

            if os.path.splitext(fp)[1] == '.pdf':
                fp = PDFPlayer(source=fp, exit_retrace=True,
                               temp_dir=self._node.temp_dir)
                if not target.duration:
                    duration = fp.num_pages * fp.interval

            self._widget.current = fp
        return duration

    def stop(self):
        if self._task:
            self._task.cancel()
        self._trigger_transition(stopped=True)

    def render(self):
        for item in self._items:
            print(item)


class GalleryManager(BaseGalleryManager):
    def __init__(self, *args, **kwargs):
        super(GalleryManager, self).__init__(*args, **kwargs)

        self._db_engine = None
        self._db = None
        self._db_dir = None
        _ = self.db

        self._persistence_load()

    def flush(self, force=False):
        super(GalleryManager, self).flush(force=force)
        session = self.db()
        try:
            results = self.db_get_resources(session).all()
        except NoResultFound:
            session.close()
            return
        try:
            for robj in results:
                session.delete(robj)
                # Orphan the resource so that the cache infrastructure
                # will clear the files as needed
                r = self._node.resource_manager.get(robj.resource)
                r.rtype = None
                r.commit()
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _load(self, items):
        _items = []
        for idx, (resource, duration) in enumerate(items):
            robj = GalleryResource(
                self, seq=idx, rtype=WEBRESOURCE,
                resource=resource, duration=duration
            )
            robj.commit()
            _items.append(robj)
            r = self._node.resource_manager.get(resource)
            r.rtype = ASSET
            r.commit()
        self._fetch()
        return _items

    def _persistence_load(self):
        session = self.db()
        try:
            results = self.db_get_resources(session).all()
        except NoResultFound:
            session.close()
            return
        try:
            _items = []
            for robj in results:
                _items.append(GalleryResource(self, robj.seq))
        finally:
            session.close()
        self._items = _items
        self._fetch()

    def db_get_resources(self, session, seq=None):
        q = session.query(self.db_model)
        if seq is not None:
            q = q.filter(
                self.db_model.seq == seq
            )
        else:
            q = q.order_by(self.db_model.seq)
        return q

    @property
    def db_model(self):
        if self._gmid == SIDEBAR:
            return WebResourceGalleryModel

    @property
    def db(self):
        if self._db is None:
            self._db_engine = create_engine(self.db_url)
            metadata.create_all(self._db_engine)
            self._db = sessionmaker(expire_on_commit=False)
            self._db.configure(bind=self._db_engine)
        return self._db

    @property
    def db_url(self):
        return 'sqlite:///{0}'.format(os.path.join(self.db_dir, 'gallery.db'))

    @property
    def db_dir(self):
        return self._node.db_dir

    def _fetch(self):
        self.log.debug("Triggering Gallery Fetch")
        session = self.db()
        try:
            results = self.db_get_resources(session).all()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        for e in results:
            r = self._node.resource_manager.get(e.resource)
            self._node.resource_manager.prefetch(
                r, semaphore=self._node.http_semaphore_download
            )

    def render(self):
        print("----------")
        super(GalleryManager, self).render()
        print("DB Content")
        print("----------")
        session = self.db()
        try:
            results = self.db_get_resources(session).all()
        finally:
            session.close()
        print(results)
        print("----------")
