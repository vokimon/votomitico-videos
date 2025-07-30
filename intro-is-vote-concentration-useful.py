from manim import *
import numpy as np
import random
import tempfile
import os
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from manim_utils import (
    overshoot,
    add_background,
    show_caption,
)

config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 18 # 9
config.frame_height = 32     # 16
config.background_color = None

class IsVoteConcentrationUseful(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService(lang="es", global_speed=1.4))

        with self.voiceover(text=
            "¿Es útil concentrar el voto en el partido más grande?"
        ):
            self.init_params()
            add_background(self)
            self.create_bars()
            self.animate_source_squash_stretch()
            self.animate_splinters()
            self.update_target_bar()
            self.animate_target_compression()
            self.animate_question_mark()
            self.wait(2)

    def init_params(self):
        self.source_color = RED
        self.target_color = BLUE
        self.bar_width = 2
        self.source_total_height = 4.0
        self.extracted_height = 1.0
        self.num_splinters = 5
        self.splinter_height = self.extracted_height / self.num_splinters
        self.source_remaining_height = self.source_total_height - self.extracted_height
        self.target_initial_height = 6.0
        self.target_final_height = self.target_initial_height + self.extracted_height
        self.base_y = -3
        self.source_pos = LEFT * 3
        self.target_pos = RIGHT * 3
        self.parabola_time = 0.7

        dx = abs(self.target_pos[0] - self.source_pos[0])
        impulse_fraction = 0.2
        self.release_time = self.parabola_time * (self.bar_width * impulse_fraction) / dx
        self.retract_time = 0.2

    def create_bars(self):
        self.source_bar = Rectangle(
            width=self.bar_width, height=self.source_total_height,
            color=self.source_color, fill_opacity=1
        ).move_to(self.source_pos).align_to([0, self.base_y, 0], DOWN)

        self.target_bar = Rectangle(
            width=self.bar_width, height=self.target_initial_height,
            color=self.target_color, fill_opacity=1
        ).move_to(self.target_pos).align_to([0, self.base_y, 0], DOWN)

        self.add(self.source_bar, self.target_bar)
        self.wait(0.5)

    def animate_source_squash_stretch(self):
        bottom = self.source_bar.get_bottom()
        scale_y = 0.85
        scale_x = 1 / scale_y

        self.play(
            self.source_bar.animate.stretch(scale_x, 0).stretch(scale_y, 1).move_to(bottom, aligned_edge=DOWN),
            run_time=self.retract_time
        )
        self.play(
            self.source_bar.animate.stretch(1 / scale_x, 0).stretch(1 / scale_y, 1).move_to(bottom, aligned_edge=DOWN),
            run_time=self.release_time
        )

        self.source_bar_cut = Rectangle(
            width=self.bar_width,
            height=self.source_remaining_height,
            color=self.source_color,
            fill_opacity=1
        ).move_to(self.source_pos).align_to([0, self.base_y, 0], DOWN)

        self.remove(self.source_bar)
        self.add(self.source_bar_cut)

    def animate_splinters(self):
        self.moving_splinters = []
        animations = []

        for i in range(self.num_splinters):
            offset_x = random.uniform(-0.15, 0.15)
            y_offset = self.source_remaining_height + self.splinter_height / 2 + i * self.splinter_height
            start = self.source_bar_cut.get_bottom() + UP * y_offset
            y_final = self.target_bar.get_height() + self.splinter_height / 2 + i * self.splinter_height
            end = self.target_bar.get_bottom() + UP * y_final
            parabola_height = 3.5 + i * 0.3
            mid = (start + end) / 2 + UP * parabola_height + RIGHT * offset_x
            path = VMobject().set_points_smoothly([start, mid, end])

            splinter = Rectangle(
                width=self.bar_width, height=self.splinter_height,
                color=self.source_color, fill_opacity=1
            ).move_to(start)

            self.moving_splinters.append(splinter)
            self.add(splinter)

            anim = MoveAlongPath(splinter, path, run_time=self.parabola_time, rate_func=smooth)
            animations.append(anim)

        self.play(*animations, lag_ratio=0.15)

    def update_target_bar(self):
        for sp in self.moving_splinters:
            self.remove(sp)
        self.remove(self.target_bar)

        self.target_bar_final = Rectangle(
            width=self.bar_width, height=self.target_final_height,
            color=self.target_color, fill_opacity=1
        ).move_to(self.target_pos).align_to([0, self.base_y, 0], DOWN)

        self.add(self.target_bar_final)

    def animate_target_compression(self):
        scale_y = 0.92
        scale_x = 1 / scale_y
        base = self.target_bar_final.get_bottom()[1]
        new_height = self.target_bar_final.height * scale_y

        self.target_bar_final.generate_target()
        self.target_bar_final.target.stretch(scale_x, 0)
        self.target_bar_final.target.stretch(scale_y, 1)
        self.target_bar_final.target.move_to([self.target_pos[0], base + new_height / 2, 0])
        self.play(MoveToTarget(self.target_bar_final), run_time=0.25)

        self.target_bar_final.generate_target()
        self.target_bar_final.target.stretch(1 / scale_x, 0)
        self.target_bar_final.target.stretch(1 / scale_y, 1)
        self.target_bar_final.target.move_to([self.target_pos[0], base + self.target_final_height / 2, 0])
        self.play(MoveToTarget(self.target_bar_final), run_time=0.25)

    def animate_question_mark(self):
        q = Text("?", color=YELLOW, stroke_width=8, stroke_color=ORANGE).scale(0.1)
        center = (self.source_pos + self.target_pos) / 2 + UP * 0.5
        q.move_to(center)
        q.set_opacity(0)
        self.add(q)
        self.play(
            FadeIn(q),
            q.animate.scale(200.0).set_opacity(1),
            run_time=0.6,
            rate_func=overshoot
        )
        self.play(q.animate.scale(0.95), run_time=0.2, rate_func=smooth)
