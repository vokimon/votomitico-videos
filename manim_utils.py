from manim import *


def overshoot(t, s=1.70158):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def add_background(scene, colors=["#f85158", BLACK]):
    if config.transparent:
        return  # Do not add the background with --transparent cli option

    background = Rectangle(
        width=config.frame_width,
        height=config.frame_height,
        fill_opacity=1,
        stroke_width=0
    )
    background.set_fill(color=colors, opacity=1)
    background.move_to(ORIGIN)
    scene.add(background)


def show_caption(scene, text):
    shadow = Text(text, font_size=48, color=BLACK)
    shadow.set_opacity(0.3)
    shadow.shift(0.06 * DOWN + 0.06 * RIGHT)

    caption = Text(text, font_size=48, color=WHITE)
    caption_group = VGroup(shadow, caption)
    caption_group.to_edge(DOWN, buff=0.6)

    scene.add(caption_group)

