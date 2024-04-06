

from kivy.uix.relativelayout import RelativeLayout
from kivy_garden.ebs.gallery import ImageGallery

from ebs.linuxnode.gui.kivy.core.basenode import BaseIoTNodeGui
from ebs.linuxnode.gallery.mixin import GalleryMixin
from kivy_garden.ebs.core.colors import color_set_alpha


class GalleryGuiMixin(GalleryMixin, BaseIoTNodeGui):
    _media_extentions_image = ['.png', '.jpg', '.bmp', '.gif', '.jpeg']

    def __init__(self, *args, **kwargs):
        self._gallery = None
        self._gallery_parent_layout = None
        super(GalleryGuiMixin, self).__init__(*args, **kwargs)

    @property
    def gui_gallery_parent(self):
        if not self._gallery_parent_layout:
            self._gallery_parent_layout = RelativeLayout()
            self.gui_sidebar.add_widget(self._gallery_parent_layout)
        return self._gallery_parent_layout

    def _gui_gallery_sidebar_control(self, *args):
        if self.gui_gallery.visible:
            self.gui_sidebar_show('gallery')
        else:
            self.gui_sidebar_hide('gallery')

    def gallery_bgcolor(self, value):
        self.gui_gallery.bgcolor = color_set_alpha(value, 1)

    @property
    def gui_gallery(self):
        if not self._gallery:
            params = {'parent_layout': self.gui_gallery_parent}
            if self.config.portrait:
                params['animation_vector'] = (1, 0)
            else:
                params['animation_vector'] = (0, 1)
            self._gallery = ImageGallery(**params)
            self._gallery.bind(visible=self._gui_gallery_sidebar_control)
        return self._gallery

    def gui_setup(self):
        return super(GalleryGuiMixin, self).gui_setup()
