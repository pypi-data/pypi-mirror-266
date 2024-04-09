from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import NumericProperty

from kivymd_utils.redrawAble import NotifyListener
import asyncio
from typing import Callable

class CoroutineSnapshot(NotifyListener):
    def __init__(self, coroutine):
        super().__init__()
        self._task = asyncio.create_task(coroutine)
        self._has_data = False
        self._data = None
        self._task.add_done_callback(self._on_finish)

    def _on_finish(self, context):
        self._has_data = context.done()
        self._data = context.result()
        self.notify_listeners()

    @property
    def has_data(self) -> bool:
        return self._has_data
    

    @property
    def ensure_data(self) -> any:
        if not self.has_data:
            raise Exception("tried to get data when none is available")
        
        return self._data

    @property
    def data(self):
        return self._data

class CoroutineBuilder(MDBoxLayout):
    changer = NumericProperty(0)
    def __init__(self, builder: Callable[[CoroutineSnapshot], any], coroutine, **kwargs):
        super().__init__()
        self.snapshot = CoroutineSnapshot(coroutine)
        self.builder = builder
        self.snapshot.register_listener(self.redraw)
        self.widget = self.builder(self.snapshot)
        self.add_widget(self.widget)

    def on_changer(self, instance, new_val):
        new_widget = self.builder(self.snapshot)
        self.remove_widget(self.widget)
        self.widget = new_widget
        self.add_widget(self.widget)

    def redraw(self):
        self.changer = (self.changer + 1) % 10

