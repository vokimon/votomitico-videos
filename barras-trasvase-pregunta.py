from manim import *
import numpy as np
import random
import tempfile
import os
from gtts import gTTS

"""
[
aparece un interrogante con dos barras desiguales,
desaparece el interrogante y una parte de la barra menor se va a la barra mayor.
]
¿Es útil concentrar el voto en el partido más grande?
[aparece un cruz palpitante encima de todo]
Pues NO es así.
El llamado voto útil, que tenemos interiorizado, es una patraña.
No solo es que dejas de votar a quien representa mejor, si es que lo hace.
Es que se puede demostrar visualmente que no, puede ser hasta peor.
[un monigote con los ojos mirando para arriba???]
Que sí, que el sistema electoral beneficia a los grandes
pero verás que eso no afecta al poder de cambio de tu voto.
[
Animación con varios bloques de votos.
Un marcador en la parte superior indica,
Disponibles y Repartidos, referiendo se a los escaños.
La linea baja hasta que reparte hasta que reparte uno de más y echa para atras.
A medida que baja se marcan los escaños conseguidos en las barras y en el marcador.
]
En otros vídeos explicamos de forma muy sencilla el reparto de D'Hondt,
que se usa para repartir escaños en España.
Resumido: ajusta un precio en votos por escaño para repartir escaños sin que sobren ni falten.
[Desaparecen todas las barras menos una.
Resaltar uno tras otro los bloques de votos de cada escaño.
Una breve pausa justa para romper el ritmo.
Resaltar el bloque de los restos.]
Establecido el precio, los votos van, bien a obtener escaños o a los restos.
[
Animación de sucesivos trasvases entre dos candidaturas,
pasandose bloques de un escaño mientras las otras y los restos de todas, quedan igual
]
Si muevo votos en bloques de un escaño,
no hay ganancia conjunta de ambas candidaturas,
solo muevo un escaño entre las dos, y el resto queda igual.
Vale, puedo estar moviendo cientos de miles de votos.
El grande se beneficia. El bloque de ambos partidos, no.
[
Entra otro interrogante.
]
Pero, y entre medias, puede haber ganancia?
[
Sale el interrogante. Y hacemos zoom en la parte de restos de una candidatura.
Los restos oscilan entre 0 y P.
]
Pues eso depende de cuales eran los restos en la situacion inicial.
[

]



los votos de una candidatura, o se usan para "comprar" un escaño o quedan para restos.
Los restos de una candidatura quedarán en un punto indeterminado entre cero y el precio.
Si movemos tantos votos como el precio vamos a otra situación en la que
Pongamos que N personas que iban a votar a un partido deciden votar a otro mas grande para concentrar.
Si N es un múltiplo del precio,
que son escaños enteros que se van de una candidatura a la otra
sin cambiar para nada el resultado de las otras candidaturas,
ni el resultado conjunto de la grande y la pequeña.
Y que pasa si no es múltiplo?
Pues que lo que sobra

pero que conjuntamente no cambian el resultado.
Y despues esta la parte mas pequeña que el precio.



"""


config.frame_rate = 30
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.background_color = WHITE  # Will be overridden with gradient

def overshoot(t, s=1.70158):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1

