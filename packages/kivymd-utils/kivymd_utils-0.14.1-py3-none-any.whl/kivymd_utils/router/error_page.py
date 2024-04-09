from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDTextButton

class ErrorPage(MDBoxLayout):
    def __init__(self, error_route: str, *args, **kwargs):
        router = kwargs["router"]
        super().__init__(
            MDLabel(text="invalid route detected"),
            MDLabel(text=f"route '{error_route}' does not exist"),
            MDTextButton(
                text="go back",
                on_release=lambda x: router.pop()
            ),
            orientation="vertical"
        )