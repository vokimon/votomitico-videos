from manim import *

def zoom_on_rests(self, emitter_idx=2, receiver_idx=1):
    axis_percent = 0.08
    xmargin_pct = self.xmargin_pct
    xmargin = xmargin_pct * config.frame_width
    safe_width = config.frame_width * (1 - 2 * xmargin_pct)

    canvas_side = safe_width
    self.add(Rectangle(width=canvas_side, height=canvas_side).move_to([0, 0, 0]))

    def create_rest_overlay(party_index):
        votes = self.parties[party_index][1]
        color = self.parties[party_index][0]
        seats_won = len(self.seat_groups[party_index])
        votes_used = seats_won * self.final_price
        rest_votes = votes - votes_used

        bar = self.bar_group[party_index]
        bar_y = bar.get_center()[1]

        rest_width = self.votes2x.scale(rest_votes)
        height = self.bar_height

        rect = Rectangle(
            width=rest_width,
            height=height,
            fill_color=color,
            fill_opacity=1.0,
            stroke_color=WHITE,
            stroke_width=2,
        )
        rect.align_to(bar, RIGHT)
        rect.move_to([rect.get_center()[0], bar_y, 0])

        guide_line = Line(
            start=rect.get_left() + UP * (height / 2 + 0.15),
            end=rect.get_left() + DOWN * (height / 2 + 0.15),
            stroke_color=WHITE,
            stroke_width=4,
        )

        next_price_votes = self.final_price * (seats_won + 1)
        next_price_x = self.votes2x(next_price_votes)
        next_price_line = Line(
            start=[next_price_x, bar_y + height / 2 + 0.15, 0],
            end=[next_price_x, bar_y - height / 2 - 0.15, 0],
            stroke_color=WHITE,
            stroke_width=4,
            stroke_opacity=0.25,
        )

        overlay = VGroup(rect, guide_line, next_price_line)
        left_edge = rect.get_left()
        for m in overlay:
            m.shift(-left_edge)
        overlay.move_to([left_edge[0], bar_y, 0], aligned_edge=LEFT)
        return overlay

    emitter_overlay = create_rest_overlay(emitter_idx)
    receiver_overlay = create_rest_overlay(receiver_idx)

    self.add(emitter_overlay, receiver_overlay)

    fade_group = VGroup(
        *self.bar_group,
        *[seat for group in self.seat_groups for seat in group],
        *[line_and_label for _, line_and_label in self.price_lines],
        self.available_label,
        self.available_count,
        self.distributed_label,
        self.distributed_count,
    )

    self.play(fade_group.animate.set_opacity(0.2), run_time=1.5)
    self.wait(0.5)

    # Escalado horizontal común
    overlay_width = emitter_overlay.width
    overlay_height = emitter_overlay.height
    scale = [
        (safe_width * (1 - axis_percent)) / overlay_width,
        (safe_width * axis_percent) / overlay_height,
        0,
    ]

    # Posiciones finales en el canvas cuadrado
    half_safe = safe_width / 2
    offset = safe_width * axis_percent / 2

    emitter_target_pos = [
        -half_safe + (safe_width * (1 - axis_percent)) / 2,
        -offset,
        0,
    ]

    receiver_target_pos = [
        half_safe - offset,
        offset,
        0,
    ]

    # Fase 1: Escalado proporcional y movimiento
    self.play(
        emitter_overlay.animate.scale(scale).move_to(emitter_target_pos),
        receiver_overlay.animate.scale(scale).move_to(receiver_target_pos),
        receiver_overlay.animate.rotate(PI / 2),
        fade_group.animate.set_opacity(0),
        run_time=2.0,
        rate_func=smooth,
    )

    self.wait(0.5)
