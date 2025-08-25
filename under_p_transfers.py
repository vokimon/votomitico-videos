from manim import *

def under_p_transfers(self, emitter_idx=2, receiver_idx=1):
    prepare_rest_plot_axes(self, emitter_idx, receiver_idx)
    rest_uncertainty(self)
    draw_gain_zone(self)
    draw_loss_zone(self)
    draw_results(self)
    animate_n(self)

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

    def emitter_crit_updater(mob):
        N = self.n_tracker.get_value()
        pos = mob.get_center()
        pos[0] = _get_x(self, N)
        mob.move_to(pos)
    emitter_crit.add_updater(emitter_crit_updater)
    def receiver_crit_updater(mob):
        N = self.n_tracker.get_value()
        pos = mob.get_center()
        pos[1] = _get_y(self, 1-N)
        mob.move_to(pos)
    receiver_crit.add_updater(receiver_crit_updater)

    self.add(emitter_zero, emitter_full, receiver_zero, receiver_full)
    self.to_delete.add(emitter_zero, emitter_full, receiver_zero, receiver_full)
    add_scenario_point(self)



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
    self.add(self.line_x, self.line_y, self.point)
    self.to_delete.add(self.line_x, self.line_y, self.point)

def remove_scenario_point(self):
    self.point.clear_updaters()
    self.line_x.clear_updaters()
    self.line_y.clear_updaters()
    self.remove(self.point, self.line_x, self.line_y)
    self.to_delete.remove(self.point, self.line_x, self.line_y)
    del self.point
    del self.line_x
    del self.line_y


def draw_gain_zone(self, duration=2):
    # Duraciones relativas
    initial_phase_time = 0.6 * duration
    oscillation_time = 0.4 * duration

    # Acceso dinámico al valor de N
    def get_N():
        return self.n_tracker.get_value()

    def draw_brace():
        # Brace entre (1, 1-N) y (1, 1)
        x = _get_x(self, 0)
        return BraceBetweenPoints(
            [x, _get_y(self, 1 - get_N()), 0],
            [x, _get_y(self, 1), 0],
            direction=LEFT,
            color=WHITE,
            sharpness=0.3,
        )
    # --- Elementos dinámicos ---
    brace = draw_brace()

    # Actualizar brace en tiempo real
    def brace_updater(mob):
        mob.become(draw_brace())
    brace.add_updater(brace_updater)

    # Etiqueta N
    label = Text("N", font_size=80, color=WHITE)
    def label_updater(mob):
        mob.next_to(brace, LEFT, buff=0.15)
    label.add_updater(label_updater)

    # Función para dibujar la zona, con tamaño dinámico
    def draw_zone():
        return _labeled_zone(
            self,
            x_min=0,
            x_max=1,  # Ancho final
            y_min=1 - get_N(),
            y_max=1,
            color=GREEN,
            text="",
        )[0]

    zone_target = draw_zone()
    zone = zone_target.copy().stretch_to_fit_width(0, about_edge=RIGHT)
    self.add(zone)

    # receiver_crit, pos en función de N
    def receiver_crit_updater(mob):
        N = get_N()
        pos = mob.get_center()
        pos[1] = _get_y(self, 1 - N)
        mob.move_to(pos)
    self.receiver_crit.add_updater(receiver_crit_updater)

    # Animación de entrada: Crecer en X (de 0 a 1 en X)
    self.play(
        AnimationGroup(
            FadeIn(self.receiver_crit),
            FadeIn(brace),
            FadeIn(label),
            Transform(zone, zone_target),
            _animate_mercury_y_to(self, 1),
        ),
        run_time=initial_phase_time,
    )

    # Actualización dinámica de la zona con N
    def zone_updater(mob):
        new_zone = draw_zone()
        mob.become(new_zone)

    zone.add_updater(zone_updater)

    # Añadir a la escena y registrar para limpieza
    self.add(brace, label, zone)
    self.to_delete.add(brace, label, zone, self.receiver_crit)

    # Fase 2: Crecimiento en Y, dependiendo de N
    N = get_N()
    self.play(
        _animate_mercury_y_to(self, 1-N),  # Mover barra dependiendo de N
        run_time=oscillation_time/2,
    )
    self.play(
        _animate_mercury_y_to(self, 1-3*N/4),  # Oscilación hacia la mitad
        run_time=oscillation_time/2,
    )


