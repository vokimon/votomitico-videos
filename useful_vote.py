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

class UsefulVoteScene(VoiceoverScene):
    from scene_00_is_vote_concentration_useful import is_vote_concentration_useful
    from balance import balance_sequence
    from full_seat_transfer import transfer_seat
    from under_p_transfers import under_p_transfers, prepare_rest_plot_axes, draw_gain_zone, draw_loss_zone, rest_uncertainty
    from conclusions import conclusions
    from visualdhondt import visual_dhondt, highlight_rests_and_fraction

    def voiceover(self, **kwds):
        return super().voiceover(**dict(kwds, max_subcaption_len=20))

    def construct(self):
        add_background(self)
        self.set_speech_service(GTTSService(lang="es", global_speed=1.4))
        self.to_delete = VGroup()

        with self.voiceover(text=
            "¿Es útil concentrar el voto en el partido más grande?"
        ):
            self.is_vote_concentration_useful()

        with self.voiceover(text=
            "El voto útil plantea votar un partido que te gusta menos, "
            "a cambio de la ventaja que da el sistema al votar al mayor. "
            "¿Pero sabías que tal ventaja no existe?"
        ):
            self.play(FadeOut(self.to_delete))
            self.balance_sequence()

        with self.voiceover(text=
            "Visualmente, el reparto D'Hondt consiste en "
            "rebajar los votos que cuesta cada escaño hasta que se reparten todos. "
        ):
            self.visual_dhondt(total_duration=5.0)

        with self.voiceover(text=
            "Fijado este precio P, los votos suman escaño o bien quedan como restos. "
        ):
            self.highlight_rests_and_fraction()

        with self.voiceover(text=
            "Si transferimos bloques de P votos entre candidaturas afines "
            "lo que gana una lo pierde la otra. "
            "Concentraríamos miles de votos sin beneficio conjunto. "
        ):
            for _ in range(2):
                self.transfer_seat(2, 1, duration=0.8)
            for _ in range(5):
                self.transfer_seat(1, 2, duration=0.8)
            for _ in range(3):
                self.transfer_seat(2, 1, duration=0.5)

        with self.voiceover(text=
            "En trasvases menores que P depende de los restos de ambas formaciones... "
        ):
            self.prepare_rest_plot_axes(emitter_idx=2, receiver_idx=1)

        with self.voiceover(text=
            "En un trasvase es de N votos el receptor llegará al escaño si sus restos andan cerca de P. "
        ):
            self.draw_gain_zone()
            
        with self.voiceover(text=
            "Pero el emisor lo perderá si no tiene tantos restos para dar. "
        ):
            self.draw_loss_zone()

        with self.voiceover(text=
            "Si no podemos predecir los restos, cada resultado es tan probable como el área que ocupa. "
        ):
            self.rest_uncertainty()

        with self.voiceover(text=
            "Y las zonas de pérdida y ganancia netas son iguales aunque cambie N. "
        ):
            self.rest_uncertainty()

        with self.voiceover(text=
            "Habrá oportunidad de voto estratégico cuando podamos predecir los restos. "
            "Pero no, el criterio tampoco será votar al más grande. "
            "¿Aún piensas que..."
        ):
            self.play(FadeOut(self.to_delete, duration=0.001))
            self.conclusions()




