from manim import *
from manim_utils import add_background, overshoot  # Asegúrate de tener esta función definida en manim_utils.py


# === Manim Config ===
config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 18
config.frame_height = 32
config.background_color = None

cascade_lines = [
    "Más trasvase no da más escaños",
    "Como mucho diferencia de un escaño",
    "Igual de probable perderlo o ganarlo",
    "Hacia el menor, mismos resultados",
]

def create_cascade_texts(lines, total_duration=3.0, spacing=1.5):
    texts = VGroup()
    for i, line in enumerate(lines):
        txt = Text(
            line,
            color="#DDD",
            font="sans"
        ).scale_to_fit_width(config.frame_width * 0.9)
        txt.shift(DOWN * spacing * i)
        texts.add(txt)

    def animate_cascade(scene):
        n = len(lines)
        per_line = total_duration / n
        for txt in texts:
            scene.play(FadeIn(txt, shift=UP), run_time=per_line)
            scene.wait(0.1)

    return texts, animate_cascade

def stamp_seal(self, text="mito", width=12, color=RED, stroke_width=18, duration=0.6):
    label = Text(
        text.upper(),
        font="sans",
        slant=ITALIC,
        color=WHITE,
        weight=BOLD,
        fill_opacity=1
    ).scale_to_fit_width(width * 0.8)

    line = Line(LEFT * width / 2, RIGHT * width / 2,
                stroke_width=stroke_width, color=color)
    top_line = line.copy().next_to(label, UP, buff=0.3)
    bottom_line = line.copy().next_to(label, DOWN, buff=0.3)

    stamp = VGroup(top_line, label, bottom_line)
    stamp.set_stroke(color=color, width=stroke_width)
    stamp.set_fill(color=color, opacity=1)
    stamp.rotate(10 * DEGREES)

    stamp.scale(0.1).move_to(DOWN * 6)

    self.play(
        stamp.animate.scale(10),
        rate_func=rush_into,
        run_time=duration,
    )
    return stamp

def conclusions(self):
    texts, animate = create_cascade_texts(
        cascade_lines,
        total_duration=4.0,  # <-- controla toda la animación
        spacing=3.0
    )

    texts.move_to(UP * 2.5)
    animate(self)

    self.wait(0.3)

    stamp = stamp_seal(self)


class CascadingTextsScene(Scene):
    def construct(self):
        add_background(self)
        conclusions(self)
        self.wait(1)
