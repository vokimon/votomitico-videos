from manim import *
from manim_utils import add_background
from itertools import pairwise
from tts import TTS
import math

config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 18
config.frame_height = 32
config.background_color = None
locution="""\
En otro video, explicamos esta forma visual de entender el reparto D'Hondt.
Se ajusta el precio en votos por escaño hasta que se reparten los escaños disponibles.
"""

class VisualDHondtScene(Scene):
    def construct(self):
        # Generate speech audio file with TTS
        with TTS(lang='es') as tts:
            audio_path = tts.speak(locution.replace('\n',' '))

            # Play audio in the scene
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
        self.total_seats = 12

        self.bar_height = 1.0
        self.bar_spacing = 1.6
        self.max_bar_width = 12.0

        self.quotients = list(sorted(
            [
                (votes/seats, party)
                for seats in range(1, self.total_seats+3)
                for party, (_, votes) in enumerate(self.parties)
            ],
            key=lambda x: -x[0]
        ))
        print(self.quotients)
        max_votes = self.quotients[0][0]
        self.initial_price = max_votes * 1.02
        self.final_price = self.quotients[self.total_seats][0]
        self.scale = self.max_bar_width / self.initial_price

    def seats_up_to(self, max_seats: int):
        from collections import Counter
        counts = Counter([party for price, party in self.quotients[:max_seats]])
        cutoff_price = self.quotients[max_seats-1][0] if max_seats else self.quotients[0][0]*1.02
        return [counts.get(party, 0) for party in range(len(self.parties))], cutoff_price

    def setup_layout(self):
        self.bar_group = VGroup()
        self.seat_groups = []
        for i, (color, votes) in enumerate(self.parties):
            bar = Rectangle(
                width=self.bar_scale(votes),
                height=self.bar_height,
                fill_color=color,
                fill_opacity=0.6,
                stroke_width=0,
            )
            bar.align_to(ORIGIN, LEFT)
            bar.shift(DOWN * i * self.bar_spacing)
            self.bar_group.add(bar)

            seats = VGroup()
            self.seat_groups.append(seats)
            self.add(seats)

        self.bar_group.move_to(ORIGIN)
        self.add(self.bar_group)

    def setup_price_line(self):
        plot_height = (self.bar_height + self.bar_spacing) * len(self.parties) - self.bar_spacing

        self.price_line = Line(
            start=[self.bar_scale(self.initial_price), +plot_height / 2, 0],
            end=[self.bar_scale(self.initial_price), -plot_height / 2, 0],
            color=RED,
            stroke_width=4,
        )
        #self.price_line.shift(DOWN * ((len(self.parties) - 1) * self.bar_spacing / 2))
        self.add(self.price_line)

    def setup_counters(self):
        self.available_label = Text("Disponibles: ", font_size=70, color=WHITE).to_corner(UL).shift(RIGHT*1 + DOWN*8.0)
        self.available_count = Integer(self.total_seats, font_size=96, color=WHITE).next_to(self.available_label, RIGHT, buff=1.0)

        self.distributed_label = Text("Repartidos: ", font_size=70, color=WHITE).next_to(self.available_label, DOWN, buff=0.7)
        self.distributed_count = VGroup().next_to(self.distributed_label, RIGHT, buff=1.0)

        self.add(self.available_label, self.available_count, self.distributed_label, self.distributed_count)

    def update_counters(self, value):
        self.distributed_count[:]=[]
        counter = Integer(value, font_size=96, color=WHITE).next_to(self.distributed_label, RIGHT, buff=1.0)
        self.distributed_count.add(counter)

        if value == self.total_seats:
            self.distributed_count.set_color(GREEN)
        elif value > self.total_seats:
            self.distributed_count.set_color(RED)

    def bar_scale(self, votes: float):
        return votes*self.scale


    def get_seat_rectangle(self, party_index, seat_index, price, is_new=False):
        bar = self.bar_group[party_index]
        x = bar.get_corner(LEFT)[0] + seat_index * price * self.scale + (price * self.scale) / 2
        y = bar.get_y()

        return Rectangle(
            width=price * self.scale,
            height=self.bar_height,
            fill_color=WHITE,
            fill_opacity=1.0 if is_new else 0.0,
            stroke_color=WHITE,
            stroke_width=10,
        ).move_to([x, y, 0])

    def animate_prices(self):
        """
        Animate price line and seat allocation step-by-step:
        - Move price and resize seats
        - Flash new seats
        - Update seat counter
        - Transform new seats to transparent
        - Remove seats with color change and fade out
        """
        total_duration = 12.0
        move_fraction = 0.20
        removal_fraction = 0.25

        seat_steps = self._get_seat_steps()
        price_sequence = self._get_price_sequence(seat_steps)
        price_deltas = self._calculate_price_deltas(price_sequence)

        move_durations, flash_duration = self._calculate_durations(
            total_duration, move_fraction, price_deltas
        )
        removal_duration = flash_duration * removal_fraction
        transform_duration = flash_duration - removal_duration

        current_deal, current_price = self.seats_up_to(0)

        for i in range(len(seat_steps) - 1):
            seats_step = seat_steps[i + 1]
            next_deal, next_price = self.seats_up_to(seats_step)

            self._animate_price_and_seats_move(current_deal, next_deal, next_price, move_durations[i])
            self._add_new_seats_flash(current_deal, next_deal, next_price)
            self.update_counters(seats_step)
            self._transform_new_seats_to_normal(current_deal, next_deal, next_price, transform_duration)
            self._animate_seats_removal_with_color_and_fade(current_deal, next_deal, removal_duration)

            current_deal = next_deal
            current_price = next_price


    def _get_seat_steps(self):
        return list(range(self.total_seats + 2)) + [self.total_seats, self.total_seats]


    def _get_price_sequence(self, seat_steps):
        return [self.seats_up_to(step)[1] for step in seat_steps]


    def _calculate_price_deltas(self, price_sequence):
        return [abs(a - b) for a, b in pairwise(price_sequence)]


    def _calculate_durations(self, total_duration, move_fraction, price_deltas):
        total_delta = sum(price_deltas)
        n_steps = len(price_deltas)

        move_time = total_duration * move_fraction
        flash_time = total_duration * (1 - move_fraction)

        move_durations = [(delta / total_delta) * move_time if total_delta else 0 for delta in price_deltas]
        flash_duration = flash_time / n_steps if n_steps > 0 else 0

        return move_durations, flash_duration


    def _animate_price_and_seats_move(self, current_deal, next_deal, next_price, duration):
        animations = []

        animations.append(self.price_line.animate.set_x(
            self.bar_group.get_corner(LEFT)[0] + self.bar_scale(next_price)
        ))

        for party_idx in range(len(self.parties)):
            current_seats = current_deal[party_idx]
            seats = self.seat_groups[party_idx]

            for s_idx, seat in enumerate(seats):
                seat_target = self.get_seat_rectangle(
                    party_index=party_idx,
                    seat_index=s_idx,
                    price=next_price,
                    is_new=False
                )
                animations.append(Transform(seat, seat_target))

        if animations and duration > 0:
            self.play(*animations, run_time=duration, rate_func=linear)


    def _add_new_seats_flash(self, current_deal, next_deal, price):
        for party_idx in range(len(self.parties)):
            current_seats = current_deal[party_idx]
            next_seats = next_deal[party_idx]
            seats = self.seat_groups[party_idx]

            for seat_index in range(current_seats, next_seats):
                seat = self.get_seat_rectangle(
                    party_index=party_idx,
                    seat_index=seat_index,
                    price=price,
                    is_new=True
                )
                seats.add(seat)


    def _transform_new_seats_to_normal(self, current_deal, next_deal, price, duration):
        animations = []
        for party_idx in range(len(self.parties)):
            current_seats = current_deal[party_idx]
            next_seats = next_deal[party_idx]
            seats = self.seat_groups[party_idx]

            for s_idx in range(current_seats, next_seats):
                seat = seats[s_idx]
                seat_target = self.get_seat_rectangle(
                    party_index=party_idx,
                    seat_index=s_idx,
                    price=price,
                    is_new=False,
                )
                animations.append(Transform(seat, seat_target))

        if animations and duration > 0:
            self.play(*animations, run_time=duration, rate_func=smooth)


    def _animate_seats_removal_with_color_and_fade(self, current_deal, next_deal, duration):
        highlight_anims = []
        fadeout_anims = []

        for party_idx in range(len(self.parties)):
            current_seats = current_deal[party_idx]
            next_seats = next_deal[party_idx]
            seats = self.seat_groups[party_idx]

            for seat_index in range(next_seats, current_seats):
                seat = seats[seat_index]
                highlight_anims.append(seat.animate.set_fill(RED))
                fadeout_anims.append(Transform(seat, seat.copy().scale(0.1)))
                fadeout_anims.append(FadeOut(seat))

        if highlight_anims and duration > 0:
            self.play(*highlight_anims, run_time=duration * 0.3, rate_func=smooth)

        if fadeout_anims and duration > 0:
            self.play(*fadeout_anims, run_time=duration * 0.7, rate_func=smooth)

        for party_idx in range(len(self.parties)):
            current_seats = current_deal[party_idx]
            next_seats = next_deal[party_idx]
            seats = self.seat_groups[party_idx]
            for seat_index in reversed(range(next_seats, current_seats)):
                seats.remove(seats[seat_index])
