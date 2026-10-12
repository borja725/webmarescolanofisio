# -*- coding: utf-8 -*-
"""Transcribe a WhatsApp voice note so it can be pasted into the agent.

    python tools/transcribir.py "ruta/al/audio.ogg"

Runs entirely on this machine: the audio never leaves it, which matters because
these recordings are a health professional talking about her patients.

faster-whisper rather than the original openai-whisper: it needs no external
ffmpeg (there is none installed here), runs several times faster on a CPU and
does not drag in PyTorch, which is gigabytes. The model downloads once, the
first time, into the user's cache.

'small' is enough for dictated Spanish. If a recording comes out poorly - noisy
room, several people talking - rerun it with 'medium' as the second argument.
"""
import os
import sys
import time

from faster_whisper import WhisperModel

audio = sys.argv[1] if len(sys.argv) > 1 else None
size = sys.argv[2] if len(sys.argv) > 2 else 'small'
if not audio or not os.path.exists(audio):
    raise SystemExit('uso: python tools/transcribir.py "ruta/al/audio.ogg" [small|medium]')

print('audio  : %s (%.0f KB)' % (os.path.basename(audio), os.path.getsize(audio) / 1024))
print('modelo : %s' % size)
print('')
t0 = time.time()

# int8 keeps it fast and light on a CPU; the accuracy cost on dictated speech
# is not noticeable
model = WhisperModel(size, device='cpu', compute_type='int8')
segments, info = model.transcribe(audio, language='es', vad_filter=True,
                                  beam_size=5)

print('duracion detectada: %.0f s' % info.duration)
print('')
print('-' * 70)
partes = []
for s in segments:
    partes.append(s.text.strip())
    print('[%5.1f - %5.1f] %s' % (s.start, s.end, s.text.strip()))
print('-' * 70)
print('')

texto = ' '.join(partes)
out = os.path.splitext(audio)[0] + '.txt'
open(out, 'w', encoding='utf-8').write(texto + '\n')
print('%d palabras, %.0f s de proceso' % (len(texto.split()), time.time() - t0))
print('guardado en: %s' % out)
