# night_shift.py — Night Shift – Emergency Decision System
# Python 3.9+ | pygame only
from __future__ import annotations

import pygame
import random
import math
import sys
import time
import array
import struct
import io
import os
import traceback

pygame.init()
# Le mixeur est initialisé APRÈS pygame.display.set_mode() (voir GameManager).
# L'ordre « fenêtre d'abord » évite des plantages SDL fréquents sous Windows au 1er clic.

# ── Constantes ─────────────────────────────────────────────────────────────
W, H = 1280, 720
FPS = 60
HUD_H = 50
ROOM_W, ROOM_H = 800, 620
PANEL_W = 480
NOTIF_H = 50

COLORS = {
    "bg": (10, 26, 46),
    "bg2": (13, 31, 56),
    "bg3": (7, 17, 31),
    "panel": (11, 25, 48),
    "border": (30, 58, 96),
    "blue": (79, 195, 247),
    "blue_d": (24, 95, 165),
    "teal": (29, 158, 117),
    "green": (76, 175, 80),
    "green_d": (27, 94, 32),
    "yellow": (255, 179, 0),
    "red": (244, 67, 54),
    "red_d": (130, 30, 20),
    "white": (224, 232, 240),
    "grey": (120, 160, 190),
    "grey_d": (50, 80, 110),
    "black": (5, 12, 22),
}

DISEASES = [
    {
        "name": "Grippe",
        "symptoms": ["Fièvre", "Fatigue", "Courbatures", "Toux"],
        "severity": "mild",
        "base_gain": 100,
        "key_exam": "nfs",
    },
    {
        "name": "Pneumonie",
        "symptoms": ["Fièvre", "Toux grasse", "Douleur thoracique", "Dyspnée"],
        "severity": "moderate",
        "base_gain": 250,
        "key_exam": "radio",
    },
    {
        "name": "Appendicite",
        "symptoms": ["Douleur FID", "Fièvre", "Nausées", "Défense abdominale"],
        "severity": "moderate",
        "base_gain": 300,
        "key_exam": "echo",
    },
    {
        "name": "Asthme aigu",
        "symptoms": ["Dyspnée", "Sibilances", "Toux", "Cyanose"],
        "severity": "moderate",
        "base_gain": 200,
        "key_exam": "spo2",
    },
    {
        "name": "Infarctus",
        "symptoms": ["Douleur thoracique", "Irradiation bras gauche", "Sueurs", "Nausées"],
        "severity": "critical",
        "base_gain": 600,
        "key_exam": "ecg",
    },
    {
        "name": "Fracture",
        "symptoms": ["Douleur locale", "Déformation", "Impotence fonctionnelle", "Oedème"],
        "severity": "mild",
        "base_gain": 150,
        "key_exam": "radio",
    },
    {
        "name": "Hémorragie interne",
        "symptoms": ["Hypotension", "Tachycardie", "Pâleur", "Douleur abdominale"],
        "severity": "critical",
        "base_gain": 700,
        "key_exam": "echo",
    },
]

EXAMS = {
    "nfs": {"label": "Bilan sanguin (NFS)", "cost": 30, "duration_sec": 0},
    "radio": {"label": "Radiographie", "cost": 50, "duration_sec": 0},
    "echo": {"label": "Échographie", "cost": 80, "duration_sec": 0},
    "ecg": {"label": "ECG", "cost": 40, "duration_sec": 0},
    "spo2": {"label": "Saturation O2", "cost": 10, "duration_sec": 0},
}

EXAM_RESULTS = {
    "nfs": {
        "Grippe": "Leucocytes 12 000/µL — syndrome inflammatoire viral",
        "Pneumonie": "Leucocytes 18 000/µL, CRP 120 — infection bactérienne",
        "Infarctus": "Troponines élevées à 2.4 µg/L — nécrose myocardique",
        "_default": "NFS dans les normes — pas d'anomalie notable",
    },
    "radio": {
        "Pneumonie": "Opacité alvéolaire lobe inférieur droit confirmée",
        "Fracture": "Fracture diaphysaire visible, déplacement 2 mm",
        "Asthme aigu": "Distension thoracique bilatérale, pas d'opacité",
        "_default": "Radiographie sans anomalie significative",
    },
    "echo": {
        "Appendicite": "Appendice mesuré 12 mm, non compressible — appendicite",
        "Hémorragie interne": "Épanchement intra-abdominal libre — hémorragie active",
        "_default": "Échographie abdominale normale",
    },
    "ecg": {
        "Infarctus": "Sus-décalage ST en V1-V4 — STEMI confirmé",
        "Asthme aigu": "Tachycardie sinusale 110/min",
        "_default": "Rythme sinusal régulier, pas d'anomalie",
    },
    "spo2": {
        "Asthme aigu": "SpO2 87 % — désaturation critique, O2 urgent",
        "Pneumonie": "SpO2 92 % — légère désaturation",
        "_default": "SpO2 98 % — saturation normale",
    },
}

NOISE_SYMPTOMS = ["Céphalées", "Vertiges", "Anorexie", "Insomnie", "Anxiété", "Asthénie"]

BED_W, BED_H = 170, 140
BED_POSITIONS = [
    (20, 80),
    (220, 80),
    (420, 80),
    (620, 80),
    (20, 230),
    (220, 230),
    (420, 230),
    (620, 230),
]

FIRST_NAMES = [
    "Lucas", "Emma", "Hugo", "Léa", "Noah", "Chloé", "Louis", "Manon",
    "Gabriel", "Camille", "Arthur", "Julie",
]
LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Petit", "Durand", "Leroy",
    "Moreau", "Simon", "Laurent", "Lefebvre",
]

SKIN_COLORS = [
    (255, 219, 172),
    (241, 194, 125),
    (224, 172, 105),
    (198, 134, 66),
    (141, 85, 36),
    (92, 51, 23),
]

SEVERITY_LABELS = {"mild": "LÉGER", "moderate": "MODÉRÉ", "critical": "CRITIQUE"}
SEVERITY_COLORS = {
    "mild": COLORS["green"],
    "moderate": COLORS["yellow"],
    "critical": COLORS["red"],
}

EQUIPMENT_DEFS = [
    {"id": "ct", "name": "Scanner CT", "cost": 300, "desc": "+5 % précision"},
    {"id": "lab", "name": "Laboratoire rapide", "cost": 200, "desc": "+5 % précision"},
    {"id": "defib", "name": "Défibrillateur avancé", "cost": 250, "desc": "+5 % précision"},
]

DISEASE_WEIGHTS = []
for d in DISEASES:
    if d["severity"] == "mild":
        DISEASE_WEIGHTS.append(40 / 2)
    elif d["severity"] == "moderate":
        DISEASE_WEIGHTS.append(30 / 3)
    else:
        DISEASE_WEIGHTS.append(30 / 2)


# ── Audio procédural ───────────────────────────────────────────────────────
def _adsr_envelope(n_samples: int, sr: int, attack_ms=10, release_ms=50) -> list:
    atk = int(sr * attack_ms / 1000)
    rel = int(sr * release_ms / 1000)
    env = []
    for i in range(n_samples):
        if i < atk and atk > 0:
            e = i / atk
        elif i >= n_samples - rel and rel > 0:
            e = max(0.0, (n_samples - 1 - i) / rel)
        else:
            e = 1.0
        env.append(e)
    return env


def _pcm_stereo_to_wav_bytes(samples_left: array.array) -> bytes:
    """samples_left: 'h' signed 16 mono; duplicate to stereo."""
    n = len(samples_left)
    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + n * 4))
    buf.write(b"WAVEfmt ")
    buf.write(struct.pack("<IHHIIHH", 16, 1, 2, 44100, 44100 * 4, 4, 16))
    buf.write(b"data")
    buf.write(struct.pack("<I", n * 4))
    for s in samples_left:
        buf.write(struct.pack("<hh", s, s))
    return buf.getvalue()


def _triangle(phase: float) -> float:
    return 2.0 * abs(2.0 * (phase / (2 * math.pi) - math.floor(phase / (2 * math.pi) + 0.5))) - 1.0


