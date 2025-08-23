from manim import *

def under_p_transfers(self, emitter_idx=2, receiver_idx=1):
    prepare_rest_plot_axes(self, emitter_idx, receiver_idx)
    draw_gain_zone(self)
    draw_loss_zone(self)
    rest_uncertainty(self)

def _get_x(self, alpha):
    left = self.emitter_overlay.get_corner(LEFT + DOWN)
    right = self.emitter_overlay.get_corner(RIGHT + DOWN)
    return interpolate(left, right, alpha)[0]

def _get_y(self, alpha):
    bottom = self.receiver_overlay.get_corner(DOWN + LEFT)
    top = self.receiver_overlay.get_corner(UP + LEFT)
    return interpolate(bottom, top, alpha)[1]

def get_mercury_x(self):
    return self.emitter_overlay[1].width / self.emitter_overlay[0].width

def get_mercury_y(self):
    return self.receiver_overlay[1].height / self.receiver_overlay[0].height

def _labeled_zone(self, x_min, x_max, y_min, y_max, color, text):
    x0 = _get_x(self, x_min)
    x1 = _get_x(self, x_max)
    y0 = _get_y(self, y_min)
    y1 = _get_y(self, y_max)

    width = abs(x1 - x0)
    height = abs(y1 - y0)
    center = np.array([(x0 + x1) / 2, (y0 + y1) / 2, 0])

    rect = Rectangle(
        width=width,
        height=height,
        fill_color=color,
        fill_opacity=0.4,
        stroke_width=0,
    ).move_to(center)

    label = Text(text, color=WHITE).scale(0.5).move_to(center)
    return rect, label

def _animate_mercury_y_to(self, value):
    bar = self.receiver_overlay[1]
    overlay = self.receiver_overlay
    max_height = overlay.height
    base = bar.get_bottom()

    return bar.animate.stretch_to_fit_height(max_height * value).move_to(base, aligned_edge=DOWN)

def _animate_mercury_x_to(self, value):
    bar = self.emitter_overlay[1]
    overlay = self.emitter_overlay
    max_width = overlay.width
    base = bar.get_left()

    return bar.animate.stretch_to_fit_width(max_width * value).move_to(base, aligned_edge=LEFT)


def prepare_rest_plot_axes(self, emitter_idx=2, receiver_idx=1):
    axis_percent = 0.08
    xmargin_pct = self.xmargin_pct
    safe_width = config.frame_width * (1 - 2 * xmargin_pct)

    canvas_side = safe_width
    emitter_overlay = _create_rest_overlay(self, emitter_idx)
    receiver_overlay = _create_rest_overlay(self, receiver_idx)
    self.emitter_overlay = emitter_overlay
    self.receiver_overlay = receiver_overlay
    self.add(emitter_overlay, receiver_overlay)

    fade_group = VGroup(
        *self.bar_group,
        *[seat for group in self.seat_groups for seat in group],
        *[line_and_label for _, line_and_label in self.price_lines],
        self.seats_label,
        self.distributed_count,
    )

    self.play(fade_group.animate.set_opacity(0.0), run_time=1.5)

    overlay_width = emitter_overlay.width
    overlay_height = emitter_overlay.height
    scale_x = (safe_width * (1 - axis_percent)) / overlay_width
    scale_y = (safe_width * axis_percent) / overlay_height

    half_safe = safe_width / 2
    offset = safe_width * axis_percent / 2

    emitter_target_pos = [
        -half_safe + (safe_width * (1 - axis_percent)) / 2,
        -half_safe + offset,
        0,
    ]
    receiver_target_pos = [
        half_safe - offset,
        offset,
        0,
    ]

    self.play(
        emitter_overlay.animate.move_to(emitter_target_pos),
        receiver_overlay.animate.rotate(PI / 2).move_to(receiver_target_pos),
        run_time=1.0,
        rate_func=smooth,
    )

    self.play(
        emitter_overlay.animate.scale([scale_x, scale_y, 1]),
        receiver_overlay.animate.scale([scale_y, scale_x, 1]),
        run_time=0.5,
        rate_func=smooth,
    )

    self.to_delete[:] = [emitter_overlay, receiver_overlay]

    # Save scale info and helper functions
    self.get_x = lambda alpha: interpolate(
        emitter_overlay.get_corner(LEFT + DOWN),
        emitter_overlay.get_corner(RIGHT + DOWN),
        alpha
    )[0]
    self.get_y = lambda alpha: interpolate(
        receiver_overlay.get_corner(DOWN + LEFT),
        receiver_overlay.get_corner(UP + LEFT),
        alpha
    )[1]
    self.get_point = lambda x_alpha, y_alpha: np.array([
        self.get_x(x_alpha), self.get_y(y_alpha), 0
    ])

    N = 0.32
    self.n_tracker = ValueTracker(N)

    def hbar_label(bar, text, factor):
        margin = 0.2
        left = bar.get_corner(DOWN + LEFT)
        right = bar.get_corner(DOWN + RIGHT)
        label_point = interpolate(left, right, factor)
        label = Text(text)
        label.move_to(label_point + margin * DOWN)
        label.shift(DOWN * label.height / 2)
        return label

    def vbar_label(bar, text, factor):
        margin = 0.2
        bottom = bar.get_corner(RIGHT + DOWN)
        top = bar.get_corner(RIGHT + UP)
        label_point = interpolate(bottom, top, factor)
        label = Text(text)
        label.move_to(label_point + margin * RIGHT)
        label.shift(RIGHT * label.width / 2)
        return label

    emitter_zero = hbar_label(emitter_overlay, "0", 0)
    emitter_crit = hbar_label(emitter_overlay, "N", N)
    emitter_full = hbar_label(emitter_overlay, "P", 1)
    receiver_zero = vbar_label(receiver_overlay, "0", 0)
    receiver_crit = vbar_label(receiver_overlay, "P-N", 1 - N)
    receiver_full = vbar_label(receiver_overlay, "P", 1)
    # They appear later
    self.emitter_crit = emitter_crit
    self.receiver_crit = receiver_crit

    self.add(emitter_zero, emitter_full, receiver_zero, receiver_full)
    self.to_delete.add(emitter_zero, emitter_full, receiver_zero, receiver_full)
    add_scenario_point(self)


