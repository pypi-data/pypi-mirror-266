from kivymd.uix.boxlayout import MDBoxLayout
from typing import Callable
from kivy.properties import NumericProperty

from kivymd_utils.redrawAble.notifyListeners import NotifyListener

class RedrawAble(MDBoxLayout):
    """Widget that redraws the contained widget tree on change of a variable
    the widget does not need to own the variable
    """
    # this property is used to force a redraw
    # it never contains actual data
    changer = NumericProperty(0)
    def __init__(self, *args, builder: Callable[[], any], provider: NotifyListener, **kwargs):
        super().__init__(args, kwargs)
        self.builder = builder
        self.widget = self.builder()
        self.provider = provider
        self.provider.register_listener(self.redraw)
        self.add_widget(self.widget)

    def on_changer(self, instance, new_val):
        new_widget = self.builder()
        self.remove_widget(self.widget)
        self.widget = new_widget
        self.add_widget(self.widget)

    def redraw(self):
        self.changer = (self.changer + 1) % 10

    