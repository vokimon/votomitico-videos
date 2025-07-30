from manim import *
from manim_utils import add_background
from itertools import pairwise
from tts import TTS
import math
from scale import LinearScale

config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 18
config.frame_height = 32
config.background_color = None

locution = """\
En otro video, explicamos esta forma visual de entender el reparto D'Hondt.
Se reduce el precio en votos por escaño hasta que se reparten todos los escaños disponibles.
"""

class VisualDHondtScene(Scene):
    def construct(self):
        with TTS(lang='es') as tts:
            audio_path = tts.speak(locution.replace('\n',' '))
            self.add_sound(audio_path)
            add_background(self)
            self.setup_data()
            self.setup_layout()
            self.setup_price_line()
            self.setup_counters()
            self.animate_prices()
            self.wait(1)

    def setup_data(self):
        self.parties = [
            (RED, 13712),
            (BLUE, 9843),
            (GREEN, 7254),
            (ORANGE, 6100),
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
        self.final_price = self.quotients[self.total_seats][0]
        max_votes_domain = self.quotients[1][0] + self.quotients[2][0] # second and third added

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
        #self.add(SurroundingRectangle(self.bar_group, color=YELLOW))

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
            self.price_lines.append((i, line))
            self.add(line)

        # Guarda la línea principal para animaciones posteriores
        self.price_line = self.price_lines[0][1]


    def setup_price_line(self):
        return self.setup_price_lines()
        overshoot = 2 * self.bar_height
        bar_top = self.bar_group.get_top()[1] + overshoot
        bar_bottom = self.bar_group.get_bottom()[1] - overshoot
        x_pos = self.votes2x(self.initial_price)

        self.price_line = Line(
            start=[x_pos, bar_top, 0],
            end=[x_pos, bar_bottom, 0],
            color=RED,
            stroke_width=4,
        )
        self.add(self.price_line)

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
        x = self.votes2x(seat_index * price + price / 2)  # posición (con offset)
        y = self.bar_group[party_index].get_y()

        width = self.votes2x.scale(price)  # ancho sin offset

        return Rectangle(
            width=width,
            height=self.bar_height,
            fill_color=WHITE,
            fill_opacity=1.0 if is_new else 0.0,
            stroke_color=WHITE,
            stroke_width=10,
        ).move_to([x, y, 0])

    def seats_up_to(self, max_seats: int):
        from collections import Counter
        counts = Counter([party for price, party in self.quotients[:max_seats]])
        cutoff_price = self.quotients[max_seats - 1][0] if max_seats else self.quotients[0][0] * 1.02
        return [counts.get(party, 0) for party in range(len(self.parties))], cutoff_price

    def animate_prices(self):
        total_duration = 10.0
        move_fraction = 0.20

        seat_steps = list(range(self.total_seats + 1))
        price_sequence = [self.seats_up_to(step)[1] for step in seat_steps]
        price_deltas = [abs(a - b) for a, b in pairwise(price_sequence)]

        total_delta = sum(price_deltas)
        move_time = total_duration * move_fraction
        flash_time = total_duration * (1 - move_fraction)

        move_durations = [(delta / total_delta) * move_time if total_delta else 0 for delta in price_deltas]
        flash_duration = flash_time / len(price_deltas)

        current_deal, current_price = self.seats_up_to(0)

        for step_idx in range(len(seat_steps) - 1):
            next_step = seat_steps[step_idx + 1]
            next_deal, next_price = self.seats_up_to(next_step)

            self._animate_price_and_seats_move(
                current_deal=current_deal,
                next_deal=next_deal,
                next_price=next_price,
                duration=move_durations[step_idx],
            )
            self._add_new_seats_flash(
                current_deal=current_deal,
                next_deal=next_deal,
                price=next_price,
            )
            self.update_counters(value=next_step)
            self._transform_new_seats_to_normal(
                current_deal=current_deal,
                next_deal=next_deal,
                price=next_price,
                duration=flash_duration,
            )

            current_deal = next_deal
            current_price = next_price

    def _animate_price_and_seats_move(self, current_deal, next_deal, next_price, duration):
        animations = []

        for multiplier, line in self.price_lines:
            target_x = self.votes2x(next_price * multiplier)
            animations.append(line.animate.set_x(target_x))

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
