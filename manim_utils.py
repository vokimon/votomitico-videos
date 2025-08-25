from manim import *

def overshoot(t, s=1.70158):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1

def reverse_overshoot(t, s=1.70158):
    return 1 - overshoot(1 - t, s)

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

def full_remove(self, mob):
    mob.clear_trackers()
    self.to_delete.remove(mob)
    self.remove(mob)

def clear_previous_scene(self):
    for mob in self.to_remove:
        full_remove(self, mob)

def the_end(scene):
    """Emulates a next scene fading out elements of the previous one"""
    label = Text(text="THE END", color=BLUE, font_size=300, fill_opacity=0.5).scale(0.5).move_to(DOWN * 3)

    scene.play(
        AnimationGroup(
            FadeOut(scene.to_delete),
            FadeIn(label),
            lag_ratio=0.3,
        )
    )
    scene.wait(0.3)
