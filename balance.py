from manim import *
import numpy as np

# === Manim render config ===
config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 18
config.frame_height = 32
config.background_color = None


def create_balance(self):
    # Scaling based on screen
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

    # === CENTERED BASE ===
    # We'll build upward from the bottom to ORIGIN
    base_bottom = ORIGIN - UP * (base_triangle_height + self.support_height)

    # Base triangle
    base_triangle = Polygon(
        LEFT * base_triangle_width / 2 + DOWN * base_triangle_height,
        RIGHT * base_triangle_width / 2 + DOWN * base_triangle_height,
        ORIGIN,
        color=GRAY, fill_color=GRAY, fill_opacity=1
    ).shift(base_bottom)

    # Support column
    support = Rectangle(
        height=self.support_height,
        width=support_width,
        color=GRAY, fill_color=GRAY, fill_opacity=1
    ).next_to(base_triangle.get_top(), UP, buff=0)

    self.pivot_point = support.get_top()
    pivot = Dot(point=self.pivot_point, radius=0.005 * s, color=ORANGE)

    # Arm
    self.arm = Rectangle(
        height=arm_thickness,
        width=arm_length,
        color=GRAY, fill_color=GRAY, fill_opacity=1
    ).move_to(self.pivot_point)

    # Tip position helpers
    def get_left_tip(angle): return self.pivot_point + rotate_vector(LEFT * arm_length / 2, angle)
    def get_right_tip(angle): return self.pivot_point + rotate_vector(RIGHT * arm_length / 2, angle)
    self.get_left_tip = get_left_tip
    self.get_right_tip = get_right_tip

    # Trapezoid plate shape
    def trapezoid(center, color):
        top_left = center + UP * plate_height / 2 + LEFT * plate_width_top / 2
        top_right = center + UP * plate_height / 2 + RIGHT * plate_width_top / 2
        bottom_right = center + DOWN * plate_height / 2 + RIGHT * plate_width_bottom / 2
        bottom_left = center + DOWN * plate_height / 2 + LEFT * plate_width_bottom / 2
        return Polygon(top_left, top_right, bottom_right, bottom_left,
                       color=BLACK, fill_color=color, fill_opacity=0.6)

    # Plates attached to arm tips
    self.left_plate = always_redraw(lambda: trapezoid(
        self.get_left_tip(self.arm_angle) + DOWN * self.plate_offset, RED
    ))
    self.right_plate = always_redraw(lambda: trapezoid(
        self.get_right_tip(self.arm_angle) + DOWN * self.plate_offset, GREEN
    ))

    # Chains
    left_chain = always_redraw(lambda: Line(
        start=self.get_left_tip(self.arm_angle),
        end=self.left_plate.get_top(), color=GRAY))
    right_chain = always_redraw(lambda: Line(
        start=self.get_right_tip(self.arm_angle),
        end=self.right_plate.get_top(), color=GRAY))

    # Weights
    self.weight_bad = always_redraw(lambda: Circle(
        radius=0.014 * s, fill_opacity=1, color=RED
    ).move_to(self.left_plate.get_center() + UP * 0.022 * s))

    self.weight_good = always_redraw(lambda: Circle(
        radius=0.022 * s, fill_opacity=1, color=GREEN
    ).move_to(self.right_plate.get_center() + UP * 0.022 * s))

    # Group all elements for transitions
    self.elements = VGroup(
        base_triangle, support, pivot,
        left_chain, right_chain,
        self.left_plate, self.right_plate,
        self.arm
    )


# === Arm rotation with update ===
def rotate_arm_to(self, target_angle, duration):
    start_angle = self.arm_angle

    def updater(mob, dt):
        t = min(1, (self.time - start_time) / duration)
        new_angle = interpolate(start_angle, target_angle, t)
        diff = new_angle - self.arm_angle
        mob.rotate(diff, about_point=self.pivot_point)
        self.arm_angle = new_angle

    start_time = self.time
    self.arm.add_updater(updater)
    self.wait(duration)
    self.arm.remove_updater(updater)
    self.arm_angle = target_angle


# === Animation steps ===

def show_balance(self):
    self.add(self.elements)
    self.wait(0.3)

def drop_bad_weight(self):
    self.add(self.weight_bad)
    rotate_arm_to(self, self.left_tilt_angle, duration=0.8)

def drop_good_weight(self):
    self.add(self.weight_good)
    rotate_arm_to(self, self.right_tilt_angle, duration=1.0)

def remove_good_weight(self):
    self.remove(self.weight_good)
    rotate_arm_to(self, self.left_tilt_angle, duration=0.8)

def prepare_transition(self):
    self.play(
        FadeOut(self.weight_bad),
        FadeOut(self.arm),
        FadeOut(self.elements)
    )
    self.wait(0.3)


# === Debug scene ===

class DebugBalanceScene(Scene):
    def construct(self):
        create_balance(self)

        show_balance(self)
        self.wait(0.5)

        drop_bad_weight(self)
        self.wait(0.5)

        drop_good_weight(self)
        self.wait(1.0)

        remove_good_weight(self)
        self.wait(0.5)

        prepare_transition(self)
