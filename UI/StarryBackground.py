import random
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.animation import Animation

class StarryBackground(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stars = []
        self.num_stars = 180  # number of stars

        # define a richer palette of star colors
        self.star_colors = [
            (1, 1, 1),  # white
            (0.7, 0.8, 1),  # bluish-white
            (0.5, 0.7, 1),  # deep blue
            (0.6, 0.9, 1),  # cyan-tinted
            (1, 0.95, 0.7),  # yellowish
            (1, 0.85, 0.5),  # orange
            (1, 0.6, 0.6),  # light red
            (0.9, 0.5, 0.7),  # magenta tint
        ]

        with self.canvas:
            # black sky background
            self.bg_color = Color(0, 0, 0, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

            # create stars
            for _ in range(self.num_stars):
                x = random.randint(0, 800)
                y = random.randint(0, 600)
                size = random.randint(3, 6)

                r, g, b = random.choice(self.star_colors)
                c = Color(r, g, b, random.uniform(0.4, 1))
                e = Ellipse(pos=(x, y), size=(size, size))  # width == height ensures round
                self.stars.append((c, e))

        self.bind(size=self.update_layout, pos=self.update_layout)
        self.start_animation()

    def update_layout(self, *_):
        """Adjust background and reposition stars on resize"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        for c, e in self.stars:
            x = random.randint(0, int(self.width))
            y = random.randint(0, int(self.height))
            e.pos = (x, y)
            e.size = (e.size[0], e.size[0])  # keep width == height

    def start_animation(self):
        """Start twinkling for all stars"""
        for c, e in self.stars:
            self.animate_star(c)

    def animate_star(self, color_instruction):
        """Recursive twinkling effect"""
        anim = (
            Animation(a=random.uniform(0.1, 1), duration=random.uniform(0.3, 1)) +
            Animation(a=random.uniform(0.1, 1), duration=random.uniform(0.3, 1))
        )
        anim.bind(on_complete=lambda *x: self.animate_star(color_instruction))
        anim.start(color_instruction)