def draw_loss_zone(self, duration=2):
    # Duraciones relativas
    initial_phase_time = 0.6 * duration
    oscillation_time = 0.4 * duration

    # Acceso dinámico al valor de N
    def get_N():
        return self.n_tracker.get_value()

    def draw_brace():
        y = _get_y(self, 1)
        return BraceBetweenPoints(
            [_get_x(self, 0), y, 0],
            [_get_x(self, get_N()), y, 0],
            direction=UP,
            color=WHITE,
            sharpness=0.3,
        )

    brace = draw_brace()
    # Updater del brace
    def brace_updater(mob):
        mob.become(draw_brace())
    brace.add_updater(brace_updater)

    # Etiqueta N
    label = Text("N", font_size=80, color=WHITE)
    def label_updater(mob):
        mob.next_to(brace, UP, buff=0.15)
    label.add_updater(label_updater)

    # Zona roja: parte visible inicial
    def draw_zone():
        return _labeled_zone(
            self,
            x_min=0,
            x_max=get_N(),
            y_min=0,
            y_max=1,
            color=RED,
            text="",
        )[0]

    zone_target = draw_zone()

    # Crear zona para animación de entrada
    zone = draw_zone()
    zone.stretch_to_fit_height(0, about_edge=DOWN)  # Crece desde abajo

    self.add(zone)

    # emitter_crit: posición dinámica en función de N
    def emitter_crit_updater(mob):
        N = get_N()
        pos = mob.get_center()
        pos[0] = _get_x(self, N)
        mob.move_to(pos)
    self.emitter_crit.add_updater(emitter_crit_updater)

    # Animación de entrada
    self.play(
        AnimationGroup(
            FadeIn(self.emitter_crit),
            FadeIn(brace),
            FadeIn(label),
            Transform(zone, zone_target),  # Crecimiento vertical
            _animate_mercury_x_to(self, 0.01),  # Evitar ancho cero total
        ),
        run_time=initial_phase_time,
    )

    def zone_updater(mob):
        mob.become(draw_zone())
    zone.add_updater(zone_updater)

    self.add(brace, label, zone)
    self.to_delete.add(brace, label, zone, self.emitter_crit)

    N = get_N()
    self.play(
        _animate_mercury_x_to(self, N),
        run_time=oscillation_time / 2,
    )
    self.play(
        _animate_mercury_x_to(self, N / 2),
        run_time=oscillation_time / 2,
    )


def rest_uncertainty(self, duration=2):
    self.play(Succession(
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
            AnimationGroup(
                _animate_mercury_x_to(self, 0.6),
                _animate_mercury_y_to(self, 0.2),
            ),
        ),
        run_time=duration,
    )

def add_label(self, text, pos_function):
    def center(N):
        x, y = pos_function(N)
        return [
            _get_x(self, x),
            _get_y(self, y),
            0,
        ]
    def updater(mob):
        N = self.n_tracker.get_value()
        mob.move_to(center(N))

    N = self.n_tracker.get_value()
    label = Text(text)
    label.add_updater(updater)
    updater(label)
    self.to_delete.add(label)
    return label

def draw_results(self):
    self.result_zero = add_label(self, "0", lambda N: ((1+N)/2, (1-N)/2) )
    self.result_plusminus = add_label(self, "+1 -1 = 0", lambda N: (N/2, 1-N/2) )
    self.result_plus = add_label(self, "+1", lambda N: (N/2, (1-N)/2) )
    self.result_minus = add_label(self, "-1", lambda N: ((1+N)/2, 1-N/2) )
    self.play(
        Succession(*[
            FadeIn(self.result_zero),
            FadeIn(self.result_plusminus),
            FadeIn(self.result_plus),
            FadeIn(self.result_minus),
        ])
    )

def animate_n(self):
    self.play(
        self.n_tracker.animate.set_value(0.9)
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
