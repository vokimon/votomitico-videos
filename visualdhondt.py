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

class DebugScene(VoiceoverScene):

    def construct(self):
        add_background(self)
        self.to_delete = VGroup()

        visual_dhondt(self)

        highlight_rests_and_fraction(self)

def visual_dhondt(self, total_duration=7.0):
    self.play(FadeOut(self.to_delete, duration=0.001))
    setup_data(self)
    setup_layout(self)
    setup_price_lines(self)
    setup_counters(self)
    animate_prices(self, total_duration)

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
    self.initial_price_factor = 1.2

    self.quotients = sorted(
        [(votes / seats, party)
         for seats in range(1, self.total_seats + 3)
         for party, (_, votes) in enumerate(self.parties)],
        key=lambda x: -x[0]
    )

    max_votes = self.quotients[0][0]
    self.initial_price = max_votes * self.initial_price_factor
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
    self.seats_label = Text("Escaños repartidos: ", font_size=70, color=WHITE).to_corner(UL).shift(RIGHT + DOWN * 8)
    self.distributed_count = VGroup().next_to(self.seats_label, RIGHT, buff=1.0)
    self.add(self.seats_label, self.distributed_count)

def _update_counters(self, value):
    self.distributed_count[:] = []
    counter = Text(f"{value} / {self.total_seats}",
        font_size=96, color=WHITE
    ).next_to(self.seats_label, RIGHT, buff=1.0)
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
    cutoff_price = self.quotients[max_seats - 1][0] if max_seats else self.quotients[0][0] * 1.05
    return [counts.get(party, 0) for party in range(len(self.parties))], cutoff_price

def animate_prices(self, total_duration = 7.0):
    move_fraction = 0.30
    seat_steps = list(range(self.total_seats + 1))

    price_sequence = [self.initial_price] + [
        seats_up_to(self, step)[1]
        for step in seat_steps
    ]
    price_deltas = [
        abs(a - b) for a, b in pairwise(price_sequence)]

    total_delta = sum(price_deltas)
    move_time = total_duration * move_fraction
    flash_time = total_duration * (1 - move_fraction)

    move_durations = [
        (delta / total_delta) * move_time if total_delta else 0
        for delta in price_deltas
    ]
    flash_duration = flash_time / len(price_deltas)

    current_deal, current_price = seats_up_to(self, 0)

    _update_counters(self, value=0)

    for step_idx, next_step in enumerate(seat_steps):
        next_deal, next_price = seats_up_to(self, next_step)
        price_move_duration = move_durations[step_idx]

        print(step_idx, next_step, next_price, price_move_duration, next_deal)

        _animate_price_and_seats_move(self, current_deal, next_deal, next_price, price_move_duration)
        _add_new_seats_flash(self, current_deal, next_deal, next_price)

        _update_counters(self, value=next_step)
        _transform_new_seats_to_normal(self, current_deal, next_deal, next_price, flash_duration)

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
            seat_target = get_seat_rectangle(
                self,
                party_index=party_idx,
                seat_index=seat_idx,
                price=next_price,
                is_new=False,
            )
            animations.append(Transform(seat, seat_target))

    if animations:
        self.play(*animations, run_time=max(duration,.001), rate_func=linear)

def _add_new_seats_flash(self, current_deal, next_deal, price):
    for party_idx in range(len(self.parties)):
        current_seats = current_deal[party_idx]
        next_seats = next_deal[party_idx]
        seats = self.seat_groups[party_idx]

        for seat_idx in range(current_seats, next_seats):
            seat = get_seat_rectangle(
                self,
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
            seat_target = get_seat_rectangle(
                self,
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

    self.play(Indicate(self.price_lines[0][1]))

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



