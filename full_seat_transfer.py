from manim import *


def transfer_seat(self, emitter_idx, receiver_idx, duration):
    shift_receiver_right(self, receiver_idx, duration * 0.3)
    shrink_emitter_bar_left(self, emitter_idx)
    animate_seat_fly(self, emitter_idx, receiver_idx, duration * 0.4)
    shift_emitter_left(self, emitter_idx, duration * 0.3)
    grow_receiver_right(self, receiver_idx)

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


