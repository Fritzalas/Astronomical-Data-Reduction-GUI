from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from UI.StarryBackground import StarryBackground


class AstronomyApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical")

        # starry background
        background = StarryBackground()
        root.add_widget(background)
        return root