class GoogleTTS:
    def __init__(self, lang='es', slow=False):
        self.lang = lang
        self.slow = slow
        self._temp_dir = None

    def __enter__(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._temp_dir.cleanup()

    def speak(self, text):
        if self._temp_dir is None:
            raise RuntimeError("Use this class as a context manager with 'with'.")
        fd, path = tempfile.mkstemp(suffix=".mp3", dir=self._temp_dir.name)
        os.close(fd)
        tts = gTTS(text=text, lang=self.lang, slow=self.slow)
        tts.save(path)
        return path

class VoteTransferWithQuestionMark(Scene):
    def construct(self):
        question_text = "¿Es útil concentrar el voto\nen el partido más grande?"

        # Generate speech audio file with TTS
        with GoogleTTS(lang='es') as tts:
            audio_path = tts.speak(question_text.replace('\n',' '))

            # Play audio in the scene
            self.add_sound(audio_path)

            self.init_params()
            self.add_gradient_background()
            self.show_caption(question_text)
            self.create_bars()
            self.animate_source_squash_stretch()
            self.animate_splinters()
            self.update_target_bar()
            self.animate_target_compression()
            self.animate_question_mark()
            self.wait(2)

    def init_params(self):
        self.source_color = RED
        self.target_color = BLUE
        self.bar_width = 2
        self.source_total_height = 4.0
        self.extracted_height = 1.0
        self.num_splinters = 5
        self.splinter_height = self.extracted_height / self.num_splinters
        self.source_remaining_height = self.source_total_height - self.extracted_height
        self.target_initial_height = 6.0
        self.target_final_height = self.target_initial_height + self.extracted_height
        self.base_y = -3
        self.source_pos = LEFT * 3
        self.target_pos = RIGHT * 3
        self.parabola_time = 0.7

        dx = abs(self.target_pos[0] - self.source_pos[0])
        impulse_fraction = 0.2
        self.release_time = self.parabola_time * (self.bar_width * impulse_fraction) / dx
        self.retract_time = 0.2

    def add_gradient_background(self):
        gradient = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_opacity=1,
            stroke_width=0
        )
        gradient.set_fill(color=["#f85158", BLACK], opacity=1)
        gradient.move_to(ORIGIN)
        self.add(gradient)

    def create_bars(self):
        self.source_bar = Rectangle(
            width=self.bar_width, height=self.source_total_height,
            color=self.source_color, fill_opacity=1
        ).move_to(self.source_pos).align_to([0, self.base_y, 0], DOWN)

        self.target_bar = Rectangle(
            width=self.bar_width, height=self.target_initial_height,
            color=self.target_color, fill_opacity=1
        ).move_to(self.target_pos).align_to([0, self.base_y, 0], DOWN)

        self.add(self.source_bar, self.target_bar)
        self.wait(0.5)

    def animate_source_squash_stretch(self):
        bottom = self.source_bar.get_bottom()
        scale_y = 0.85
        scale_x = 1 / scale_y

        self.play(
            self.source_bar.animate.stretch(scale_x, 0).stretch(scale_y, 1).move_to(bottom, aligned_edge=DOWN),
            run_time=self.retract_time
        )
        self.play(
            self.source_bar.animate.stretch(1 / scale_x, 0).stretch(1 / scale_y, 1).move_to(bottom, aligned_edge=DOWN),
            run_time=self.release_time
        )

        self.source_bar_cut = Rectangle(
            width=self.bar_width,
            height=self.source_remaining_height,
            color=self.source_color,
            fill_opacity=1
        ).move_to(self.source_pos).align_to([0, self.base_y, 0], DOWN)

        self.remove(self.source_bar)
        self.add(self.source_bar_cut)

    def animate_splinters(self):
        self.moving_splinters = []
        animations = []

        for i in range(self.num_splinters):
            offset_x = random.uniform(-0.15, 0.15)
            y_offset = self.source_remaining_height + self.splinter_height / 2 + i * self.splinter_height
            start = self.source_bar_cut.get_bottom() + UP * y_offset
            y_final = self.target_bar.get_height() + self.splinter_height / 2 + i * self.splinter_height
            end = self.target_bar.get_bottom() + UP * y_final
            parabola_height = 3.5 + i * 0.3
            mid = (start + end) / 2 + UP * parabola_height + RIGHT * offset_x
            path = VMobject().set_points_smoothly([start, mid, end])

            splinter = Rectangle(
                width=self.bar_width, height=self.splinter_height,
                color=self.source_color, fill_opacity=1
            ).move_to(start)

            self.moving_splinters.append(splinter)
            self.add(splinter)

            anim = MoveAlongPath(splinter, path, run_time=self.parabola_time, rate_func=smooth)
            animations.append(anim)

        self.play(*animations, lag_ratio=0.15)

    def update_target_bar(self):
        for sp in self.moving_splinters:
            self.remove(sp)
        self.remove(self.target_bar)

        self.target_bar_final = Rectangle(
            width=self.bar_width, height=self.target_final_height,
            color=self.target_color, fill_opacity=1
        ).move_to(self.target_pos).align_to([0, self.base_y, 0], DOWN)

        self.add(self.target_bar_final)

    def animate_target_compression(self):
        scale_y = 0.92
        scale_x = 1 / scale_y
        base = self.target_bar_final.get_bottom()[1]
        new_height = self.target_bar_final.height * scale_y

        self.target_bar_final.generate_target()
        self.target_bar_final.target.stretch(scale_x, 0)
        self.target_bar_final.target.stretch(scale_y, 1)
        self.target_bar_final.target.move_to([self.target_pos[0], base + new_height / 2, 0])
        self.play(MoveToTarget(self.target_bar_final), run_time=0.25)

        self.target_bar_final.generate_target()
        self.target_bar_final.target.stretch(1 / scale_x, 0)
        self.target_bar_final.target.stretch(1 / scale_y, 1)
        self.target_bar_final.target.move_to([self.target_pos[0], base + self.target_final_height / 2, 0])
        self.play(MoveToTarget(self.target_bar_final), run_time=0.25)

    def animate_question_mark(self):
        q = Text("?", color=YELLOW, stroke_width=8, stroke_color=ORANGE).scale(0.1)
        center = (self.source_pos + self.target_pos) / 2 + UP * 0.5
        q.move_to(center)
        q.set_opacity(0)
        self.add(q)
        self.play(
            FadeIn(q),
            q.animate.scale(200.0).set_opacity(1),
            run_time=0.6,
            rate_func=overshoot
        )
        self.play(q.animate.scale(0.95), run_time=0.2, rate_func=smooth)

    def show_caption(self, text):
        shadow = Text(text, font_size=48, color=BLACK)
        shadow.set_opacity(0.3)
        shadow.shift(0.06 * DOWN + 0.06 * RIGHT)

        caption = Text(text, font_size=48, color=WHITE)
        caption_group = VGroup(shadow, caption)
        caption_group.to_edge(DOWN, buff=0.6)

        self.add(caption_group)