def draw_gain_zone(self, duration=4):
    N = self.n_tracker.get_value()

    # Duraciones relativas (suman 1)
    initial_phase_time = 0.25 * duration
    oscillation_time = 0.15 * duration
    final_phase_time = 0.6 * duration

    # Coordenadas verticales (eje receptor vertical)
    y_0 = _get_y(self, 0)
    y_p = _get_y(self, 1)
    y_p_n = _get_y(self, 1 - N)

    # Barra original del receptor
    old_mercury_bar = self.receiver_overlay[1]
    base = old_mercury_bar.get_corner(DOWN)

    # Cota vertical N
    brace = BraceBetweenPoints(
        [_get_x(self, 1), y_p_n, 0],
        [_get_x(self, 1), y_p, 0],
        direction=LEFT,
        color=WHITE,
        sharpness=0.3,
    )
    n_label = Text("N", font_size=80, color=WHITE).next_to(brace, LEFT, buff=0.15)

    # Fase 1: aparición cota y subida
    self.play(
        AnimationGroup(
            FadeIn(self.receiver_crit),
            FadeIn(brace),
            FadeIn(n_label),
            _animate_mercury_y_to(self, 1),
        ),
        run_time=initial_phase_time,
    )
    self.add(brace, n_label)

    # Fase 2: oscilación (bajar a P-N, subir a mitad)
    self.play(
        Succession(
            _animate_mercury_y_to(self, 1-N),
            _animate_mercury_y_to(self, 1-N/2),
        ),
        run_time=oscillation_time,
    )

    # Fase 3: desaparición cota y aparición zona verde
    green_target, _ = _labeled_zone(
        self,
        x_min=0,
        x_max=1,
        y_min=1 - N,
        y_max=1,
        color=GREEN,
        text="",
    )
    green_rect = green_target.copy().stretch_to_fit_width(0, about_edge=RIGHT)

    self.play(
        AnimationGroup(
            FadeOut(brace),
            FadeOut(n_label),
            Transform(green_rect, green_target),
            lag_ratio=0.0,
        ),
        run_time=final_phase_time,
    )

    self.add(green_rect)
    self.to_delete.add(green_rect, self.receiver_crit)


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
    p_width = self.votes2x.scale(price)
    background_bar = Rectangle(
        width=p_width,
        height=height+.3,
        fill_color=background_color,
        fill_opacity=1.0,
        stroke_color=background_color,
        stroke_width=5,
    ).move_to([center_x, bar_y, 0])

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


