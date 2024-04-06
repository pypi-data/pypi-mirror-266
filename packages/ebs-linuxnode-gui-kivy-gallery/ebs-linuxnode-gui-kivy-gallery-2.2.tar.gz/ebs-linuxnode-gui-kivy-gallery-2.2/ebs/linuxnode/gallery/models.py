

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class WebResourceGalleryModel(Base):
    __tablename__ = 'gallery_1'

    id = Column(Integer, primary_key=True)
    seq = Column(Integer, unique=True, index=True)
    rtype = Column(Integer)
    resource = Column(Text, index=True)
    duration = Column(Integer)

    def __repr__(self):
        return "{0:3} {1} {2} [{3}]".format(
            self.seq, self.rtype, self.resource, self.duration or ''
        )
