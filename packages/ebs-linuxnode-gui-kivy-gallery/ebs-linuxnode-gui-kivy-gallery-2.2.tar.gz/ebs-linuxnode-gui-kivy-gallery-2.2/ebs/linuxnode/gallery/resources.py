

import os
from six.moves.urllib.parse import urlparse
from sqlalchemy.orm.exc import NoResultFound

from .constants import WEBRESOURCE


class GalleryResource(object):
    def __init__(self, manager, seq=None, rtype=None,
                 resource=None, duration=None):
        self._manager = manager
        self._seq = seq

        self._rtype = None
        self.rtype = rtype

        self._resource = None
        self.resource = resource

        self._duration = duration

        if not self._rtype:
            self.load()

    @property
    def seq(self):
        return self._seq

    @property
    def rtype(self):
        return self._rtype

    @rtype.setter
    def rtype(self, value):
        if value not in [None, WEBRESOURCE]:
            raise ValueError
        self._rtype = value

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, value):
        if self._rtype == WEBRESOURCE:
            self._resource = os.path.basename(urlparse(value).path)

    @property
    def duration(self):
        return self._duration

    def commit(self):
        session = self._manager.db()
        try:
            try:
                robj = session.query(self._db_model).filter_by(seq=self.seq).one()
            except NoResultFound:
                robj = self._db_model()
                robj.seq = self.seq

            robj.rtype = self.rtype
            robj.resource = self.resource
            robj.duration = self._duration

            session.add(robj)
            session.commit()
            session.flush()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def load(self):
        session = self._manager.db()
        try:
            robj = session.query(self._db_model).filter_by(seq=self._seq).one()
            self.rtype = robj.rtype
            self.resource = robj.resource
            self._duration = robj.duration
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def _db_model(self):
        return self._manager.db_model
