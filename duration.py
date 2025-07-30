from tts import TTS
from pydub import AudioSegment

def cargar_lineas_narracion(path):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    # Filtrar: quitar líneas vacías y líneas visuales (que empiezan con ">")
    narracion = [line.strip() for line in lines if line.strip() and not line.strip().startswith(">")]
    return narracion

def calcular_duracion(lines):
    total_ms = 0
    with TTS(lang='es') as tts:
        for line in lines:
            print(line)
            path = tts.speak(line)
            audio = AudioSegment.from_file(path)
            total_ms += len(audio)
    return total_ms

if __name__ == "__main__":
    archivo = "script.md"
    lineas = cargar_lineas_narracion(archivo)
    duracion_ms = calcular_duracion(lineas)
    duracion_seg = duracion_ms / 1000
    minutos = int(duracion_seg // 60)
    segundos = int(duracion_seg % 60)

    print(f"Duración estimada: {duracion_seg:.1f} segundos ({minutos}:{segundos:02d})")

