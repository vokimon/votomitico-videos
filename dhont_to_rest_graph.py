from manim import *

def _create_rest_overlay(self, party_index):
    votes = self.parties[party_index][1]
    color = self.parties[party_index][0]
    seats_won = len(self.seat_groups[party_index])
    votes_used = seats_won * self.final_price
    rest_votes = votes - votes_used

    bar = self.bar_group[party_index]
    bar_y = bar.get_center()[1]

    height = self.bar_height
    price = self.final_price

    # Posición centro del bloque de fondo negro (entre escaño s y s+1)
    center_vote_value = price * (seats_won + 0.5)
    center_x = self.votes2x(center_vote_value)

    background_color = "#622"
    # Fondo negro de ancho P
    p_width = self.votes2x.scale(price)
    background_bar = Rectangle(
        width=p_width,
        height=height+.3,
        fill_color=background_color,
        fill_opacity=1.0,
        stroke_color=background_color,
        stroke_width=5,
    ).move_to([center_x, bar_y, 0])

    # Resto encima, alineado a la izquierda del bloque
    rest_width = self.votes2x.scale(rest_votes)
    rect = Rectangle(
        width=rest_width,
        height=height,
        fill_color=color,
        fill_opacity=1.0,
        stroke_color=None,
        stroke_width=0,
    ).align_to(background_bar, LEFT).set_y(bar_y)

    overlay = VGroup(background_bar, rect)
    return overlay


def zoom_on_rests(self, emitter_idx=2, receiver_idx=1):
    axis_percent = 0.08
    xmargin_pct = self.xmargin_pct
    safe_width = config.frame_width * (1 - 2 * xmargin_pct)

    canvas_side = safe_width
    debug_margin = Rectangle(width=canvas_side, height=canvas_side).move_to([0, 0, 0])
    self.add(debug_margin)

    emitter_overlay = _create_rest_overlay(self, emitter_idx)
    receiver_overlay = _create_rest_overlay(self, receiver_idx)
    self.add(emitter_overlay, receiver_overlay)

    fade_group = VGroup(
        *self.bar_group,
        *[seat for group in self.seat_groups for seat in group],
        *[line_and_label for _, line_and_label in self.price_lines],
        self.seats_label,
        self.distributed_count,
    )

    self.play(fade_group.animate.set_opacity(0.0), run_time=1.5)

    # Escalado objetivo
    overlay_width = emitter_overlay.width
    overlay_height = emitter_overlay.height
    scale_x = (safe_width * (1 - axis_percent)) / overlay_width
    scale_y = (safe_width * axis_percent) / overlay_height

    half_safe = safe_width / 2
    offset = safe_width * axis_percent / 2

    emitter_target_pos = [
        -half_safe + (safe_width * (1 - axis_percent)) / 2,
        -half_safe +offset,
        0,
    ]

    receiver_target_pos = [
        half_safe - offset,
        offset,
        0,
    ]

    # Fase 1: traslación + rotación receptor
    self.play(
        emitter_overlay.animate.move_to(emitter_target_pos),
        receiver_overlay.animate.rotate(PI / 2).move_to(receiver_target_pos),
        run_time=1.0,
        rate_func=smooth,
    )

    # Fase 2: escalado con ejes invertidos en receptor
    self.play(
        emitter_overlay.animate.scale([scale_x, scale_y, 1]),
        receiver_overlay.animate.scale([scale_y, scale_x, 1]),  # ejes invertidos
        fade_group.animate.set_opacity(0.0),
        run_time=0.5,
        rate_func=smooth,
    )
    self.to_delete[:] = [
        emitter_overlay,
        receiver_overlay,
        debug_margin,
    ]

