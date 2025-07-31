from manim import *
from manim_utils import add_background
from itertools import pairwise
import math
from scale import LinearScale
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
import numpy as np

config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 18
config.frame_height = 32
config.background_color = None

class VisualDHondtScene(VoiceoverScene):
    def voiceover(self, **kwds):
        return super().voiceover(**dict(kwds, max_subcaption_len=30))

    def construct(self):
        self.set_speech_service(GTTSService(lang="es", global_speed=1.4))

        with self.voiceover(text=
            "Esta es una forma muy visual de entender el reparto D'Hondt.\n"
            "Se reducen los votos que cuesta un escaño hasta que quedan repartidos todos los escaños disponibles."
        ):
            add_background(self)
            self.setup_data()
            self.setup_layout()
            self.setup_price_lines()
            self.setup_counters()
            self.animate_prices()

        with self.voiceover(text=
            "Fijado este precio P, los votos suman escaño o bien quedan como restos."
        ):
            self.wait(1)
            self.highlight_rests_and_fraction()

        with self.voiceover(text=
            "Si transferimos bloques de P votos entre candidaturas afines, "
            "el receptor gana escaños, pero entre los dos tienen los mismos. "
            "Concentramos cientos de miles de votos sin beneficio conjunto. "
        ):
            self.wait()
            for _ in range(2):
                self.animate_vote_transfer(2, 1, duration=0.8)
            for _ in range(5):
                self.animate_vote_transfer(1, 2, duration=0.8)
            for _ in range(3):
                self.animate_vote_transfer(2, 1, duration=0.5)

        with self.voiceover(text=
            "En trasvases menores que P depende de los restos de ambas formaciones... "
        ):
            self.zoom_on_rests(emitter_idx=2, receiver_idx=1)

        with self.voiceover(text=
            "...cuyo valor entre 0 y P desconocemos antes de la votación. "
            "Si trasvasamos N el emisor ganará un escaño cuando le queden menos para llegar a P. "
            "Pero el emisor lo perdera si no tiene tantos restos. "
            "Las áreas de pérdida y de ganancia neta son iguales aunque cambie N. "
            "Hay oportunidad de hacer voto estratégico cuando podemos predecir los restos. "
            "Pero no, el criterio no es votar al más grande. "
            "Aún piensas que..."
        ):
            pass


    def setup_data(self):
        self.parties = [
            (RED, 13712),
            (BLUE, 9843),
            (ORANGE, 7254),
            (GREEN, 6100),
        ]
        self.total_seats = 11
        self.bar_height = 1.0
        self.bar_spacing = 1.6
        self.max_bar_width = 12.0
        self.xmargin_pct = 0.10  # SSMM safe area

        self.quotients = sorted(
            [(votes / seats, party)
             for seats in range(1, self.total_seats + 3)
             for party, (_, votes) in enumerate(self.parties)],
            key=lambda x: -x[0]
        )

        max_votes = self.quotients[0][0]
        self.initial_price = max_votes * 1.02
        self.final_price = self.quotients[self.total_seats-1][0]
        max_votes_domain = self.quotients[1][0] + self.quotients[2][0]

        useful_width = config.frame_width - 2*self.xmargin_pct*config.frame_width
        self.votes2x = LinearScale(
            0, max_votes_domain,
            -useful_width/2, +useful_width/2,
        )

    def setup_layout(self):
        self.bar_group = VGroup()
        self.seat_groups = []

        for i, (color, votes) in enumerate(self.parties):
            x0 = self.votes2x(0)
            x1 = self.votes2x(votes)
            width = x1 - x0

            bar = Rectangle(
                width=width,
                height=self.bar_height,
                fill_color=color,
                fill_opacity=0.6,
                stroke_width=0,
            ).move_to([(x0 + x1) / 2, -i * self.bar_spacing, 0])

            self.bar_group.add(bar)
            seats = VGroup()
            self.seat_groups.append(seats)

        self.add(self.bar_group)

    def setup_price_lines(self):
        plot_height = (self.bar_height + self.bar_spacing) * len(self.parties) - self.bar_spacing
        y0 = self.bar_group.get_top()[1] + 2 * self.bar_height
        y1 = self.bar_group.get_bottom()[1] - 2 * self.bar_height

        self.price_lines = []

        for i in range(1, self.total_seats + 1):
            x = self.votes2x(self.initial_price * i)

            line = Line(
                start=[x, y0, 0],
                end=[x, y1, 0],
                color=RED if i == 1 else WHITE,
                stroke_width=4 if i == 1 else 2,
                stroke_opacity=1.0 if i == 1 else 0.25,
            )

            label_text = f"{i}P" if i > 1 else "P"
            label = Text(label_text, font_size=36, color=WHITE)
            label.next_to(line, UP, buff=0.2)

            line_and_label = VGroup(line, label)
            self.price_lines.append((i, line_and_label))
            self.add(line_and_label)

        self.price_line = self.price_lines[0][1][0]  # only the Line, for legacy code

    def setup_counters(self):
        self.available_label = Text("Disponibles: ", font_size=70, color=WHITE).to_corner(UL).shift(RIGHT + DOWN * 8)
        self.available_count = Integer(self.total_seats, font_size=96, color=WHITE).next_to(self.available_label, RIGHT, buff=1.0)

        self.distributed_label = Text("Repartidos: ", font_size=70, color=WHITE).next_to(self.available_label, DOWN, buff=0.7)
        self.distributed_count = VGroup().next_to(self.distributed_label, RIGHT, buff=1.0)

        self.add(self.available_label, self.available_count, self.distributed_label, self.distributed_count)

    def update_counters(self, value):
        self.distributed_count[:] = []
        counter = Integer(value, font_size=96, color=WHITE).next_to(self.distributed_label, RIGHT, buff=1.0)
        self.distributed_count.add(counter)

        if value == self.total_seats:
            self.distributed_count.set_color(GREEN)

    def get_seat_rectangle(self, party_index, seat_index, price, is_new=False):
        x = self.votes2x(seat_index * price + price / 2)
        y = self.bar_group[party_index].get_y()

        new_color = WHITE
        party_color = self.parties[party_index][0]
        width = self.votes2x.scale(price)

        return Rectangle(
            width=width,
            fill_color=new_color if is_new else party_color,
            height=self.bar_height,
            fill_opacity=1.0,
            stroke_color=WHITE,
            stroke_width=10,
        ).move_to([x, y, 0])

    def seats_up_to(self, max_seats: int):
        from collections import Counter
        counts = Counter([party for price, party in self.quotients[:max_seats]])
        cutoff_price = self.quotients[max_seats - 1][0] if max_seats else self.quotients[0][0] * 1.02
        return [counts.get(party, 0) for party in range(len(self.parties))], cutoff_price

    def animate_prices(self):
        total_duration = 8.0
        move_fraction = 0.30
        seat_steps = list(range(self.total_seats + 1))

        price_sequence = [self.seats_up_to(step)[1] for step in seat_steps]
        price_deltas = [abs(a - b) for a, b in pairwise(price_sequence)]

        total_delta = sum(price_deltas)
        move_time = total_duration * move_fraction
        flash_time = total_duration * (1 - move_fraction)

        move_durations = [
            (delta / total_delta) * move_time if total_delta else 0
            for delta in price_deltas
        ]
        flash_duration = flash_time / len(price_deltas)

        current_deal, current_price = self.seats_up_to(0)

        for step_idx in range(len(seat_steps) - 1):
            next_step = seat_steps[step_idx + 1]
            next_deal, next_price = self.seats_up_to(next_step)

            self._animate_price_and_seats_move(current_deal, next_deal, next_price, move_durations[step_idx])
            self._add_new_seats_flash(current_deal, next_deal, next_price)

            self.update_counters(value=next_step)
            self._transform_new_seats_to_normal(current_deal, next_deal, next_price, flash_duration)

            current_deal = next_deal
            current_price = next_price

    def _animate_price_and_seats_move(self, current_deal, next_deal, next_price, duration):
        animations = []

        for multiplier, group in self.price_lines:
            target_x = self.votes2x(next_price * multiplier)
            animations.append(group.animate.set_x(target_x))

        for party_idx in range(len(self.parties)):
            seats = self.seat_groups[party_idx]
            for seat_idx, seat in enumerate(seats):
                seat_target = self.get_seat_rectangle(
                    party_index=party_idx,
                    seat_index=seat_idx,
                    price=next_price,
                    is_new=False,
                )
                animations.append(Transform(seat, seat_target))

        if animations and duration > 0:
            self.play(*animations, run_time=duration, rate_func=linear)

    def _add_new_seats_flash(self, current_deal, next_deal, price):
        for party_idx in range(len(self.parties)):
            current_seats = current_deal[party_idx]
            next_seats = next_deal[party_idx]
            seats = self.seat_groups[party_idx]

            for seat_idx in range(current_seats, next_seats):
                seat = self.get_seat_rectangle(
                    party_index=party_idx,
                    seat_index=seat_idx,
                    price=price,
                    is_new=True,
                )
                seats.add(seat)

    def _transform_new_seats_to_normal(self, current_deal, next_deal, price, duration):
        animations = []

        for party_idx in range(len(self.parties)):
            current_seats = current_deal[party_idx]
            next_seats = next_deal[party_idx]
            seats = self.seat_groups[party_idx]

            for seat_idx in range(current_seats, next_seats):
                seat = seats[seat_idx]
                seat_target = self.get_seat_rectangle(
                    party_index=party_idx,
                    seat_index=seat_idx,
                    price=price,
                    is_new=False,
                )
                animations.append(Transform(seat, seat_target))

        if animations and duration > 0:
            self.play(*animations, run_time=duration, rate_func=smooth)

    def highlight_rests_and_fraction(self):
        party_index = 0
        votes = self.parties[party_index][1]
        color = self.parties[party_index][0]
        seats = self.seat_groups[party_index]
        seats_won = len(seats)
        price = self.final_price
        votes_used = seats_won * price
        rests = votes - votes_used

        bounce_anims = [Indicate(seat) for seat in seats]

        self.play(
            LaggedStart(*bounce_anims, lag_ratio=0.5, run_time=seats_won * 0.3)
        )

        self.wait(0.5)
        for party_index, (color, votes) in enumerate(self.parties):

            rests = votes % self.final_price

            bar = self.bar_group[party_index]
            x_start = self.votes2x(votes_used)
            x_end = self.votes2x(votes)

            rest_width = self.votes2x.scale(rests)
            rest_rect = Rectangle(
                width=rest_width,
                height=self.bar_height,
                fill_color=color,
                fill_opacity=0.7,
                stroke_color=None,
                stroke_width=0,
            ).move_to(bar, RIGHT).set_y(bar.get_y())

            self.add(rest_rect)

            self.play(
                Indicate(rest_rect, run_time=0.4)
            )
            self.remove(rest_rect)

        self.wait(1.0)

    def animate_vote_transfer(self, emitter_idx, receiver_idx, duration):
        self.shift_receiver_right(receiver_idx, duration * 0.3)
        self.shrink_emitter_bar_left(emitter_idx)
        self.animate_seat_fly(emitter_idx, receiver_idx, duration * 0.4)
        self.shift_emitter_left(emitter_idx, duration * 0.3)
        self.grow_receiver_right(receiver_idx)

    def shift_receiver_right(self, iparty, duration):
        seat_width = self.votes2x.scale(self.final_price)
        receiver_bar = self.bar_group[iparty]
        receiver_seats = self.seat_groups[iparty]

        self.play(
            receiver_bar.animate.shift(RIGHT * seat_width),
            *[seat.animate.shift(RIGHT * seat_width) for seat in receiver_seats],
            run_time=duration,
            rate_func=smooth,
        )

    def shift_emitter_left(self, iparty, duration):
        seat_width = self.votes2x.scale(self.final_price)
        emitter_bar = self.bar_group[iparty]
        emitter_seats = self.seat_groups[iparty]

        self.play(
            emitter_bar.animate.shift(LEFT * seat_width),
            *[seat.animate.shift(LEFT * seat_width) for seat in emitter_seats],
            run_time=duration,
            rate_func=smooth,
        )

    def shrink_emitter_bar_left(self, emitter_idx):
        seat_width = self.votes2x.scale(self.final_price)
        bar = self.bar_group[emitter_idx]
        new_width = bar.width - seat_width
        bar.stretch_to_fit_width(new_width)
        bar.shift(RIGHT * (seat_width / 2))

    def grow_receiver_right(self, party_idx):
        seat_width = self.votes2x.scale(self.final_price)
        bar = self.bar_group[party_idx]
        new_width = bar.width + seat_width
        bar.stretch_to_fit_width(new_width)
        bar.shift(LEFT * seat_width / 2)

    def animate_seat_fly(self, emitter_idx, receiver_idx, duration):
        seat_to_fly = self.seat_groups[emitter_idx][0]
        current_pos = seat_to_fly.get_center()
        target_y = self.bar_group[receiver_idx].get_y()
        target_pos = np.array([current_pos[0], target_y, 0])

        path = ArcBetweenPoints(current_pos, target_pos, angle=PI / 2)

        self.play(
            MoveAlongPath(seat_to_fly, path),
            run_time=duration,
            rate_func=smooth,
        )

        receiver_color = self.parties[receiver_idx][0]
        seat_to_fly.set_fill(receiver_color, opacity=1.0)

        self.seat_groups[receiver_idx].submobjects.insert(0, seat_to_fly)
        self.seat_groups[emitter_idx].remove(seat_to_fly)


        receiver_target_pos = RIGHT * (config.frame_width / 2 - 2.5)  # zona derecha segura

    def zoom_on_rests(self, emitter_idx=2, receiver_idx=1):
        # Crear overlays de restos

        def create_rest_overlay(party_index):
            votes = self.parties[party_index][1]
            color = self.parties[party_index][0]
            seats_won = len(self.seat_groups[party_index])
            votes_used = seats_won * self.final_price
            rest_votes = votes - votes_used

            if rest_votes <= 0:
                return None

            bar = self.bar_group[party_index]
            bar_y = bar.get_center()[1]

            rest_width = self.votes2x.scale(rest_votes)
            height = self.bar_height

            # RECTÁNGULO DEL RESTO
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

            # LÍNEA DE PRECIO SUPERADO (último escaño ganado)
            guide_line = Line(
                start=rect.get_left() + UP * (height / 2 + 0.15),
                end=rect.get_left() + DOWN * (height / 2 + 0.15),
                stroke_color=WHITE,
                stroke_width=4,
            )

            # LÍNEA DE PRECIO NO SUPERADO (siguiente escaño posible)
            next_price_votes = self.final_price * (seats_won + 1)
            next_price_x = self.votes2x(next_price_votes)
            next_price_line = Line(
                start=[next_price_x, bar_y + height / 2 + 0.15, 0],
                end=[next_price_x, bar_y - height / 2 - 0.15, 0],
                stroke_color=WHITE,
                stroke_width=4,
                stroke_opacity=0.25,
            )

            # GRUPO DE OVERLAY
            overlay = VGroup(rect, guide_line, next_price_line)

            # 🔧 AJUSTE de posición para que el borde izquierdo esté en el punto correcto
            left_edge = rect.get_left()
            for mobj in overlay:
                mobj.shift(-left_edge)

            # Ahora colocamos el grupo entero con su borde izquierdo en la posición correcta
            overlay.move_to([left_edge[0], bar_y, 0], aligned_edge=LEFT)

            return overlay


        emitter_overlay = create_rest_overlay(emitter_idx)
        receiver_overlay = create_rest_overlay(receiver_idx)

        if emitter_overlay is None or receiver_overlay is None:
            return  # No hay restos para hacer zoom

        # Añadir overlays
        self.add(emitter_overlay, receiver_overlay)

        # Fade parcial de los demás elementos menos el fondo
        fade_group = VGroup(
            *self.bar_group,
            *[seat for group in self.seat_groups for seat in group],
            *[line_and_label for _, line_and_label in self.price_lines],
            self.available_label,
            self.available_count,
            self.distributed_label,
            self.distributed_count,
        )

        self.play(
            fade_group.animate.set_opacity(0.2),
            run_time=1.5
        )
        self.wait(0.5)

        # Posiciones destino en la zona segura
        emitter_target_pos = DOWN * (config.frame_height / 2 - 2.0)
        receiver_target_pos = RIGHT * (config.frame_width / 2 - 2.0)

        # Animar zoom, traslado y rotación
        self.play(
            emitter_overlay.animate.scale(3.5).move_to(emitter_target_pos),
            receiver_overlay.animate.scale(3.5).rotate(PI / 2).move_to(receiver_target_pos),
            run_time=2.5
        )
        self.wait(0.5)

    from dhont_to_rest_graph import zoom_on_rests



