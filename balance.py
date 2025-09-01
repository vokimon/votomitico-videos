from manim import *
import numpy as np
from manim_utils import (
    add_background,
    overshoot,
    reverse_overshoot,
)

# === Manim render config ===
config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 18
config.frame_height = 32
config.background_color = None

def create_balance(self):
    s = min(config.frame_width, config.frame_height)
    self.base_scale = s
    self.arm_angle = 0

    # === SCALED DIMENSIONS (all doubled for larger rendering) ===
    self.support_height = 0.4 * s
    arm_length = 0.66 * s
    arm_thickness = 0.028 * s
    support_width = 0.03 * s
    plate_height = 0.03 * s
    plate_width_top = 0.176 * s
    plate_width_bottom = 0.11 * s
    self.plate_offset = 0.166 * s
    base_triangle_height = 0.12 * s
    base_triangle_width = 0.28 * s

    self.left_tilt_angle = 0.3
    self.right_tilt_angle = -0.4
    
    self.weight_bad_radius = 0.03 * s
    self.weight_good_radius = 0.04 * s

    base_bottom = DOWN * (base_triangle_height + self.support_height)

    base = Polygon(
        LEFT * base_triangle_width / 2 + DOWN * base_triangle_height,
        RIGHT * base_triangle_width / 2 + DOWN * base_triangle_height,
        + RIGHT * support_width / 2,
        + LEFT * support_width / 2,
        color=GRAY, fill_color=GRAY, fill_opacity=1
    ).shift(base_bottom)

    support = Rectangle(
        height=self.support_height,
        width=support_width,
        color=GRAY, fill_color=GRAY, fill_opacity=1
    ).next_to(base.get_top(), UP, buff=0)

    self.pivot_point = support.get_top()
    pivot = Dot(point=self.pivot_point, radius=0.005 * s, color=ORANGE)

    self.arm = Rectangle(
        height=arm_thickness,
        width=arm_length,
        color=GRAY, fill_color=GRAY, fill_opacity=1
    ).move_to(self.pivot_point)

    def get_left_tip(angle):
        return self.pivot_point + rotate_vector(LEFT * arm_length / 2, angle)

    def get_right_tip(angle):
        return self.pivot_point + rotate_vector(RIGHT * arm_length / 2, angle)

    self.get_left_tip = get_left_tip
    self.get_right_tip = get_right_tip

    def make_plate(position):
        return Polygon(
            position + UP * plate_height / 2 + LEFT * plate_width_top / 2,
            position + UP * plate_height / 2 + RIGHT * plate_width_top / 2,
            position + DOWN * plate_height / 2 + RIGHT * plate_width_bottom / 2,
            position + DOWN * plate_height / 2 + LEFT * plate_width_bottom / 2,
            color=GRAY, fill_color=GRAY, fill_opacity=1
        )

    self.left_plate = make_plate(
        self.get_left_tip(self.arm_angle) + DOWN * self.plate_offset
    )
    self.right_plate = make_plate(
        self.get_right_tip(self.arm_angle) + DOWN * self.plate_offset
    )

    self.left_chain = Line(
        self.get_left_tip(self.arm_angle),
        self.left_plate.get_top(),
        color=GRAY
    )
    self.right_chain = Line(
        self.get_right_tip(self.arm_angle),
        self.right_plate.get_top(),
        color=GRAY
    )

    self.weight_bad = Circle(radius=self.weight_bad_radius, fill_opacity=1, color=RED)
    self.weight_good = Circle(radius=self.weight_good_radius, fill_opacity=1, color=GREEN)

    self.to_delete = VGroup(
        base, support, pivot,
        self.arm,
        self.left_plate, self.right_plate,
        self.left_chain, self.right_chain
    )

    def update_positions(mob, dt):
        mob.move_to(self.pivot_point)
        mob.set_angle(self.arm_angle)

        self.left_plate.move_to(self.get_left_tip(self.arm_angle) + DOWN * self.plate_offset)
        self.right_plate.move_to(self.get_right_tip(self.arm_angle) + DOWN * self.plate_offset)

        self.left_chain.put_start_and_end_on(
            self.get_left_tip(self.arm_angle),
            self.left_plate.get_top()
        )
        self.right_chain.put_start_and_end_on(
            self.get_right_tip(self.arm_angle),
            self.right_plate.get_top()
        )

        if self.weight_bad in self.mobjects:
            self.weight_bad.move_to(self.left_plate.get_center() + UP * 0.022 * s)
        if self.weight_good in self.mobjects:
            self.weight_good.move_to(self.right_plate.get_center() + UP * 0.022 * s)

    self.arm.add_updater(update_positions)

    vertical_shift = -self.to_delete.get_center()[1]

    # Shift all static parts
    self.to_delete.shift(UP * vertical_shift)

    # Also shift pivot point vector
    self.pivot_point += UP * vertical_shift

    # Move arm to new pivot point (important for updaters)
    self.arm.move_to(self.pivot_point)