def add_scenario_point(self):

    def point_position(self, x=None, y=None):
        return [
            _get_x(self, get_mercury_x(self) if x is None else x),
            _get_y(self, get_mercury_y(self) if y is None else y),
            0,
        ]

    def update_point(mob):
        return mob.move_to(point_position(self))

    def update_line_x(mob):
        return mob.become(Line(point_position(self), point_position(self, y=0), color=BLUE))

    def update_line_y(mob):
        return mob.become(Line(point_position(self), point_position(self, x=1), color=BLUE))

    self.line_x = Line(point_position(self), point_position(self, y=0), color=BLUE)
    self.line_y = Line(point_position(self), point_position(self, x=1), color=BLUE)
    self.point = Dot(radius=0.2, color=YELLOW).move_to(point_position(self))

    self.point.add_updater(update_point)
    self.line_x.add_updater(update_line_x)
    self.line_y.add_updater(update_line_y)
    self.add(self.point, self.line_x, self.line_y)
    self.to_delete.add(self.point, self.line_x, self.line_y)

def remove_scenario_point(self):
    self.point.clear_updaters()
    self.line_x.clear_updaters()
    self.line_y.clear_updaters()
    self.remove(self.point, self.line_x, self.line_y)
    self.to_delete.remove(self.point, self.line_x, self.line_y)
    del self.point
    del self.line_x
    del self.line_y


def draw_loss_zone(self, duration=4):
    N = self.n_tracker.get_value()

    # Fases temporales
    initial_phase_time = 0.25 * duration
    oscillation_time = 0.15 * duration
    final_phase_time = 0.6 * duration

    # Coordenadas
    x_0 = _get_x(self, 0)
    x_n = _get_x(self, N)
    y = _get_y(self, 0)

    # Barra de "mercurio" horizontal (emisor)
    mercury_bar = self.emitter_overlay[1]
    base = mercury_bar.get_left()


    # Brace entre 0 y N
    brace = BraceBetweenPoints(
        [x_0, y, 0],
        [x_n, y, 0],
        direction=UP,
        color=WHITE,
        sharpness=0.3,
    )
    n_label = Text("N", font_size=80, color=WHITE).next_to(brace, UP, buff=0.15)

    # Fase 1: aparición brace, crit y subida inicial 0 → N
    self.play(
        AnimationGroup(
            FadeIn(self.emitter_crit),
            FadeIn(brace),
            FadeIn(n_label),
            _animate_mercury_x_to(self, 0.01), # avoid 0, breaks later resizing
            lag_ratio=0.0,
        ),
        run_time=initial_phase_time,
    )
    self.add(brace, n_label)
    self.to_delete.add(brace, n_label)

    self.play(
        Succession(
            _animate_mercury_x_to(self, N),
            _animate_mercury_x_to(self, N/2),
        ),
        run_time=oscillation_time,
    )

    # Fase 3: desaparición brace + aparición zona crítica roja
    red_target, _ = _labeled_zone(
        self,
        x_min=0,
        x_max=N,
        y_min=0,
        y_max=1,
        color=RED,
        text="",
    )
    self.red_rect = red_target.copy().stretch_to_fit_height(0, about_edge=DOWN)

    self.play(
        AnimationGroup(
            FadeOut(brace),
            FadeOut(n_label),
            Transform(self.red_rect, red_target),
            lag_ratio=0.0,
        ),
        run_time=final_phase_time,
    )

    self.add(self.red_rect)
    self.to_delete.add(self.red_rect, self.emitter_crit)

def rest_uncertainty(self, duration=2):
    self.play(
        Succession(
            AnimationGroup(
                _animate_mercury_x_to(self, 0.3),
                _animate_mercury_y_to(self, 0.8),
            ),
            AnimationGroup(
                _animate_mercury_x_to(self, 0.7),
                _animate_mercury_y_to(self, 0.5),
            ),
            AnimationGroup(
                _animate_mercury_x_to(self, 0.2),
                _animate_mercury_y_to(self, 0.3),
            ),
            AnimationGroup(
                _animate_mercury_x_to(self, 0.8),
                _animate_mercury_y_to(self, 0.9),
            ),
        ),
        run_time=duration,
    )


class DebugScene(Scene):
    from visualdhondt import visual_dhondt, highlight_rests_and_fraction
    from manim_utils import add_background, the_end
    def construct(self):
        self.add_background()
        self.to_delete = VGroup()
        self.visual_dhondt()
        self.highlight_rests_and_fraction()
        under_p_transfers(self)
        self.the_end()