class AudioManager:
    """Musique et SFX procéduraux (aucun fichier externe)."""

    def __init__(self):
        self.music_sound: pygame.mixer.Sound | None = None
        self._snd_success = None
        self._snd_error = None
        self._snd_alert = None
        self._snd_info = None
        self._mixer_usable = False
        self.music_on = True
        self.sfx_on = True
        self.music_vol = 0.6
        self.sfx_vol = 0.7
        if os.environ.get("NIGHT_SHIFT_NO_AUDIO", "").strip() in ("1", "true", "yes"):
            return
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            self._build_music()
            self._snd_success = self._sfx_freq_sweep(523.0, 659.0, 0.25, True)
            self._snd_error = self._sfx_freq_sweep(150.0, 130.0, 0.5, False)
            self._snd_alert = self._sfx_beep(880.0, 0.15)
            self._snd_info = self._sfx_beep(330.0, 0.2)
            self._mixer_usable = True
        except Exception:
            self.music_sound = None
            self._snd_success = self._snd_error = self._snd_alert = self._snd_info = None
            self._mixer_usable = False

    def _build_music(self):
        sr = 44100
        bpm = 72.0
        beat = 60.0 / bpm
        measures = 16
        beats_total = measures * 4
        duration = beat * beats_total
        n = int(duration * sr)
        # Notes (Hz): La 220, Do 261, Si 246, etc.
        notes = [220.0, 261.63, 246.94, 196.0, 174.61, 220.0, 293.66, 261.63]
        bass_f = 55.0
        arr = array.array("h")
        env_global = _adsr_envelope(n, sr, attack_ms=50, release_ms=200)
        for i in range(n):
            t = i / sr
            beat_idx = int(t / beat) % beats_total
            step = beat_idx % len(notes)
            f_m = notes[step]
            mel = math.sin(2 * math.pi * f_m * t) * 0.12
            bass = _triangle(2 * math.pi * bass_f * t + beat_idx * 0.1) * 0.18
            rhythm = math.sin(2 * math.pi * (82.0) * t) * 0.04
            if int(t / (beat / 2)) % 2 == 0:
                rhythm *= 0.3
            s = mel + bass + rhythm
            s = max(-1.0, min(1.0, s)) * env_global[i]
            v = int(s * 28000)
            arr.append(v)
        wav = _pcm_stereo_to_wav_bytes(arr)
        self.music_sound = pygame.mixer.Sound(file=io.BytesIO(wav))

    def _sfx_freq_sweep(self, f0: float, f1: float, dur: float, up: bool) -> pygame.mixer.Sound:
        sr = 44100
        n = int(dur * sr)
        arr = array.array("h")
        env = _adsr_envelope(n, sr, 10, 50)
        for i in range(n):
            u = i / max(1, n - 1)
            f = f0 + (f1 - f0) * (u if up else (1 - u))
            ph = 2 * math.pi * f * (i / sr)
            s = math.sin(ph) * 0.45 * env[i]
            arr.append(int(s * 30000))
        return pygame.mixer.Sound(file=io.BytesIO(_pcm_stereo_to_wav_bytes(arr)))

    def _sfx_beep(self, freq: float, dur: float) -> pygame.mixer.Sound:
        sr = 44100
        n = int(dur * sr)
        arr = array.array("h")
        env = _adsr_envelope(n, sr, 10, 50)
        for i in range(n):
            s = math.sin(2 * math.pi * freq * (i / sr)) * 0.5 * env[i]
            arr.append(int(s * 30000))
        return pygame.mixer.Sound(file=io.BytesIO(_pcm_stereo_to_wav_bytes(arr)))

    def play_music(self):
        if not self._mixer_usable or not self.music_on or self.music_sound is None:
            return
        try:
            self.music_sound.set_volume(self.music_vol * 0.5)
            self.music_sound.play(loops=-1)
        except Exception:
            pass

    def stop_music(self):
        try:
            if self.music_sound:
                self.music_sound.stop()
        except Exception:
            pass

    def set_music_volume_live(self):
        try:
            if self._mixer_usable and self.music_sound and self.music_sound.get_num_channels() > 0:
                self.music_sound.set_volume(self.music_vol * 0.5)
        except Exception:
            pass

    def play_success(self):
        if not self._mixer_usable or not self.sfx_on or self._snd_success is None:
            return
        try:
            self._snd_success.set_volume(self.sfx_vol)
            self._snd_success.play()
        except Exception:
            pass

    def play_error(self):
        if not self._mixer_usable or not self.sfx_on or self._snd_error is None:
            return
        try:
            self._snd_error.set_volume(self.sfx_vol)
            self._snd_error.play()
        except Exception:
            pass

    def play_alert(self):
        if not self._mixer_usable or not self.sfx_on or self._snd_alert is None:
            return
        try:
            self._snd_alert.set_volume(self.sfx_vol)
            self._snd_alert.play()
        except Exception:
            pass

    def play_info(self):
        if not self._mixer_usable or not self.sfx_on or self._snd_info is None:
            return
        try:
            self._snd_info.set_volume(self.sfx_vol * 0.9)
            self._snd_info.play()
        except Exception:
            pass


# ── Patient ────────────────────────────────────────────────────────────────
class Patient:
    _next_id = 1

    def __init__(self, disease: dict, difficulty_multiplier: float):
        self.id = Patient._next_id
        Patient._next_id += 1
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        self.name = f"{fn} {ln}"
        self.age = random.randint(18, 75)
        self.skin_color = random.choice(SKIN_COLORS)
        self.disease = disease
        self.severity = disease["severity"]
        base_syms = list(disease["symptoms"])
        n_noise = random.randint(0, 2)
        noise = random.sample(NOISE_SYMPTOMS, min(n_noise, len(NOISE_SYMPTOMS)))
        self.symptoms = base_syms + noise
        random.shuffle(self.symptoms)
        others = [d["name"] for d in DISEASES if d["name"] != disease["name"]]
        wrong = random.sample(others, min(3, len(others)))
        opts = [disease["name"]] + wrong
        random.shuffle(opts)
        self.diag_options = opts
        self.status = "waiting"
        self.wait_seconds = 0
        self.exams_done: list[str] = []
        self.exam_results: dict[str, str] = {}
        self.selected_diag: str | None = None
        self.anim_phase = random.random() * math.tau
        self.flash_timer = 0.0
        self.flash_ok: bool | None = None
        self.bed_index = -1
        sev = self.severity
        if sev == "mild":
            self.max_wait = int(350 * difficulty_multiplier)
        elif sev == "moderate":
            self.max_wait = int(190 * difficulty_multiplier)
        else:
            self.max_wait = int(110 * difficulty_multiplier)
        self.status_since: float | None = None

    def max_survival_seconds(self) -> int:
        return self.max_wait


# ── Button ─────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, text, font, bg_color, text_color, radius=6):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.radius = radius
        self.hovered = False
        self.disabled = False

    def draw(self, surface: pygame.Surface):
        bg = self.bg_color
        if self.disabled:
            bg = tuple(max(0, c // 3) for c in bg[:3])
        elif self.hovered:
            bg = tuple(min(255, int(c * 1.12)) for c in bg[:3])
        pygame.draw.rect(surface, bg, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, COLORS["border"], self.rect, 1, border_radius=self.radius)
        tc = COLORS["grey_d"] if self.disabled else self.text_color
        surf = self.font.render(self.text, True, tc)
        r = surf.get_rect(center=self.rect.center)
        surface.blit(surf, r)

    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos) and not self.disabled

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
            and not self.disabled
        )


# ── Economy (Model) ─────────────────────────────────────────────────────────
class EconomyManager:
    def __init__(self):
        self.budget = 1000
        self.reputation = 100
        self.fatigue = 0.0
        self.level = 1
        self.xp = 0
        self.equipment_owned: set[str] = set()
        self.consecutive_errors = 0
        self.total_errors = 0
        self.patients_treated = 0
        self.patients_dead = 0
        self._audio: AudioManager | None = None

    def reset_for_new_shift(self):
        self.budget = 1000
        self.reputation = 100
        self.fatigue = 0.0
        self.level = 1
        self.xp = 0
        self.equipment_owned.clear()
        self.consecutive_errors = 0
        self.total_errors = 0
        self.patients_treated = 0
        self.patients_dead = 0

    def survival_rate(self) -> float:
        tot = self.patients_treated + self.patients_dead
        if tot <= 0:
            return 100.0
        return 100.0 * self.patients_treated / tot

    def add_xp(self, amount: int):
        self.xp += amount
        while self.level < 10 and self.xp >= self.level * 100:
            self.xp -= self.level * 100
            self.level += 1
            if self._audio:
                self._audio.play_alert()

    def equipment_count(self) -> int:
        return len(self.equipment_owned)

    def buy_equipment(self, eq_id: str, cost: int) -> bool:
        if eq_id in self.equipment_owned or self.budget < cost:
            return False
        self.budget -= cost
        self.equipment_owned.add(eq_id)
        return True


# ── Diagnostic (Model) ─────────────────────────────────────────────────────
class DiagnosticEngine:
    @staticmethod
    def compute_accuracy(level: int, equip_count: int, fatigue: float) -> float:
        competence = 1.0 + (level * 0.03)
        equipment = 1.0 + (equip_count * 0.05)
        fatigue_malus = fatigue * 0.02
        prec = 0.75 * competence * equipment * (1.0 - fatigue_malus / 100.0)
        return min(0.98, prec)