# === Arm rotation ===
def rotate_arm_to(self, target_angle, duration):
    start_angle = self.arm_angle
    start_time = self.time

    def updater(mob, dt):
        elapsed = self.time - start_time
        t = min(1, elapsed / duration)
        new_angle = interpolate(start_angle, target_angle, t)
        diff = new_angle - self.arm_angle
        mob.rotate(diff, about_point=self.pivot_point)
        self.arm_angle = new_angle

    self.arm.add_updater(updater)
    self.wait(duration)
    self.arm.remove_updater(updater)
    self.arm_angle = target_angle

# === Animation steps ===
def show_balance(self, duration=0.3):
    self.add(self.to_delete)
    self.wait(duration)

def drop_bad_weight(self, duration=1.0):
    appear_time = 0.4 * duration
    settle_time = 0.2 * duration
    tilt_time = 0.4 * duration
    first_scale = 0.6
    bounce_scale = 1.5

    self.weight_bad.scale(first_scale * self.weight_bad_radius / self.weight_bad.radius)  # ensure small start
    self.weight_bad.set_opacity(0)
    self.add(self.weight_bad)
    self.to_delete.add(self.weight_bad)

    self.play(
        self.weight_bad.animate.set_opacity(1).scale(bounce_scale * self.weight_bad_radius / self.weight_bad.radius),
        rate_func=overshoot,
        run_time=appear_time
    )
    self.play(
        self.weight_bad.animate.scale(self.weight_bad_radius / self.weight_bad.radius),
        run_time=settle_time
    )
    rotate_arm_to(self, self.left_tilt_angle, tilt_time)

def drop_good_weight(self, duration=1.2):
    appear_time = 0.3 * duration
    settle_time = 0.1 * duration
    tilt_time = 0.6 * duration

    if self.weight_good not in self.mobjects:
        self.weight_good.scale(0.6)
        self.weight_good.set_opacity(0)
        self.add(self.weight_good)
        self.to_delete.add(self.weight_good)

    self.play(
        self.weight_good.animate.set_opacity(1).scale(2.0),
        rate_func=overshoot,
        run_time=appear_time
    )
    self.play(
        self.weight_good.animate.scale(0.5),
        run_time=settle_time
    )
    rotate_arm_to(self, self.right_tilt_angle, tilt_time)

def remove_good_weight(self, duration=1.0):
    pop_time = 0.1 * duration
    fade_time = 0.3 * duration
    tilt_time = 0.6 * duration

    self.play(
        self.weight_good.animate.scale(1.2),
        rate_func=overshoot,
        run_time=pop_time
    )
    self.play(
        self.weight_good.animate.set_opacity(0).scale(0),
        run_time=fade_time
    )
    self.remove(self.weight_good)
    self.to_delete.remove(self.weight_good)

    rotate_arm_to(self, self.left_tilt_angle, tilt_time)
    self.arm.clear_updaters()

def balance_sequence(self):
    create_balance(self)

    show_balance(self)
    self.wait(1)
    drop_bad_weight(self)
    self.wait(1)
    drop_good_weight(self)
    self.wait(1.5)
    remove_good_weight(self)

# === Debug Scene with inline transition
class DebugBalanceScene(Scene):
    def construct(self):
        add_background(self)
        create_balance(self)

        show_balance(self)
        drop_bad_weight(self)
        drop_good_weight(self)
        remove_good_weight(self)

        # Simulate next scene
        next_scene_element = Text(text="THE END", color=BLUE, font_size=300, fill_opacity=0.5).scale(0.5).move_to(DOWN * 3)

        self.play(
            AnimationGroup(
                FadeOut(self.to_delete),
                FadeIn(next_scene_element),
                lag_ratio=0.3,
            )
        )
        self.wait(0.3)
