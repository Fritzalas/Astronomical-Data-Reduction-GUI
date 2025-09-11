from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import sys
import datetime
from UI.StarryBackground import StarryBackground
from UI.StylishButton import StylishButton


class AstronomyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logs = []  # in-memory logs

    def log_action(self, action: str):
        """Add an action to the in-memory log with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append(f"[{timestamp}] {action}")

    def proceed_clicked(self):
        self.log_action("Proceed button clicked")

    def exit_clicked(self):
        self.log_action("Exit button clicked")
        sys.exit(0)

    def build(self):
        root = FloatLayout()

        # Add starry background
        stars = StarryBackground()
        root.add_widget(stars)

        # Add informative text overlay
        info_text = (
            "Welcome to the Data Reduction GUI!\n\n"
            "The purpose of this App is to enable users to perform image reduction and data analysis of FITS files.\n\n"
            "Features:\n"
            "- Master Bias Creation"
        )
        label = Label(
            text=info_text,
            font_size='20sp',
            color=(1, 1, 1, 0.9),  # white, semi-transparent
            halign='center',
            valign='top',
            size_hint=(0.8, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.70}
        )
        label.bind(size=label.setter('text_size'))  # wrap text
        root.add_widget(label)
        # Buttons layout
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint=(0.6, None),
            height=50,
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )

        proceed_btn = StylishButton(text="Proceed")
        proceed_btn.bind(on_release=lambda instance: self.proceed_clicked())

        exit_btn = StylishButton(text="Exit")
        exit_btn.bind(on_release=lambda instance: self.exit_clicked())

        button_layout.add_widget(proceed_btn)
        button_layout.add_widget(exit_btn)
        root.add_widget(button_layout)

        return root