# ── PatientManager (Controller) ────────────────────────────────────────────
class PatientManager:
    def __init__(self, economy: EconomyManager, audio: AudioManager):
        self.economy = economy
        self.audio = audio
        self.patients: list[Patient] = []
        self.spawn_timer = 0
        self.difficulty_multiplier = 0.8
        self._timeout_logged: set[int] = set()

    def reset(self, difficulty_multiplier: float):
        self.patients.clear()
        self.spawn_timer = 0
        self.difficulty_multiplier = difficulty_multiplier
        self._timeout_logged.clear()
        Patient._next_id = 1

    def _bed_occupied(self, idx: int) -> bool:
        for p in self.patients:
            if p.bed_index == idx:
                return True
        return False

    def _free_bed_index(self) -> int | None:
        for i in range(len(BED_POSITIONS)):
            if not self._bed_occupied(i):
                return i
        return None

    def waiting_count(self) -> int:
        return sum(1 for p in self.patients if p.status == "waiting")

    def spawn_interval(self) -> float:
        lv = self.economy.level
        if lv <= 3:
            base = 40
        elif lv <= 6:
            base = 28
        else:
            base = 18
        return max(8.0, base * self.difficulty_multiplier)

    def try_spawn(self) -> Patient | None:
        if self.waiting_count() >= 8:
            return None
        bi = self._free_bed_index()
        if bi is None:
            return None
        disease = random.choices(DISEASES, weights=DISEASE_WEIGHTS, k=1)[0]
        p = Patient(dict(disease), self.difficulty_multiplier)
        p.bed_index = bi
        self.patients.append(p)
        return p

    def get_patient_at_bed_click(self, pos) -> Patient | None:
        mx, my = pos
        if mx >= ROOM_W:
            return None
        room_y = my - HUD_H
        if room_y < 0 or room_y >= ROOM_H:
            return None
        for p in self.patients:
            if p.status != "waiting":
                continue
            bx, by = BED_POSITIONS[p.bed_index]
            rect = pygame.Rect(bx, by, BED_W, BED_H)
            if rect.collidepoint(mx, room_y):
                return p
        return None

    def do_exam(self, patient: Patient, exam_key: str, game_log) -> bool:
        if patient.status != "waiting":
            return False
        if exam_key in patient.exams_done:
            return False
        info = EXAMS[exam_key]
        if self.economy.budget < info["cost"]:
            return False
        self.economy.budget -= info["cost"]
        patient.exams_done.append(exam_key)
        res_map = EXAM_RESULTS.get(exam_key, {})
        dname = patient.disease["name"]
        txt = res_map.get(dname, res_map.get("_default", "RAS"))
        patient.exam_results[exam_key] = txt
        game_log.append(("cyan", f"Examen {info['label']} - {patient.name}"))
        self.audio.play_info()
        return True

    def treat_patient(self, patient: Patient, game_log) -> None:
        if patient.status != "waiting" or patient.selected_diag is None:
            return
        d = patient.disease
        correct = patient.selected_diag == d["name"]
        acc = DiagnosticEngine.compute_accuracy(
            self.economy.level, self.economy.equipment_count(), self.economy.fatigue
        )
        if correct and random.random() < acc:
            gain = d["base_gain"] + 100
            if patient.wait_seconds < 60:
                gain += 50
            self.economy.budget += gain
            if d["severity"] == "critical":
                self.economy.reputation = min(100, self.economy.reputation + 8)
            else:
                self.economy.reputation = min(100, self.economy.reputation + 4)
            if d["severity"] == "critical":
                self.economy.add_xp(30)
            elif d["severity"] == "moderate":
                self.economy.add_xp(20)
            else:
                self.economy.add_xp(10)
            self.economy.consecutive_errors = 0
            patient.status = "treated"
            patient.status_since = time.time()
            patient.flash_ok = True
            patient.flash_timer = 1.0
            self.economy.patients_treated += 1
            game_log.append(("green", f"Succes - {patient.name} ({d['name']}) +{gain} EUR"))
            self.audio.play_success()
        else:
            if d["severity"] == "critical":
                pen = 200
            elif d["severity"] == "moderate":
                pen = 120
            else:
                pen = 60
            self.economy.budget -= pen
            if not correct:
                self.economy.reputation = max(0, self.economy.reputation - 15)
            else:
                self.economy.reputation = max(0, self.economy.reputation - 5)
            self.economy.consecutive_errors += 1
            self.economy.total_errors += 1
            self.economy.patients_dead += 1
            patient.status = "dead"
            patient.status_since = time.time()
            patient.flash_ok = False
            patient.flash_timer = 1.0
            msg = "Mauvais diagnostic" if not correct else "Échec technique malgré bon diagnostic"
            game_log.append(("red", f"{msg} - {patient.name} (-{pen} EUR)"))
            self.audio.play_error()

    def delegate_patient(self, patient: Patient, game_log) -> None:
        if patient.status != "waiting":
            return
        d = patient.disease
        gain = int(d["base_gain"] * 0.8)
        self.economy.budget += gain
        self.economy.reputation = max(0, self.economy.reputation - 3)
        self.economy.add_xp(5)
        patient.status = "treated"
        patient.status_since = time.time()
        patient.flash_ok = True
        patient.flash_timer = 0.8
        self.economy.patients_treated += 1
        self.economy.consecutive_errors = 0
        game_log.append(("yellow", f"Delegation - {patient.name} +{gain} EUR (reputation -3)"))
        self.audio.play_info()

    def tick_waiting(self, game_log: list):
        for p in self.patients:
            if p.status == "waiting":
                p.wait_seconds += 1
                if p.wait_seconds >= p.max_survival_seconds():
                    p.status = "dead"
                    p.status_since = time.time()
                    p.flash_ok = False
                    p.flash_timer = 1.0
                    self.economy.patients_dead += 1
                    self.economy.consecutive_errors += 1
                    self.economy.total_errors += 1
                    if p.id not in self._timeout_logged:
                        self._timeout_logged.add(p.id)
                        game_log.append(("red", f"Délai dépassé — {p.name} ({p.disease['name']})"))

    def cleanup_finished(self, game_log):
        now = time.time()
        to_remove: list[Patient] = []
        for p in self.patients:
            if p.status not in ("dead", "treated"):
                continue
            if p.status_since is None:
                p.status_since = now
            if now - p.status_since >= 2.5:
                to_remove.append(p)
        for p in to_remove:
            if p in self.patients:
                self.patients.remove(p)


# ── UIManager (View) ───────────────────────────────────────────────────────
def _font(size: int, bold: bool = False) -> pygame.font.Font:
    """SysFont Segoe UI si dispo, sinon police bitmap pygame (évite plantages TTF)."""
    try:
        f = pygame.font.SysFont("segoeui", size, bold=bold)
        f.render("Hg", True, (255, 255, 255))
        return f
    except Exception:
        try:
            return pygame.font.SysFont("arial", size, bold=bold)
        except Exception:
            return pygame.font.Font(None, size)


