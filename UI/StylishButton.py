from kivy.uix.button import Button

class StylishButton(Button):
    """Custom button with rounded corners and color effects"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''  # Remove default background
        self.background_color = (0.2, 0.6, 0.9, 0.8)  # bluish semi-transparent
        self.color = (1, 1, 1, 1)  # white text
        self.font_size = '18sp'
        self.size_hint_y = None
        self.height = 50
        self.border_radius = 15  # Rounded corners

    def on_press(self):
        # Darken button on press
        self.background_color = (0.1, 0.4, 0.7, 0.9)
        super().on_press()

    def on_release(self):
        # Restore color on release
        self.background_color = (0.2, 0.6, 0.9, 0.8)
        super().on_release()