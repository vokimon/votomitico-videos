from manim import *
import numpy as np

# === Manim render config ===
config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 18
config.frame_height = 32
config.background_color = None

# === Easing functions ===
def overshoot(t, s=1.70158):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1

def reverse_overshoot(t, s=1.70158):
    return 1 - overshoot(1 - t, s)

# === Balance construction ===
def create_balance(self):
    s = min(config.frame_width, config.frame_height)
    self.base_scale = s
    self.arm_angle = 0

    # Dimensions
    self.support_height = 0.2 * s
    arm_length = 0.33 * s
    arm_thickness = 0.014 * s
    support_width = 0.015 * s
    plate_height = 0.033 * s
    plate_width_top = 0.088 * s
    plate_width_bottom = 0.055 * s
    self.plate_offset = 0.083 * s
    base_triangle_height = 0.06 * s
    base_triangle_width = 0.14 * s

    self.left_tilt_angle = 0.3
    self.right_tilt_angle = -0.4

    base_bottom = ORIGIN - UP * (base_triangle_height + self.support_height)

    base_triangle = Polygon(
        LEFT * base_triangle_width / 2 + DOWN * base_triangle_height,
        RIGHT * base_triangle_width / 2 + DOWN * base_triangle_height,
        ORIGIN,
        color=GRAY, fill_color=GRAY, fill_opacity=1
    ).shift(base_bottom)

    support = Rectangle(
        height=self.support_height,
        width=support_width,
        color=GRAY, fill_color=GRAY, fill_opacity=1
    ).next_to(base_triangle.get_top(), UP, buff=0)

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

    def trapezoid(center, color):
        top_left = center + UP * plate_height / 2 + LEFT * plate_width_top / 2
        top_right = center + UP * plate_height / 2 + RIGHT * plate_width_top / 2
        bottom_right = center + DOWN * plate_height / 2 + RIGHT * plate_width_bottom / 2
        bottom_left = center + DOWN * plate_height / 2 + LEFT * plate_width_bottom / 2
        return Polygon(top_left, top_right, bottom_right, bottom_left,
                       color=BLACK, fill_color=color, fill_opacity=0.6)

    self.left_plate = trapezoid(
        self.get_left_tip(self.arm_angle) + DOWN * self.plate_offset, RED
    )
    self.right_plate = trapezoid(
        self.get_right_tip(self.arm_angle) + DOWN * self.plate_offset, GREEN
    )

    self.left_chain = Line(
        start=self.get_left_tip(self.arm_angle),
        end=self.left_plate.get_top(), color=GRAY)
    self.right_chain = Line(
        start=self.get_right_tip(self.arm_angle),
        end=self.right_plate.get_top(), color=GRAY)

    self.weight_bad = Circle(
        radius=0.014 * s, fill_opacity=1, color=RED
    )
    self.weight_good = Circle(
        radius=0.022 * s, fill_opacity=1, color=GREEN
    )

    self.elements = VGroup(
        base_triangle, support, pivot,
        self.left_chain, self.right_chain,
        self.left_plate, self.right_plate,
        self.arm
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
    self.add(self.elements, self.arm)
    self.wait(duration)

def drop_bad_weight(self, duration=1.0):
    appear_time = 0.4 * duration
    settle_time = 0.2 * duration
    tilt_time = 0.4 * duration

    if self.weight_bad not in self.mobjects:
        self.add(self.weight_bad)
        self.weight_bad.move_to(self.left_plate.get_center() + UP * 0.022 * self.base_scale)
        self.weight_bad.scale(0.6)
        self.weight_bad.set_opacity(0)

    self.play(
        self.weight_bad.animate.set_opacity(1).scale(2.0),
        rate_func=overshoot,
        run_time=appear_time
    )
    self.play(
        self.weight_bad.animate.scale(0.5),
        rate_func=smooth,
        run_time=settle_time
    )
    rotate_arm_to(self, self.left_tilt_angle, duration=tilt_time)

def drop_good_weight(self, duration=1.2):
    appear_time = 0.3 * duration
    settle_time = 0.1 * duration
    tilt_time = 0.6 * duration

    if self.weight_good not in self.mobjects:
        self.add(self.weight_good)
        self.weight_good.move_to(self.right_plate.get_center() + UP * 0.022 * self.base_scale)
        self.weight_good.scale(0.6)
        self.weight_good.set_opacity(0)

    self.play(
        self.weight_good.animate.set_opacity(1).scale(2.0),
        rate_func=overshoot,
        run_time=appear_time
    )
    self.play(
        self.weight_good.animate.scale(0.5),
        rate_func=smooth,
        run_time=settle_time
    )
    rotate_arm_to(self, self.right_tilt_angle, duration=tilt_time)

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
        rate_func=smooth,
        run_time=fade_time
    )
    self.remove(self.weight_good)
    rotate_arm_to(self, self.left_tilt_angle, duration=tilt_time)

def prepare_transition(self, duration=0.8):
    self.play(
        FadeOut(self.weight_bad),
        FadeOut(self.arm),
        FadeOut(self.elements),
        run_time=duration
    )
    self.wait(0.3)

# === Debug Scene ===
class DebugBalanceScene(Scene):
    def construct(self):
        create_balance(self)
        show_balance(self)
        drop_bad_weight(self)
        drop_good_weight(self)
        remove_good_weight(self)
        prepare_transition(self)