class UIManager:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.fonts = {
            "huge": _font(58, True),
            "big": _font(34, True),
            "title": _font(21, True),
            "medium": _font(17, True),
            "body": _font(15, False),
            "small": _font(12, False),
            "tiny": _font(10, False),
        }

    def _text(self, key, t, color, bold=False):
        f = self.fonts.get(key, self.fonts["body"])
        return f.render(t, True, color)

    def draw_menu(self, t_anim: float):
        self.screen.fill((11, 26, 46))
        # ECG décor
        pts = []
        for x in range(0, W + 8, 4):
            phase = (x * 0.08 + t_anim * 120) % (math.tau * 2)
            y = 360 + math.sin(phase) * 8
            if int(x / 40) % 7 == 3:
                y -= 35
            pts.append((x, y))
        if len(pts) > 1:
            pygame.draw.lines(self.screen, COLORS["blue"], False, pts, 2)
        t1 = self.fonts["huge"].render("NIGHT SHIFT", True, COLORS["blue"])
        r1 = t1.get_rect(center=(W // 2, 200))
        self.screen.blit(t1, r1)
        t2 = self.fonts["title"].render("Emergency Decision System", True, COLORS["grey"])
        r2 = t2.get_rect(center=(W // 2, 270))
        self.screen.blit(t2, r2)

    def draw_settings(self, settings_state: dict):
        self.screen.fill(COLORS["bg"])
        title = self.fonts["big"].render("RÉGLAGES", True, COLORS["blue"])
        self.screen.blit(title, (40, 40))

    def draw_hud(
        self,
        surface: pygame.Surface,
        time_left: int,
        budget: int,
        rep: int,
        surv: float,
        level: int,
        fatigue: float,
        err_c: int,
        y_offset: int = 0,
    ):
        hud = pygame.Rect(0, y_offset, W, HUD_H)
        pygame.draw.rect(surface, COLORS["bg3"], hud)
        pygame.draw.line(surface, COLORS["border"], (0, HUD_H - 1 + y_offset), (W, HUD_H - 1 + y_offset))
        tiny = self.fonts["tiny"]
        parts = [
            ("NIGHT SHIFT", COLORS["blue"]),
            (f"Temps {time_left // 60:02d}:{time_left % 60:02d}", COLORS["white"]),
            (f"Budget {budget} EUR", COLORS["yellow"]),
            (f"Répu {rep}", COLORS["teal"]),
            (f"Survie {surv:.0f}%", COLORS["green"]),
            (f"Nv {level}", COLORS["blue"]),
            (f"Fatigue {fatigue:.0f}%", COLORS["grey"]),
            (f"Err↯ {err_c}", COLORS["red"] if err_c > 0 else COLORS["grey"]),
        ]
        x = 12
        for txt, col in parts:
            s = tiny.render(txt, True, col)
            surface.blit(s, (x, 8 + y_offset))
            x += s.get_width() + 18

    def draw_room_background(self, surface: pygame.Surface, room_rect: pygame.Rect, animations_on: bool, t: float):
        pygame.draw.rect(surface, (12, 30, 54), room_rect)
        # plafond néons
        ceil = pygame.Rect(room_rect.x, room_rect.y, room_rect.w, 28)
        pygame.draw.rect(surface, (8, 20, 40), ceil)
        for i in range(5):
            nx = room_rect.x + 40 + i * 150
            a = 120 if animations_on else 80
            neon = pygame.Surface((120, 6), pygame.SRCALPHA)
            neon.fill((120, 200, 255, a))
            surface.blit(neon, (nx, room_rect.y + 10))
        # grille sol
        floor_y = room_rect.bottom - 40
        for gx in range(room_rect.x, room_rect.right, 28):
            pygame.draw.line(surface, (25, 45, 70), (gx, floor_y), (gx, room_rect.bottom), 1)
        for gy in range(floor_y, room_rect.bottom, 24):
            pygame.draw.line(surface, (25, 45, 70), (room_rect.x, gy), (room_rect.right, gy), 1)
        lab = self.fonts["title"].render("URGENCES — GARDE DE NUIT", True, COLORS["blue"])
        lr = lab.get_rect(center=(room_rect.centerx, room_rect.y + 48))
        surface.blit(lab, lr)
        # 4 moniteurs ECG bas
        mw, mh = 160, 50
        for i in range(4):
            bx = room_rect.x + 20 + i * (mw + 15)
            by = room_rect.bottom - mh - 12
            pygame.draw.rect(surface, COLORS["black"], (bx, by, mw, mh), border_radius=4)
            pygame.draw.rect(surface, COLORS["border"], (bx, by, mw, mh), 1, border_radius=4)
            pts = []
            for u in range(0, mw, 3):
                ph = t * 3 + u * 0.1 + i
                yy = by + mh // 2 + math.sin(ph) * 10
                if u % 33 < 4:
                    yy -= 14
                pts.append((bx + u, int(yy)))
            if len(pts) > 1:
                pygame.draw.lines(surface, COLORS["green"], False, pts, 1)

    def draw_bed(
        self,
        surface: pygame.Surface,
        bx: int,
        by: int,
        patient: Patient | None,
        selected: bool,
        t: float,
        animations_on: bool,
    ):
        bed_rect = pygame.Rect(bx, by, BED_W, BED_H)
        sev_color = COLORS["blue_d"]
        if patient and patient.status == "waiting":
            sev_color = SEVERITY_COLORS.get(patient.severity, COLORS["blue_d"])
        # lit
        pygame.draw.rect(surface, (20, 40, 80), bed_rect, border_radius=10)
        band = pygame.Rect(bx + 4, by + 4, BED_W - 8, 22)
        pygame.draw.rect(surface, sev_color, band, border_radius=4)
        inner = pygame.Rect(bx + 10, by + 32, BED_W - 20, BED_H - 42)
        pygame.draw.rect(surface, (40, 70, 110), inner, border_radius=6)
        if selected:
            pygame.draw.rect(surface, COLORS["blue"], bed_rect.inflate(6, 6), 3, border_radius=12)

        if patient is None:
            txt = self.fonts["small"].render("Disponible", True, COLORS["grey_d"])
            tr = txt.get_rect(center=bed_rect.center)
            surface.blit(txt, tr)
            return

        name_s = self.fonts["tiny"].render(patient.name[:14], True, COLORS["white"])
        surface.blit(name_s, (bx + 8, by + 6))

        # badge sévérité
        badge = pygame.Rect(bx + BED_W - 72, by + 6, 66, 16)
        pygame.draw.rect(surface, SEVERITY_COLORS.get(patient.severity, COLORS["grey"]), badge, border_radius=3)
        bl = SEVERITY_LABELS.get(patient.severity, "?")
        bs = self.fonts["tiny"].render(bl, True, COLORS["black"])
        surface.blit(bs, (badge.x + 4, badge.y + 2))

        # patient stick figure
        if patient.status == "waiting" or patient.status in ("treated", "dead"):
            oy = 0
            if animations_on and patient.severity == "critical" and patient.status == "waiting":
                oy = int(math.sin(t * 4 + patient.anim_phase) * 3)
            cx, cy = bed_rect.centerx, by + 78 + oy
            pygame.draw.circle(surface, patient.skin_color, (cx, cy - 28), 14)
            pygame.draw.circle(surface, (30, 30, 40), (cx - 5, cy - 30), 2)
            pygame.draw.circle(surface, (30, 30, 40), (cx + 5, cy - 30), 2)
            if patient.severity == "critical" and patient.status == "waiting":
                pygame.draw.arc(surface, COLORS["red"], (cx - 8, cy - 22, 16, 12), 3.5, 5.5, 2)
            else:
                pygame.draw.arc(surface, (40, 40, 50), (cx - 8, cy - 24, 16, 10), 0.2, 2.9, 2)
            scrubs = SEVERITY_COLORS.get(patient.severity, COLORS["blue_d"])
            body = pygame.Rect(cx - 22, cy - 10, 44, 40)
            pygame.draw.rect(surface, scrubs, body, border_radius=6)
            pygame.draw.ellipse(surface, scrubs, (cx - 38, cy - 6, 18, 28))
            pygame.draw.ellipse(surface, scrubs, (cx + 20, cy - 6, 18, 28))
            leg = pygame.Rect(cx - 18, cy + 28, 36, 22)
            pygame.draw.rect(surface, (50, 70, 100), leg, border_radius=4)

        if patient.status == "critical" and patient.severity == "critical" and animations_on:
            pulse = int((math.sin(t * 6) * 0.5 + 0.5) * 255)
            pygame.draw.circle(surface, (pulse, 40, 40), (bx + BED_W - 14, by + 14), 5)

        # barre attente
        max_w = BED_W - 16
        ratio = min(1.0, patient.wait_seconds / max(1, patient.max_survival_seconds()))
        bar_bg = pygame.Rect(bx + 8, by + BED_H - 16, max_w, 8)
        pygame.draw.rect(surface, COLORS["black"], bar_bg, border_radius=3)
        col = COLORS["green"]
        if ratio > 0.45:
            col = COLORS["yellow"]
        if ratio > 0.75:
            col = COLORS["red"]
        fill_w = int(max_w * ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, col, (bar_bg.x, bar_bg.y, fill_w, bar_bg.h), border_radius=3)
        m, s = divmod(max(0, patient.max_survival_seconds() - patient.wait_seconds), 60)
        ts = self.fonts["tiny"].render(f"{m}m {s}s", True, COLORS["white"])
        surface.blit(ts, (bx + 8, by + BED_H - 28))

        # overlays treated/dead
        if patient.status == "treated":
            ov = pygame.Surface((BED_W, BED_H), pygame.SRCALPHA)
            ov.fill((40, 120, 60, 120))
            surface.blit(ov, (bx, by))
            chk = self.fonts["medium"].render("+", True, COLORS["green"])
            surface.blit(chk, (bx + BED_W // 2 - 8, by + BED_H // 2 - 10))
        elif patient.status == "dead":
            ov = pygame.Surface((BED_W, BED_H), pygame.SRCALPHA)
            ov.fill((120, 20, 20, 130))
            surface.blit(ov, (bx, by))

    def draw_right_panel_frame(self, surface: pygame.Rect):
        pygame.draw.rect(self.screen, COLORS["panel"], surface)
        pygame.draw.line(self.screen, COLORS["border"], (surface.left, surface.top), (surface.left, surface.bottom), 2)

    def draw_notification(self, msg: str, msg_color):
        bar = pygame.Rect(0, H - NOTIF_H, W, NOTIF_H)
        pygame.draw.rect(self.screen, COLORS["bg3"], bar)
        pygame.draw.line(self.screen, COLORS["border"], (0, bar.top), (W, bar.top))
        s = self.fonts["body"].render(msg[:120], True, msg_color)
        self.screen.blit(s, (16, bar.y + 14))

    def wrap_text(self, text: str, font: pygame.font.Font, max_w: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines[:6]


# ── GameManager ─────────────────────────────────────────────────────────────
def _log_crash() -> None:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "night_shift_error.log")
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n---\n")
            traceback.print_exc(file=f)
    except OSError:
        pass


class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Night Shift - Emergency Decision System")
        if os.environ.get("NIGHT_SHIFT_NO_AUDIO", "").strip() not in ("1", "true", "yes"):
            try:
                pygame.mixer.quit()
            except Exception:
                pass
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            except Exception:
                pass
        self.clock = pygame.time.Clock()
        self.state = "menu"
        self.audio = AudioManager()
        self.economy = EconomyManager()
        self.economy._audio = self.audio
        self.patients = PatientManager(self.economy, self.audio)
        self.ui = UIManager(self.screen)
        self.sel: Patient | None = None
        self.time_left = 12 * 60
        self.last_tick = time.time()
        self.game_log: list[tuple[str, str]] = []
        self.notif = ("", COLORS["white"])
        self.end_won = False
        self.end_reason = ""
        self.show_management = False
        self.t_menu = 0.0
        self.t_game = 0.0
        # réglages
        self.set_music_on = True
        self.set_sfx_on = True
        self.music_vol_pct = 60
        self.sfx_vol_pct = 70
        self.shift_minutes = 12
        self.difficulty_key = "normal"  # easy normal hard
        self.animations_on = True
        self.settings_return_state = "menu"
        self.menu_quit_confirm = False
        # boutons menu (recréés chaque frame simplifié: stocker rects dans handle)
        self._menu_buttons: list[Button] = []
        self._settings_buttons: list[Button] = []
        self._hud_buttons: list[Button] = []
        self._end_buttons: list[Button] = []
        self._panel_regions: list[tuple] = []
        self.panel_scroll_y = 0
        self._panel_scroll_patient_id: int | None = None
        self._panel_max_scroll = 0

    def difficulty_multiplier(self) -> float:
        return {"easy": 1.0, "normal": 0.8, "hard": 0.6}.get(self.difficulty_key, 0.8)

    def apply_audio_settings(self):
        self.audio.music_on = self.set_music_on
        self.audio.sfx_on = self.set_sfx_on
        self.audio.music_vol = self.music_vol_pct / 100.0
        self.audio.sfx_vol = self.sfx_vol_pct / 100.0
        self.audio.set_music_volume_live()

    def log_add(self, kind: str, text: str):
        self.game_log.append((kind, text))
        if len(self.game_log) > 200:
            self.game_log = self.game_log[-120:]

    def sync_tick_clock(self):
        """Évite une rafale de game_tick après pause / overlay (temps réel ignoré)."""
        self.last_tick = time.time()

    def start_new_shift(self):
        self.economy.reset_for_new_shift()
        self.patients.reset(self.difficulty_multiplier())
        self.time_left = int(self.shift_minutes * 60)
        self.sync_tick_clock()
        self.game_log.clear()
        self.sel = None
        self.end_reason = ""
        self.show_management = False
        self.state = "game"
        self.panel_scroll_y = 0
        self._panel_scroll_patient_id = None
        self._panel_max_scroll = 0
        self.log_add("cyan", "Garde commencée — bon courage.")
        self.apply_audio_settings()
        if self.set_music_on:
            self.audio.stop_music()
            self.audio.play_music()
        else:
            self.audio.stop_music()
        self.patients.try_spawn()

    def check_defeat_immediate(self) -> str | None:
        e = self.economy
        if e.consecutive_errors >= 3:
            return "3 erreurs consécutives !"
        if e.budget < -500:
            return "Budget trop bas (< -500 EUR) !"
        tot = e.patients_treated + e.patients_dead
        if tot > 5 and e.patients_dead / tot > 0.40:
            return "Taux de mortalité trop élevé (> 40 %) !"
        return None

    def end_shift(self, premature: bool, reason: str = ""):
        self.state = "end"
        self.audio.stop_music()
        e = self.economy
        surv = e.survival_rate()
        if premature:
            self.end_won = False
            self.end_reason = reason
        else:
            self.end_won = surv >= 70 and e.budget >= 0 and e.reputation >= 30
            self.end_reason = "" if self.end_won else "Objectifs non atteints (survie ≥70 %, budget ≥0, réputation ≥30)"

    def game_tick(self):
        if self.state != "game" or self.show_management:
            return
        self.time_left -= 1
        fadd = 0.07 if self.economy.level >= 7 else 0.1
        self.economy.fatigue = min(100.0, self.economy.fatigue + fadd)
        self.patients.spawn_timer += 1
        interval = self.patients.spawn_interval()
        if self.patients.spawn_timer >= interval:
            self.patients.spawn_timer = 0
            self.patients.try_spawn()
        self.patients.tick_waiting(self.game_log)
        self.patients.cleanup_finished(self.game_log)
        if self.sel and self.sel.status != "waiting":
            self.sel = None
        lose = self.check_defeat_immediate()
        if lose:
            self.end_shift(True, lose)
            return
        if self.time_left <= 0:
            self.end_shift(False)

    def build_menu_buttons(self, mouse) -> tuple[list[Button], Button]:
        """Boutons principaux + Quitter séparé (bas, style danger) pour éviter les clics par erreur."""
        btns = []
        y0 = 360
        for i, label in enumerate(["Nouvelle Garde", "Réglages"]):
            r = pygame.Rect(W // 2 - 140, y0 + i * 62, 280, 48)
            b = Button(r, label, self.ui.fonts["medium"], COLORS["blue_d"], COLORS["white"])
            b.update_hover(mouse)
            btns.append(b)
        quit_r = pygame.Rect(W // 2 - 140, y0 + 2 * 62 + 28, 280, 44)
        quit_b = Button(quit_r, "Quitter le jeu", self.ui.fonts["medium"], COLORS["red_d"], COLORS["white"])
        quit_b.update_hover(mouse)
        return btns, quit_b

    def handle_menu(self, events, mouse):
        self.t_menu += 1 / FPS
        self._menu_buttons, self._menu_quit_btn = self.build_menu_buttons(mouse)

        if self.menu_quit_confirm:
            yes = Button(
                pygame.Rect(W // 2 - 150, H // 2 + 30, 130, 44),
                "Oui, quitter",
                self.ui.fonts["medium"],
                COLORS["red_d"],
                COLORS["white"],
            )
            no = Button(
                pygame.Rect(W // 2 + 20, H // 2 + 30, 130, 44),
                "Annuler",
                self.ui.fonts["medium"],
                COLORS["blue_d"],
                COLORS["white"],
            )
            yes.update_hover(mouse)
            no.update_hover(mouse)
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if yes.is_clicked(e):
                        pygame.quit()
                        sys.exit()
                    if no.is_clicked(e):
                        self.menu_quit_confirm = False
            self.ui.draw_menu(self.t_menu)
            for b in self._menu_buttons:
                b.draw(self.screen)
            self._menu_quit_btn.draw(self.screen)
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 200))
            self.screen.blit(ov, (0, 0))
            t = self.ui.fonts["big"].render("Quitter Night Shift ?", True, COLORS["white"])
            self.screen.blit(t, t.get_rect(center=(W // 2, H // 2 - 20)))
            yes.draw(self.screen)
            no.draw(self.screen)
            return

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self._menu_buttons[0].is_clicked(e):
                    self.start_new_shift()
                elif self._menu_buttons[1].is_clicked(e):
                    self.settings_return_state = "menu"
                    self.state = "settings"
                elif self._menu_quit_btn.is_clicked(e):
                    self.menu_quit_confirm = True
        self.ui.draw_menu(self.t_menu)
        for b in self._menu_buttons:
            b.draw(self.screen)
        self._menu_quit_btn.draw(self.screen)

    def build_settings_ui(self, mouse) -> dict:
        """Retourne dict de boutons clés pour clic."""
        out: dict[str, Button] = {}
        x0, y0 = 40, 100
        # toggles rows
        def row(y, label, on_txt):
            t = self.ui.fonts["body"].render(label, True, COLORS["white"])
            self.screen.blit(t, (x0, y))
            r = pygame.Rect(400, y - 4, 120, 28)
            b = Button(r, on_txt, self.ui.fonts["small"], COLORS["blue_d"], COLORS["white"], 4)
            b.update_hover(mouse)
            return b

        mus = "ON" if self.set_music_on else "OFF"
        out["music"] = row(y0, "Musique", mus)
        sfx = "ON" if self.set_sfx_on else "OFF"
        out["sfx"] = row(y0 + 40, "Effets sonores", sfx)
        anim = "ON" if self.animations_on else "OFF"
        out["anim"] = row(y0 + 320, "Animations", anim)

        # sliders (simplifiés: - + boutons)
        def slider_row(y, label, val, key):
            self.ui.fonts["body"].render(label, True, COLORS["white"])
            t = self.ui.fonts["body"].render(f"{label}: {val}%", True, COLORS["white"])
            self.screen.blit(t, (x0, y))
            bm = Button(pygame.Rect(400, y - 4, 40, 26), "−", self.ui.fonts["small"], COLORS["bg2"], COLORS["white"], 4)
            bp = Button(pygame.Rect(450, y - 4, 40, 26), "+", self.ui.fonts["small"], COLORS["bg2"], COLORS["white"], 4)
            bm.update_hover(mouse)
            bp.update_hover(mouse)
            bm.draw(self.screen)
            bp.draw(self.screen)
            out[key + "_m"] = bm
            out[key + "_p"] = bp

        slider_row(y0 + 90, "Volume musique", self.music_vol_pct, "mv")
        slider_row(y0 + 130, "Volume effets", self.sfx_vol_pct, "sv")

        # durée
        t = self.ui.fonts["body"].render(f"Durée de garde: {self.shift_minutes} min", True, COLORS["white"])
        self.screen.blit(t, (x0, y0 + 180))
        dm = Button(pygame.Rect(400, y0 + 176, 40, 26), "−", self.ui.fonts["small"], COLORS["bg2"], COLORS["white"], 4)
        dp = Button(pygame.Rect(450, y0 + 176, 40, 26), "+", self.ui.fonts["small"], COLORS["bg2"], COLORS["white"], 4)
        dm.update_hover(mouse)
        dp.update_hover(mouse)
        dm.draw(self.screen)
        dp.draw(self.screen)
        out["dm"] = dm
        out["dp"] = dp

        # difficulté
        self.ui.fonts["title"].render("Difficulté", True, COLORS["white"])
        td = self.ui.fonts["body"].render("Difficulté", True, COLORS["grey"])
        self.screen.blit(td, (x0, y0 + 230))
        diffs = [("Facile", "easy"), ("Normal", "normal"), ("Difficile", "hard")]
        for i, (lab, key) in enumerate(diffs):
            r = pygame.Rect(400 + i * 130, y0 + 226, 118, 30)
            bg = COLORS["teal"] if self.difficulty_key == key else COLORS["blue_d"]
            b = Button(r, lab, self.ui.fonts["small"], bg, COLORS["white"], 4)
            b.update_hover(mouse)
            b.draw(self.screen)
            out["diff_" + key] = b

        back = Button(pygame.Rect(80, H - 90, 160, 40), "Retour", self.ui.fonts["medium"], COLORS["grey_d"], COLORS["white"])
        play = Button(pygame.Rect(W - 240, H - 90, 160, 40), "Jouer", self.ui.fonts["medium"], COLORS["green_d"], COLORS["white"])
        back.update_hover(mouse)
        play.update_hover(mouse)
        back.draw(self.screen)
        play.draw(self.screen)
        out["back"] = back
        out["play"] = play
        return out

    def handle_settings(self, events, mouse):
        self.screen.fill(COLORS["bg"])
        title = self.ui.fonts["big"].render("RÉGLAGES", True, COLORS["blue"])
        self.screen.blit(title, (40, 40))
        btns = self.build_settings_ui(mouse)
        for e in events:
            if e.type != pygame.MOUSEBUTTONDOWN or e.button != 1:
                continue
            if btns["music"].is_clicked(e):
                self.set_music_on = not self.set_music_on
            elif btns["sfx"].is_clicked(e):
                self.set_sfx_on = not self.set_sfx_on
            elif btns["anim"].is_clicked(e):
                self.animations_on = not self.animations_on
            elif btns["mv_m"].is_clicked(e):
                self.music_vol_pct = max(0, self.music_vol_pct - 5)
            elif btns["mv_p"].is_clicked(e):
                self.music_vol_pct = min(100, self.music_vol_pct + 5)
            elif btns["sv_m"].is_clicked(e):
                self.sfx_vol_pct = max(0, self.sfx_vol_pct - 5)
            elif btns["sv_p"].is_clicked(e):
                self.sfx_vol_pct = min(100, self.sfx_vol_pct + 5)
            elif btns["dm"].is_clicked(e):
                self.shift_minutes = max(5, self.shift_minutes - 1)
            elif btns["dp"].is_clicked(e):
                self.shift_minutes = min(20, self.shift_minutes + 1)
            elif btns.get("diff_easy") and btns["diff_easy"].is_clicked(e):
                self.difficulty_key = "easy"
            elif btns.get("diff_normal") and btns["diff_normal"].is_clicked(e):
                self.difficulty_key = "normal"
            elif btns.get("diff_hard") and btns["diff_hard"].is_clicked(e):
                self.difficulty_key = "hard"
            elif btns["back"].is_clicked(e):
                if self.settings_return_state == "game":
                    self.state = "game"
                    self.sync_tick_clock()
                    self.apply_audio_settings()
                    if self.set_music_on:
                        if self.audio.music_sound and self.audio.music_sound.get_num_channels() == 0:
                            self.audio.play_music()
                        elif self.audio.music_sound:
                            self.audio.music_sound.set_volume(self.audio.music_vol * 0.5)
                else:
                    self.state = "menu"
            elif btns["play"].is_clicked(e):
                self.apply_audio_settings()
                self.start_new_shift()

    def draw_game(self, mouse):
        self.t_game += 1 / FPS
        self.screen.fill(COLORS["bg"])
        self.ui.draw_hud(
            self.screen,
            self.time_left,
            self.economy.budget,
            self.economy.reputation,
            self.economy.survival_rate(),
            self.economy.level,
            self.economy.fatigue,
            self.economy.consecutive_errors,
        )
        room = pygame.Rect(0, HUD_H, ROOM_W, ROOM_H)
        self.ui.draw_room_background(self.screen, room, self.animations_on, self.t_game)
        for i, (bx, by) in enumerate(BED_POSITIONS):
            pat = next((p for p in self.patients.patients if p.bed_index == i), None)
            sel = pat is not None and pat is self.sel
            self.ui.draw_bed(self.screen, bx, by, pat, sel, self.t_game, self.animations_on)

        panel = pygame.Rect(ROOM_W, HUD_H, PANEL_W, ROOM_H)
        pygame.draw.rect(self.screen, COLORS["panel"], panel)
        pygame.draw.line(self.screen, COLORS["border"], (panel.left, panel.top), (panel.left, panel.bottom), 2)
        self.draw_right_panel(panel, mouse)

        # HUD boutons pause + réglages + gestion
        pause_b = Button(pygame.Rect(W - 280, 6, 100, 36), "Pause", self.ui.fonts["small"], COLORS["blue_d"], COLORS["white"])
        set_b = Button(pygame.Rect(W - 170, 6, 150, 36), "Réglages", self.ui.fonts["small"], COLORS["grey_d"], COLORS["white"])
        man_b = Button(pygame.Rect(W - 430, 6, 140, 36), "Gestion", self.ui.fonts["small"], COLORS["teal"], COLORS["black"])
        for b in (pause_b, set_b, man_b):
            b.update_hover(mouse)
            b.draw(self.screen)
        self._hud_game_buttons = (pause_b, set_b, man_b)

        if self.notif[0]:
            self.ui.draw_notification(self.notif[0], self.notif[1])

    def _draw_panel_log_scrolled(self, px: int, y_rel: int, w: int, sy) -> int:
        y = y_rel
        self.screen.blit(self.ui.fonts["title"].render("Journal", True, COLORS["blue"]), (px, sy(y)))
        y += 22
        colors = {"green": COLORS["green"], "red": COLORS["red"], "cyan": COLORS["blue"], "yellow": COLORS["yellow"]}
        for kind, line in self.game_log[-8:]:
            c = colors.get(kind, COLORS["white"])
            for ln in self.ui.wrap_text(line, self.ui.fonts["tiny"], w):
                self.screen.blit(self.ui.fonts["tiny"].render(ln, True, c), (px, sy(y)))
                y += 14
        return y

    def apply_panel_mousewheel(self, events) -> None:
        if self.state != "game" or self.show_management:
            return
        panel_rect = pygame.Rect(ROOM_W, HUD_H, PANEL_W, ROOM_H)
        pos = pygame.mouse.get_pos()
        if not panel_rect.collidepoint(pos):
            return
        if not (self.sel and self.sel.status == "waiting" and self.sel in self.patients.patients):
            return
        step = 52
        for e in events:
            if e.type == pygame.MOUSEWHEEL:
                self.panel_scroll_y -= e.y * step
                self.panel_scroll_y = max(0, min(self._panel_max_scroll, self.panel_scroll_y))

    def draw_right_panel(self, panel: pygame.Rect, mouse):
        self._panel_regions = []
        px = panel.x + 12
        inner_top = panel.y + 10
        inner_h = max(80, panel.h - 20)
        w = panel.w - 24
        py = inner_top

        if self.sel is None or self.sel not in self.patients.patients:
            self.panel_scroll_y = 0
            self._panel_scroll_patient_id = None
            self._panel_max_scroll = 0
            msg = self.ui.fonts["body"].render("Cliquez sur un patient dans la salle", True, COLORS["grey"])
            self.screen.blit(msg, (px, py))
            self.draw_log(px, py + 40, w)
            return
        p = self.sel
        if p.status != "waiting":
            self.panel_scroll_y = 0
            self._panel_scroll_patient_id = None
            self._panel_max_scroll = 0
            t = self.ui.fonts["body"].render("Patient termine - selectionnez un autre lit.", True, COLORS["grey"])
            self.screen.blit(t, (px, py))
            self.draw_log(px, py + 40, w)
            return

        if p.id != self._panel_scroll_patient_id:
            self.panel_scroll_y = 0
            self._panel_scroll_patient_id = p.id
            self._panel_max_scroll = 0

        self.panel_scroll_y = max(0, min(self._panel_max_scroll, self.panel_scroll_y))
        scroll = self.panel_scroll_y

        def sy(yrel: int) -> int:
            return inner_top + yrel - scroll

        clip_r = pygame.Rect(panel.x + 1, inner_top, panel.w - 2, inner_h)
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(clip_r)

        y = 0
        self.screen.blit(self.ui.fonts["title"].render("Identite", True, COLORS["blue"]), (px, sy(y)))
        y += 26
        lines = [
            f"{p.name}, {p.age} ans",
            f"Gravite: {SEVERITY_LABELS.get(p.severity, p.severity)}",
            f"Attente: {p.wait_seconds}s",
        ]
        for line in lines:
            self.screen.blit(self.ui.fonts["body"].render(line, True, COLORS["white"]), (px, sy(y)))
            y += 20
        y += 6
        self.screen.blit(self.ui.fonts["title"].render("Symptomes", True, COLORS["blue"]), (px, sy(y)))
        y += 24
        tx = px
        for sym in p.symptoms:
            surf = self.ui.fonts["small"].render(sym, True, COLORS["white"])
            rw = surf.get_width() + 10
            if tx + rw > panel.right - 12:
                tx = px
                y += 26
            tag_top = sy(y)
            tag = pygame.Rect(tx, tag_top, rw, 22)
            pygame.draw.rect(self.screen, COLORS["blue_d"], tag, border_radius=4)
            self.screen.blit(surf, (tx + 5, tag_top + 3))
            tx += rw + 6
        y += 32

        self.screen.blit(self.ui.fonts["title"].render("Examens", True, COLORS["blue"]), (px, sy(y)))
        y += 22
        exam_keys = list(EXAMS.keys())
        cols = 2
        cell_h = 36
        for i, ek in enumerate(exam_keys):
            row, col = divmod(i, cols)
            bx = px + col * ((w // 2) + 6)
            by_rel = y + row * (cell_h + 6)
            by_screen = sy(by_rel)
            ex = EXAMS[ek]
            done = ek in p.exams_done
            affordable = self.economy.budget >= ex["cost"]
            label = f"{ex['label'][:18]}.. {ex['cost']} EUR" if len(ex["label"]) > 18 else f"{ex['label']} {ex['cost']} EUR"
            if done:
                label = "OK Fait"
            bg = COLORS["green_d"] if done else COLORS["blue_d"]
            br = pygame.Rect(bx, by_screen, w // 2 - 8, cell_h)
            b = Button(br, label, self.ui.fonts["tiny"], bg, COLORS["white"], 4)
            b.disabled = done or (not affordable and not done)
            b.update_hover(mouse)
            b.draw(self.screen)
            setattr(self, f"_exam_btn_{ek}", b)
            self._panel_regions.append(("exam", br, ek))
        y += ((len(exam_keys) + 1) // 2) * (cell_h + 6) + 10

        self.screen.blit(self.ui.fonts["title"].render("Resultats", True, COLORS["blue"]), (px, sy(y)))
        y += 22
        for ek in p.exams_done:
            lab = EXAMS[ek]["label"]
            res = p.exam_results.get(ek, "")
            self.screen.blit(self.ui.fonts["small"].render(lab + ":", True, COLORS["teal"]), (px, sy(y)))
            y += 16
            for line in self.ui.wrap_text(res, self.ui.fonts["small"], w - 8):
                self.screen.blit(self.ui.fonts["small"].render(line, True, COLORS["white"]), (px + 6, sy(y)))
                y += 14
            y += 4

        self.screen.blit(self.ui.fonts["title"].render("Diagnostic", True, COLORS["blue"]), (px, sy(y)))
        y += 24
        acc = DiagnosticEngine.compute_accuracy(
            self.economy.level, self.economy.equipment_count(), self.economy.fatigue
        )
        self.screen.blit(
            self.ui.fonts["small"].render(f"Precision estimee: {acc*100:.1f}%", True, COLORS["yellow"]),
            (px, sy(y)),
        )
        y += 22
        dg_y = y
        for i, dname in enumerate(p.diag_options):
            row, col = divmod(i, 2)
            bx = px + col * (w // 2 + 4)
            by_rel = dg_y + row * 40
            by_screen = sy(by_rel)
            hl = p.selected_diag == dname
            bg = COLORS["yellow"] if hl else COLORS["bg2"]
            br = pygame.Rect(bx, by_screen, w // 2 - 8, 34)
            b = Button(br, dname[:22], self.ui.fonts["tiny"], bg, COLORS["black"] if hl else COLORS["white"], 4)
            b.update_hover(mouse)
            b.draw(self.screen)
            setattr(self, f"_diag_btn_{i}", b)
            self._panel_regions.append(("diag", br, i))
        y = dg_y + 90

        ty = sy(y)
        treat = Button(pygame.Rect(px, ty, w // 2 - 6, 40), "TRAITER", self.ui.fonts["medium"], COLORS["green_d"], COLORS["white"])
        deleg = Button(
            pygame.Rect(px + w // 2 + 4, ty, w // 2 - 6, 40),
            "DELEGUER",
            self.ui.fonts["medium"],
            COLORS["yellow"],
            COLORS["black"],
        )
        treat.disabled = p.selected_diag is None
        deleg.disabled = p.selected_diag is None
        for b in (treat, deleg):
            b.update_hover(mouse)
            b.draw(self.screen)
        self._treat_btn = treat
        self._deleg_btn = deleg
        self._panel_regions.append(("treat", pygame.Rect(px, ty, w // 2 - 6, 40)))
        self._panel_regions.append(("deleg", pygame.Rect(px + w // 2 + 4, ty, w // 2 - 6, 40)))
        y += 50
        y = self._draw_panel_log_scrolled(px, y, w, sy)

        total_h = y
        self._panel_max_scroll = max(0, total_h - inner_h)
        self.panel_scroll_y = max(0, min(self._panel_max_scroll, self.panel_scroll_y))

        self.screen.set_clip(prev_clip)

        if self._panel_max_scroll > 0:
            sb_x = panel.right - 10
            pygame.draw.line(self.screen, COLORS["border"], (sb_x, inner_top), (sb_x, inner_top + inner_h), 2)
            thumb_h = max(28, int(inner_h * inner_h / (total_h + 1)))
            ty0 = inner_top + int((inner_h - thumb_h) * self.panel_scroll_y / self._panel_max_scroll)
            tr = pygame.Rect(sb_x - 3, ty0, 6, thumb_h)
            pygame.draw.rect(self.screen, COLORS["blue_d"], tr, border_radius=3)
            hint = self.ui.fonts["tiny"].render("Molette", True, COLORS["grey"])
            self.screen.blit(hint, (panel.x + 8, inner_top + inner_h - 16))

    def draw_log(self, px, y, w):
        self.screen.blit(self.ui.fonts["title"].render("Journal", True, COLORS["blue"]), (px, y))
        y += 22
        colors = {"green": COLORS["green"], "red": COLORS["red"], "cyan": COLORS["blue"], "yellow": COLORS["yellow"]}
        for kind, line in self.game_log[-8:]:
            c = colors.get(kind, COLORS["white"])
            for ln in self.ui.wrap_text(line, self.ui.fonts["tiny"], w):
                self.screen.blit(self.ui.fonts["tiny"].render(ln, True, c), (px, y))
                y += 14

    def handle_game_click(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        pos = pygame.mouse.get_pos()
        panel_rect = pygame.Rect(ROOM_W, HUD_H, PANEL_W, ROOM_H)
        if hasattr(self, "_hud_game_buttons"):
            pause_b, set_b, man_b = self._hud_game_buttons
            if pause_b.rect.collidepoint(pos) and not pause_b.disabled:
                self.state = "pause"
                if self.audio.music_sound:
                    try:
                        self.audio.music_sound.set_volume(0)
                    except Exception:
                        pass
                return
            if set_b.rect.collidepoint(pos) and not set_b.disabled:
                self.settings_return_state = "game"
                self.state = "settings"
                self.audio.stop_music()
                return
            if man_b.rect.collidepoint(pos) and not man_b.disabled:
                self.show_management = True
                if self.audio.music_sound:
                    try:
                        self.audio.music_sound.set_volume(0)
                    except Exception:
                        pass
                return
        if pos[1] >= H - NOTIF_H:
            return
        if panel_rect.collidepoint(pos):
            if self.sel and self.sel.status == "waiting" and self.sel in self.patients.patients:
                p = self.sel
                for item in reversed(self._panel_regions):
                    kind = item[0]
                    rect = item[1]
                    if not rect.collidepoint(pos):
                        continue
                    if kind == "exam":
                        ek = item[2]
                        if ek in p.exams_done:
                            self.notif = ("Cet examen a deja ete realise.", COLORS["yellow"])
                            self.audio.play_info()
                            return
                        if self.economy.budget < EXAMS[ek]["cost"]:
                            self.notif = (f"Budget insuffisant ({EXAMS[ek]['cost']} EUR requis).", COLORS["red"])
                            self.audio.play_info()
                            return
                        if self.patients.do_exam(p, ek, self.game_log):
                            self.notif = (f"Examen realise : {EXAMS[ek]['label']}", COLORS["cyan"])
                        return
                    if kind == "diag":
                        i = item[2]
                        p.selected_diag = p.diag_options[i]
                        self.notif = (f"Diagnostic selectionne : {p.selected_diag}", COLORS["yellow"])
                        self.audio.play_info()
                        return
                    if kind == "treat":
                        if p.selected_diag is None:
                            self.notif = ("Choisissez un diagnostic avant de traiter.", COLORS["red"])
                            return
                        self.patients.treat_patient(p, self.game_log)
                        self.sel = None
                        return
                    if kind == "deleg":
                        if p.selected_diag is None:
                            self.notif = ("Choisissez un diagnostic avant de deleguer.", COLORS["red"])
                            return
                        self.patients.delegate_patient(p, self.game_log)
                        self.sel = None
                        return
            return
        if pos[0] < ROOM_W and HUD_H <= pos[1] < HUD_H + ROOM_H:
            hit = self.patients.get_patient_at_bed_click(pos)
            if hit:
                self.sel = hit
                self.audio.play_info()
            return

    def draw_pause_overlay(self):
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        self.screen.blit(ov, (0, 0))
        t = self.ui.fonts["big"].render("PAUSE — Cliquez pour reprendre", True, COLORS["white"])
        r = t.get_rect(center=(W // 2, H // 2))
        self.screen.blit(t, r)

    def draw_management(self, mouse):
        self.draw_game(mouse)
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        box = pygame.Rect(140, 80, W - 280, H - 160)
        pygame.draw.rect(self.screen, COLORS["panel"], box, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["border"], box, 2, border_radius=12)
        t = self.ui.fonts["big"].render("GESTION — Équipements", True, COLORS["blue"])
        self.screen.blit(t, (box.x + 20, box.y + 16))
        y = box.y + 70
        for eq in EQUIPMENT_DEFS:
            owned = eq["id"] in self.economy.equipment_owned
            line = f"{eq['name']} - {eq['cost']} EUR  ({eq['desc']})"
            col = COLORS["green"] if owned else COLORS["white"]
            self.screen.blit(self.ui.fonts["body"].render(line, True, col), (box.x + 24, y))
            buy = Button(
                pygame.Rect(box.right - 140, y - 4, 110, 30),
                "Acheté" if owned else "Acheter",
                self.ui.fonts["small"],
                COLORS["grey_d"] if owned else COLORS["teal"],
                COLORS["white"] if not owned else COLORS["grey"],
                4,
            )
            buy.disabled = owned or self.economy.budget < eq["cost"]
            buy.update_hover(mouse)
            buy.draw(self.screen)
            setattr(self, f"_buy_{eq['id']}", buy)
            y += 44
        st = (
            f"Budget: {self.economy.budget} EUR   Reputation: {self.economy.reputation}   "
            f"Traités: {self.economy.patients_treated}   Décès: {self.economy.patients_dead}"
        )
        self.screen.blit(self.ui.fonts["body"].render(st, True, COLORS["grey"]), (box.x + 24, y + 10))
        back = Button(pygame.Rect(box.centerx - 80, box.bottom - 56, 200, 40), "Retour au jeu", self.ui.fonts["medium"], COLORS["blue_d"], COLORS["white"])
        back.update_hover(mouse)
        back.draw(self.screen)
        self._man_back = back

    def handle_management(self, events, mouse):
        self.draw_management(mouse)
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self._man_back.is_clicked(e):
                    self.show_management = False
                    self.sync_tick_clock()
                    self.apply_audio_settings()
                    if self.set_music_on and self.audio.music_sound:
                        self.audio.music_sound.set_volume(self.audio.music_vol * 0.5)
                        if self.audio.music_sound.get_num_channels() == 0:
                            self.audio.play_music()
                for eq in EQUIPMENT_DEFS:
                    b = getattr(self, f"_buy_{eq['id']}", None)
                    if b and b.is_clicked(e):
                        if self.economy.buy_equipment(eq["id"], eq["cost"]):
                            self.log_add("cyan", f"Achat: {eq['name']}")
                            self.audio.play_alert()

    def draw_end(self, mouse):
        self.screen.fill(COLORS["bg"])
        e = self.economy
        surv = e.survival_rate()
        title = "GARDE RÉUSSIE !" if self.end_won else "GARDE TERMINÉE"
        col = COLORS["green"] if self.end_won else COLORS["red"]
        t = self.ui.fonts["huge"].render(title, True, col)
        self.screen.blit(t, t.get_rect(center=(W // 2, 100)))
        if self.end_reason:
            rr = self.ui.fonts["body"].render(self.end_reason, True, COLORS["yellow"])
            self.screen.blit(rr, rr.get_rect(center=(W // 2, 170)))
        # cartes stats
        cards = [
            ("Patients traités", str(e.patients_treated)),
            ("Taux de survie", f"{surv:.1f} %"),
            ("Erreurs", str(e.total_errors)),
            ("Budget final", f"{e.budget} EUR"),
        ]
        x0 = 80
        for i, (lab, val) in enumerate(cards):
            r = pygame.Rect(x0 + i * 290, 240, 260, 100)
            pygame.draw.rect(self.screen, COLORS["panel"], r, border_radius=10)
            pygame.draw.rect(self.screen, COLORS["border"], r, 1, border_radius=10)
            self.screen.blit(self.ui.fonts["small"].render(lab, True, COLORS["grey"]), (r.x + 14, r.y + 12))
            self.screen.blit(self.ui.fonts["big"].render(val, True, COLORS["white"]), (r.x + 14, r.y + 40))
        score = int((e.reputation * 0.4 * 10) + (max(0, e.budget) * 0.01) + (surv * 0.3 * 30))
        sc = self.ui.fonts["big"].render(f"Score final: {score}", True, COLORS["yellow"])
        self.screen.blit(sc, sc.get_rect(center=(W // 2, 400)))
        replay = Button(pygame.Rect(W // 2 - 200, 480, 180, 48), "Rejouer", self.ui.fonts["medium"], COLORS["green_d"], COLORS["white"])
        menu = Button(pygame.Rect(W // 2 + 20, 480, 180, 48), "Menu principal", self.ui.fonts["medium"], COLORS["blue_d"], COLORS["white"])
        for b in (replay, menu):
            b.update_hover(mouse)
            b.draw(self.screen)
        self._end_replay = replay
        self._end_menu = menu

    def handle_end(self, events, mouse):
        self.draw_end(mouse)
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self._end_replay.is_clicked(e):
                    self.start_new_shift()
                elif self._end_menu.is_clicked(e):
                    self.state = "menu"
                    self.audio.stop_music()

    def run(self):
        running = True
        while running:
            try:
                try:
                    mouse = pygame.mouse.get_pos()
                except Exception:
                    mouse = (0, 0)
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        if self.state == "game" and not self.show_management:
                            self.state = "pause"
                            if self.audio.music_sound:
                                try:
                                    self.audio.music_sound.set_volume(0)
                                except Exception:
                                    pass
                        elif self.state == "pause":
                            self.state = "game"
                            self.sync_tick_clock()
                            self.apply_audio_settings()
                            if self.set_music_on and self.audio.music_sound:
                                try:
                                    self.audio.music_sound.set_volume(self.audio.music_vol * 0.5)
                                    if self.audio.music_sound.get_num_channels() == 0:
                                        self.audio.play_music()
                                except Exception:
                                    pass
                        elif self.state == "settings":
                            if self.settings_return_state == "game":
                                self.state = "game"
                                self.sync_tick_clock()
                                self.apply_audio_settings()
                                if self.set_music_on:
                                    try:
                                        if self.audio.music_sound and self.audio.music_sound.get_num_channels() == 0:
                                            self.audio.play_music()
                                        elif self.audio.music_sound:
                                            self.audio.music_sound.set_volume(self.audio.music_vol * 0.5)
                                    except Exception:
                                        pass
                            else:
                                self.state = "menu"

                if self.state == "game" and not self.show_management:
                    self.apply_panel_mousewheel(events)

                now = time.time()
                if self.state == "game" and not self.show_management:
                    if now - self.last_tick >= 1.0:
                        self.last_tick = now
                        self.game_tick()

                if self.state == "menu":
                    self.handle_menu(events, mouse)
                elif self.state == "settings":
                    self.handle_settings(events, mouse)
                elif self.state == "game":
                    if self.show_management:
                        self.handle_management(events, mouse)
                    else:
                        self.draw_game(mouse)
                        for e in events:
                            self.handle_game_click(e)
                elif self.state == "pause":
                    self.draw_game(mouse)
                    self.draw_pause_overlay()
                    for e in events:
                        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                            self.state = "game"
                            self.sync_tick_clock()
                            self.apply_audio_settings()
                            if self.set_music_on and self.audio.music_sound:
                                try:
                                    self.audio.music_sound.set_volume(self.audio.music_vol * 0.5)
                                    if self.audio.music_sound.get_num_channels() == 0:
                                        self.audio.play_music()
                                except Exception:
                                    pass
                        elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                            self.state = "game"
                            self.sync_tick_clock()
                            self.apply_audio_settings()
                            if self.set_music_on and self.audio.music_sound:
                                try:
                                    self.audio.music_sound.set_volume(self.audio.music_vol * 0.5)
                                    if self.audio.music_sound.get_num_channels() == 0:
                                        self.audio.play_music()
                                except Exception:
                                    pass
                elif self.state == "end":
                    self.handle_end(events, mouse)

                pygame.display.flip()
            except Exception:
                _log_crash()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    GameManager().run()
