

from ebs.linuxnode.core.basemixin import BaseMixin
from .managers import GalleryManager

from .constants import SIDEBAR


class GalleryMixin(BaseMixin):
    def __init__(self, *args, **kwargs):
        self._gallery_managers = {}
        super(GalleryMixin, self).__init__(*args, **kwargs)

    def gallery_manager(self, gmid):
        if gmid not in self._gallery_managers.keys():
            self.log.info("Initializing gallery manager {gmid}", gmid=gmid)
            self._gallery_managers[gmid] = GalleryManager(self, gmid, self.gui_gallery)
        return self._gallery_managers[gmid]

    def gallery_default_duration(self, value):
        self.gallery_manager(SIDEBAR).default_duration = value

    def gallery_load(self, items):
        self.gallery_manager(SIDEBAR).load(items)

    def gallery_start(self):
        self.gallery_manager(SIDEBAR).start()

    def gallery_stop(self):
        self.gallery_manager(SIDEBAR).stop()

    @property
    def gui_gallery(self):
        raise NotImplementedError

    def start(self):
        super(GalleryMixin, self).start()
        self.gallery_start()
