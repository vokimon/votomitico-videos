from manim import *
import numpy as np

# === Scene Configuration ===
config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 18
config.frame_height = 32
config.background_color = None


class ProceduralBalanceScene(Scene):
    def construct(self):
        # === Scene Parameters ===
        support_height = 3
        arm_length = 6
        arm_thickness = 0.25
        support_width = 0.3
        plate_height = 0.6
        plate_width_top = 1.6
        plate_width_bottom = 1.0
        plate_offset = 1.5  # vertical offset from arm tip

        # === Tilt angles ===
        left_tilt_angle = 0.3    # radians, arm tilted left (blue weight)
        right_tilt_angle = -0.4  # radians, arm tilted right (red + blue weights)

        # === Create Support and Pivot ===
        support = Rectangle(
            height=support_height,
            width=support_width,
            color=GRAY,
            fill_color=GRAY,
            fill_opacity=1
        ).move_to(DOWN * 6 + UP * support_height / 2)

        pivot_point = support.get_top()
        pivot = Dot(point=pivot_point, radius=0.1, color=ORANGE)

        # === Create Arm ===
        arm = Rectangle(
            height=arm_thickness,
            width=arm_length,
            color=GRAY,
            fill_color=GRAY,
            fill_opacity=1
        ).move_to(pivot_point)

        # Track arm rotation angle
        arm_angle = 0

        # === Trapezoidal Plate Shape ===
        def create_trapezoid(center, color):
            top_left = center + UP * plate_height / 2 + LEFT * plate_width_top / 2
            top_right = center + UP * plate_height / 2 + RIGHT * plate_width_top / 2
            bottom_right = center + DOWN * plate_height / 2 + RIGHT * plate_width_bottom / 2
            bottom_left = center + DOWN * plate_height / 2 + LEFT * plate_width_bottom / 2
            return Polygon(top_left, top_right, bottom_right, bottom_left,
                           color=BLACK, fill_color=color, fill_opacity=0.6)

        # === Functions to Compute Arm Tip Positions ===
        def get_left_tip(angle):
            dx = -arm_length / 2 * np.cos(angle)
            dy = -arm_length / 2 * np.sin(angle)
            return pivot_point + np.array([dx, dy, 0])

        def get_right_tip(angle):
            dx = arm_length / 2 * np.cos(angle)
            dy = arm_length / 2 * np.sin(angle)
            return pivot_point + np.array([dx, dy, 0])

        # === Plates Attached Below Arm Tips ===
        left_plate = always_redraw(lambda: create_trapezoid(
            get_left_tip(arm_angle) + DOWN * plate_offset,
            BLUE
        ))
        right_plate = always_redraw(lambda: create_trapezoid(
            get_right_tip(arm_angle) + DOWN * plate_offset,
            RED
        ))

        # === Chains from Arm Tips to Plates ===
        left_chain = always_redraw(lambda: Line(
            start=get_left_tip(arm_angle),
            end=left_plate.get_top(),
            color=GRAY
        ))
        right_chain = always_redraw(lambda: Line(
            start=get_right_tip(arm_angle),
            end=right_plate.get_top(),
            color=GRAY
        ))

        # === Group and Add to Scene ===
        static_parts = VGroup(support, pivot, left_chain, right_chain, left_plate, right_plate)
        self.add(static_parts, arm)

        # === Weights (Circles) That Follow Plates ===
        weight_left = always_redraw(lambda: Circle(radius=0.25, fill_opacity=1, color=BLUE)
                                    .move_to(left_plate.get_center() + UP * 0.4))

        # 🔴 Larger red weight to represent "voto útil"
        weight_right = always_redraw(lambda: Circle(radius=0.4, fill_opacity=1, color=RED)
                                     .move_to(right_plate.get_center() + UP * 0.4))

        # === Function to rotate arm to a target angle smoothly ===
        def rotate_arm_to(target_angle, duration):
            nonlocal arm_angle
            start_angle = arm_angle
            def updater(mob, dt):
                nonlocal arm_angle
                t = min(1, (self.time - start_time) / duration)
                new_angle = start_angle + t * (target_angle - start_angle)
                diff = new_angle - arm_angle
                mob.rotate(diff, about_point=pivot_point)
                arm_angle = new_angle
            start_time = self.time
            arm.add_updater(updater)
            self.wait(duration)
            arm.remove_updater(updater)
            # Correct any tiny numeric drift
            diff = target_angle - arm_angle
            if abs(diff) > 1e-5:
                arm.rotate(diff, about_point=pivot_point)
                arm_angle = target_angle

        # === Animate sequence ===

        # 1. Add blue weight, rotate arm to left_tilt_angle quickly
        self.add(weight_left)
        rotate_arm_to(left_tilt_angle, duration=1.0)

        # 2. Add red weight immediately and rotate arm to right_tilt_angle smoothly
        self.add(weight_right)
        rotate_arm_to(right_tilt_angle, duration=1.5)

        # 3. Remove red weight and rotate arm back to left_tilt_angle smoothly
        self.remove(weight_right)
        rotate_arm_to(left_tilt_angle, duration=1.0)

        # === Clean Up ===
        self.play(FadeOut(weight_left), FadeOut(arm), FadeOut(static_parts))
        self.wait()
