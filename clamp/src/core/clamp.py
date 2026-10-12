# ./src/core/clamp.py
"""
Clamp task (task phase of the experiment).

Implements Clamp_Task_Procedure.pdf. On each trial the participant moves a (hidden) mouse
cursor from the central start circle through a blue target. In clamp trials the visible cursor
is not controlled by the hand: its angle is fixed relative to the target (target angle +
rotation) while its distance follows the hand. The main measure is the hand angle when the
hand crosses the target ring.

Trial structure, target angles, rotations and feedback conditions come from the trial files in
resources/trial_files (51 versions, v0..v50). The version of a participant is the last run of
digits in the PID modulo 51 (random if the PID has no digits).

Flow (run_clamp_task):
    initial screen -> 284 trials (with break messages) -> key-press attention checks after
    randomly chosen trials -> understanding check after the clamp demonstration (replays the
    task instructions and the four demonstration trials until answered correctly).

All timing uses time.perf_counter(); the display loop is frame-based (vsync).
"""


from __future__ import annotations

import csv
import datetime
import math
import random
import re
import string
import time
import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pygame

import utils.config as cfg
from utils.event_handler import ControlState, EventHandler
from utils.logger import get_logger
from utils.paths import N_TRIAL_FILES, trial_file_path
from utils.saves import finalize_save, update_save_clamp
from ui.pygame_render import toggle_full_screen


logger = get_logger("./src/core/clamp")


# ---------- Messages (Clamp_Task_Procedure.pdf, Table 4 and Section 6) ----------

INITIAL_MESSAGE = [
    "Move the white dot to the center.",
    "The white dot will disappear during your reach.",
    "Quickly move to the blue target.",
    "Press SPACE BAR when you are ready to proceed.",
]

AFTER_TRIAL_40_MESSAGE = [
    "The white dot will now be present, but will NOT be under your control.",
    "IGNORE the white dot as best as you can and continue aiming DIRECTLY towards the blue target.",
    "This will be a practice trial",
    "Press SPACE BAR when you are ready to proceed.",
]

AFTER_TRIAL_44_MESSAGE = [
    "Again, the white dot will NOT be under your control.",
    "IGNORE the white dot as best as you can and continue aiming DIRECTLY towards the blue target.",
    "Press SPACE BAR when you are ready to proceed.",
]

AFTER_TRIAL_244_MESSAGE = [
    "The white dot will now be hidden.",
    "Continue aiming DIRECTLY towards the blue target.",
    "Press SPACE BAR when you are ready to proceed.",
]

# `between_blocks` code in the trial files -> message shown after that trial
BREAK_MESSAGES = {
    6: AFTER_TRIAL_40_MESSAGE,     # after trial 40
    8: AFTER_TRIAL_44_MESSAGE,     # after trial 44
    3: AFTER_TRIAL_244_MESSAGE,    # after trial 244
}

UNDERSTANDING_QUESTION = [
    "This is an instruction understanding check.",
    "Press 'a' if you should ignore the white dot and aim directly towards the target.",
    "Press 'b' if you should be aiming away from the target.",
]
UNDERSTANDING_CORRECT_KEY = "a"

MOVE_FASTER_TEXT = "Move Faster"
SEARCH_HINT_TEXT = "To find your cursor, try moving your mouse to the center of the screen."
ATTENTION_ERROR_TEXT = "Pay attention!"


# ---------- Trial files ----------

@dataclass(frozen=True)
class Trial:
    """One row of a trial file."""
    num: int            # trial number (1..284)
    tgt_angle: float    # target angle (deg, counter-clockwise from +x)
    rotation: float     # clamp rotation (deg)
    clamped_fb: bool    # True = clamp feedback, False = no feedback
    between_blocks: int # break-message code shown after this trial (0 = none)
    feedback_ms: int    # endpoint feedback duration (ms)


def select_trial_version(pid: str | None) -> int:
    """
    Choose the trial file version for a participant.

    The last run of digits in the PID, modulo the number of trial files (51). A PID without
    digits gets a random version.

    :param pid: Participant ID
    :type pid: str | None

    :return: Trial file version (0 .. N_TRIAL_FILES - 1)
    :rtype: int
    """
    runs = re.findall(r"\d+", pid or "")
    if runs:
        return int(runs[-1]) % N_TRIAL_FILES
    return random.randrange(N_TRIAL_FILES)


def load_trial_file(path: Path) -> list[Trial]:
    """
    Read a trial file (resources/trial_files/clamp_30cw_v*.csv).

    :param path: Path to the trial file
    :type path: pathlib.Path

    :return: The trials in presentation order
    :rtype: list[Trial]
    """
    if not path.exists():
        raise FileNotFoundError(f"Trial file not found: {path}")

    trials: list[Trial] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            trials.append(
                Trial(
                    num=int(row["trialnum"]),
                    tgt_angle=float(row["tgt_angle"]),
                    rotation=float(row["rotation"]),
                    clamped_fb=int(float(row["clamped_fb"])) == 1,
                    between_blocks=int(float(row["between_blocks"])),
                    feedback_ms=int(float(row["delayed_duration"])),
                )
            )

    if len(trials) != cfg.CLAMP_FILE_N_TRIALS or [t.num for t in trials] != list(range(1, cfg.CLAMP_FILE_N_TRIALS + 1)):
        raise ValueError(f"Trial file {path.name} does not contain trials 1..{cfg.CLAMP_FILE_N_TRIALS}")

    # Demo mode: keep only the picked trials (in the order given) and renumber them 1..N
    if cfg.CLAMP_DEMO_PICK is not None:
        by_num = {t.num: t for t in trials}
        trials = [dataclasses.replace(by_num[n], num=i) for i, n in enumerate(cfg.CLAMP_DEMO_PICK, start=1)]
    return trials


def block_name(trial_num: int) -> str:
    """
    Block name of a trial number (baseline / clamp_demo / clamp / post_test).

    :param trial_num: Trial number (1..284)
    :type trial_num: int

    :return: Block name
    :rtype: str
    """
    for first, last, name in cfg.CLAMP_BLOCKS:
        if first <= trial_num <= last:
            return name
    raise ValueError(f"Trial number out of range: {trial_num}")


# ---------- Geometry ----------

@dataclass(frozen=True)
class Geometry:
    """Screen layout in pixels; everything scales with the screen height H (Table 1)."""
    w: int
    h: int
    cx: float           # start position (screen center)
    cy: float
    d: float            # target distance D
    radius: float       # start circle / target / cursor radius
    vis_radius: float   # cursor is drawn during search only within this distance
    search_tol: float   # hand distance at which the hold phase can begin
    font_px: int        # font size = line height


def build_geometry(w: int, h: int) -> Geometry:
    """
    Compute the layout for a screen of w x h pixels.

    :param w: Screen width (px)
    :param h: Screen height H (px)

    :return: Geometry
    :rtype: Geometry
    """
    d = cfg.CLAMP_TARGET_DIST_FRAC * h
    radius = d * cfg.CLAMP_RADIUS_RATIO     # start, target and cursor share this radius
    return Geometry(
        w=w,
        h=h,
        cx=w / 2,
        cy=h / 2,
        d=d,
        radius=radius,
        vis_radius=cfg.CLAMP_VIS_RADIUS_FRAC * d,
        search_tol=4 * radius + 4 * radius,     # 4 x start radius + 4 x cursor radius
        font_px=round(h / 30),
    )


def polar_to_xy(geo: Geometry, dist: float, angle_deg: float) -> tuple[float, float]:
    """
    Screen position at distance `dist` and angle `angle_deg` from the start position.

    Angles are counter-clockwise from +x; screen y increases downward.
    """
    a = math.radians(angle_deg)
    return geo.cx + dist * math.cos(a), geo.cy - dist * math.sin(a)


def _now_ms() -> float:
    """Monotonic time in milliseconds."""
    return time.perf_counter() * 1000.0


# ---------- Trial state ----------

@dataclass
class _TrialState:
    """Mutable state of the trial in progress."""
    phase: str                      # search / hold / target / reach / feedback
    hx: float                       # virtual hand position (px)
    hy: float
    t_trial_search: float           # start of the trial's search phase (for search_time)
    t_search_visit: float           # start of the current visit to the search phase (for the hint)
    hold_start: float | None = None
    target_onset: float | None = None   # set after the first frame with the target is shown
    t_leave: float | None = None        # hand left the start circle
    fb_start: float | None = None       # set after the first feedback frame is shown
    mt: float = 0.0
    hand_angle: float = 0.0
    too_slow: bool = False
    first_frame: bool = True


class ClampTask:
    """
    Runs the clamp task on an initialized pygame display.

    :param screen: Current display surface
    :param event_handler: Centralized event handler
    :param replay_instructions: Callback that shows the task instructions again and returns
        the (possibly updated) display surface; used when the understanding check fails
    """

    def __init__(
        self,
        screen: pygame.Surface,
        event_handler: EventHandler,
        replay_instructions: Callable[[pygame.Surface], pygame.Surface] | None = None,
    ) -> None:
        self.screen = screen
        self.eh = event_handler
        self.replay_instructions = replay_instructions
        self.clock = pygame.time.Clock()

        self.version = select_trial_version(cfg.PID)
        self.trial_sequence = f"v{self.version}"
        self.trials = load_trial_file(trial_file_path(self.version))
        logger.info(f"Trial file selected: {self.trial_sequence} (PID = {cfg.PID})")

        # Key-press attention checks: after random trials, without replacement
        lo, hi = cfg.KEY_CHECK_RANGE
        ex_lo, ex_hi = cfg.KEY_CHECK_EXCLUDE
        candidates = [n for n in range(lo, hi + 1) if not ex_lo <= n <= ex_hi]
        if cfg.KEY_CHECK_FIXED is not None:     # demo mode: fixed positions
            self.key_check_after = set(cfg.KEY_CHECK_FIXED)
        else:
            self.key_check_after = set(random.sample(candidates, cfg.N_KEY_CHECKS))
        logger.info(f"Key-press checks after trials: {sorted(self.key_check_after)}")

        self.key_total = 0
        self.key_correct = 0
        self.und_attempts = 0
        self.und_correct = 0

        self.capturing = False
        self.geo_version = 0    # incremented whenever the display (and geometry) is rebuilt
        self._rebuild()

    # ----- display helpers -----

    def _rebuild(self) -> None:
        """Recompute geometry and font for the current display surface."""
        w, h = self.screen.get_size()
        self.geo = build_geometry(w, h)
        self.font = pygame.font.Font(None, self.geo.font_px)
        self.geo_version += 1

    def _capture_mouse(self, on: bool) -> None:
        """Hide the system pointer and confine the mouse so relative movement is unbounded."""
        self.capturing = on
        try:
            pygame.mouse.set_visible(not on)
            pygame.event.set_grab(on)
        except pygame.error:
            pass    # display already closed (quit path)

    def _toggle_fs(self) -> None:
        """Toggle fullscreen and rebuild everything that depends on the display."""
        pygame.event.clear()
        self.screen = toggle_full_screen(self.screen)
        pygame.event.clear()
        if self.capturing:
            self._capture_mouse(True)
        self._rebuild()

    def _poll(self) -> ControlState:
        """Poll input once; handle quit and fullscreen toggle (ESC)."""
        state = self.eh.poll()
        if state.quit:
            raise SystemExit
        if state.toggle_full_screen:
            self._toggle_fs()
        return state

    def _flush(self) -> None:
        pygame.event.clear()
        pygame.time.delay(1)
        pygame.event.clear()

    def _wrap(self, text: str, max_w: float) -> list[str]:
        """Greedy word wrap of one line of text to max_w pixels."""
        lines: list[str] = []
        cur = ""
        for word in text.split(" "):
            cand = word if not cur else f"{cur} {word}"
            if cur and self.font.size(cand)[0] > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = cand
        lines.append(cur)
        return lines

    def _draw_lines(self, lines: list[str], color=cfg.PURE_WHITE_RGB) -> None:
        """
        Clear the screen and draw centered text lines. The first line is centered at
        H/2 minus one line height, each further line one line height lower.
        """
        geo = self.geo
        self.screen.fill(cfg.BLACK_RGB)
        wrapped: list[str] = []
        for line in lines:
            wrapped.extend(self._wrap(line, 0.9 * geo.w))
        y0 = geo.h / 2 - geo.font_px
        for i, line in enumerate(wrapped):
            surf = self.font.render(line, True, color)
            rect = surf.get_rect(center=(geo.cx, y0 + i * geo.font_px))
            self.screen.blit(surf, rect)

    def _draw_centered(self, text: str, y: float, color) -> None:
        surf = self.font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=(self.geo.cx, y)))

    def _render_trial_frame(
        self,
        trial: Trial,
        *,
        fill_start: bool,
        show_target: bool,
        cursor: tuple[float, float] | None,
        hint: bool = False,
        too_slow: bool = False,
    ) -> None:
        """Draw one frame of a trial (does not flip)."""
        geo = self.geo
        scr = self.screen
        scr.fill(cfg.BLACK_RGB)

        # Start circle: white outline, filled while the hand is held inside it
        if fill_start:
            pygame.draw.circle(scr, cfg.PURE_WHITE_RGB, (geo.cx, geo.cy), geo.radius)
        else:
            pygame.draw.circle(scr, cfg.PURE_WHITE_RGB, (geo.cx, geo.cy), geo.radius, cfg.CLAMP_START_STROKE)

        if show_target:
            tx, ty = polar_to_xy(geo, geo.d, trial.tgt_angle)
            pygame.draw.circle(scr, cfg.BLUE_RGB, (tx, ty), geo.radius)

        if cursor is not None:
            pygame.draw.circle(scr, cfg.PURE_WHITE_RGB, cursor, geo.radius)

        if hint:
            self._draw_centered(SEARCH_HINT_TEXT, 2 * geo.h / 3, cfg.PURE_WHITE_RGB)
        if too_slow:
            self._draw_centered(MOVE_FASTER_TEXT, 2 * geo.h / 3, cfg.RED_RGB)   # below the start circle

        # Trial counter, right-aligned at (0.95 W, 0.95 H)
        counter = self.font.render(f"Reach Number: {trial.num} / {cfg.CLAMP_N_TRIALS}", True, cfg.PURE_WHITE_RGB)
        scr.blit(counter, counter.get_rect(midright=(0.95 * geo.w, 0.95 * geo.h)))

    # ----- screens that wait for the participant -----

    def show_message(self, lines: list[str]) -> None:
        """Show a message and wait for SPACE."""
        self._flush()
        t0 = _now_ms()
        while True:
            state = self._poll()
            self._draw_lines(lines)
            pygame.display.flip()
            if state.next_page and _now_ms() - t0 >= cfg.MIN_READING_TIME:
                return
            self.clock.tick(cfg.CLAMP_MAX_FPS)

    def _understanding_question(self) -> bool:
        """Ask the understanding question once; return True if answered correctly."""
        self._flush()
        while True:
            state = self._poll()
            self._draw_lines(UNDERSTANDING_QUESTION)
            pygame.display.flip()
            for key in state.keys:
                if key in ("a", "b"):
                    return key == UNDERSTANDING_CORRECT_KEY
            self.clock.tick(cfg.CLAMP_MAX_FPS)

    def _key_check(self) -> None:
        """Key-press attention check: press the shown letter; one attempt."""
        letter = random.choice(string.ascii_uppercase)
        self._flush()
        self.key_total += 1
        correct: bool | None = None
        while correct is None:
            state = self._poll()
            self._draw_lines([f"Press the letter '{letter}' to continue."])
            pygame.display.flip()
            for key in state.keys:
                if key == "escape":     # fullscreen toggle, not a response
                    continue
                correct = key == letter.lower()
                break
            self.clock.tick(cfg.CLAMP_MAX_FPS)

        if correct:
            self.key_correct += 1
            logger.info(f"KEY_CHECK | letter={letter} | correct")
            return

        logger.info(f"KEY_CHECK | letter={letter} | error")
        t0 = _now_ms()
        while _now_ms() - t0 < cfg.ATTENTION_MESSAGE_DURATION:
            self._poll()
            self.screen.fill(cfg.BLACK_RGB)
            self._draw_centered(ATTENTION_ERROR_TEXT, self.geo.h / 2, cfg.PURE_WHITE_RGB)
            pygame.display.flip()
            self.clock.tick(cfg.CLAMP_MAX_FPS)
        self._flush()

    def _understanding_check(self) -> None:
        """
        Understanding check after the clamp demonstration. On a wrong answer the task
        instructions and the four demonstration trials are replayed, then the question is
        asked again, until it is answered correctly.
        """
        demo_first, demo_last, _ = cfg.CLAMP_BLOCKS[1]
        demo_trials = [t for t in self.trials if demo_first <= t.num <= demo_last]
        replay = 0
        while True:
            self.und_attempts += 1
            if self._understanding_question():
                self.und_correct += 1
                logger.info(f"UNDERSTANDING_CHECK | attempt={self.und_attempts} | correct")
                return

            logger.info(f"UNDERSTANDING_CHECK | attempt={self.und_attempts} | wrong -> replay {replay + 1}")
            replay += 1

            # Task instructions (shown by the experiment flow), then demonstration + its messages
            if self.replay_instructions is not None:
                self._capture_mouse(False)
                self.screen = self.replay_instructions(self.screen)
                self._rebuild()
                self._capture_mouse(True)
            self.show_message(AFTER_TRIAL_40_MESSAGE)
            for trial in demo_trials:
                self._run_trial_and_post(trial, replay)

    # ----- trial -----

    def _new_state(self) -> _TrialState:
        """Initial state of a trial; the hand starts just outside the start circle."""
        geo = self.geo
        r = geo.radius
        off_x = random.uniform(r, 2 * r) * random.choice((-1, 1))
        off_y = random.uniform(r, 2 * r) * random.choice((-1, 1))
        now = _now_ms()
        return _TrialState(
            phase="search",
            hx=geo.cx + off_x,
            hy=geo.cy + off_y,
            t_trial_search=now,
            t_search_visit=now,
        )

    def _run_trial(self, trial: Trial, replay_index: int) -> None:
        """
        Run one trial (Search -> Hold -> Target -> Reach -> Feedback) and save its data.
        Reset (blank interval, break message) is handled by _run_trial_and_post.
        """
        start_dt = datetime.datetime.now()
        s = self._new_state()
        geo_version = self.geo_version
        fb_total = trial.feedback_ms    # feedback period; becomes TOO_SLOW_FB_TIME for a too-slow reach

        while True:
            state = self._poll()

            # Display rebuilt (fullscreen toggled): geometry changed, restart this trial
            if geo_version != self.geo_version:
                logger.warning(f"Display changed during trial {trial.num}; trial restarted")
                geo_version = self.geo_version
                s = self._new_state()

            geo = self.geo
            now = _now_ms()

            # Hand = accumulated relative mouse movement, clipped to the screen
            if s.first_frame:
                s.first_frame = False       # discard movement accumulated before the trial
            else:
                s.hx = min(max(s.hx + state.mouse_dx, 0), geo.w - 1)
                s.hy = min(max(s.hy + state.mouse_dy, 0), geo.h - 1)
            r = math.hypot(s.hx - geo.cx, s.hy - geo.cy)

            # ---- phase transitions ----
            if s.phase == "search" and r <= geo.search_tol:
                s.phase = "hold"
                s.hold_start = None

            if s.phase == "hold":
                if r > geo.search_tol:
                    s.phase = "search"
                    s.t_search_visit = now
                    s.hold_start = None
                elif r <= geo.radius:
                    if s.hold_start is None:
                        s.hold_start = now
                    elif now - s.hold_start >= cfg.HOLD_TIME:
                        s.phase = "target"      # target onset is timestamped after its first flip
                else:
                    s.hold_start = None         # left the start circle: restart the hold timer

            elif s.phase == "target":
                if s.target_onset is not None and r > geo.radius:
                    s.t_leave = now
                    s.phase = "reach"

            if s.phase == "reach" and r > geo.d:
                s.mt = now - s.t_leave
                s.hand_angle = math.degrees(math.atan2(geo.cy - s.hy, s.hx - geo.cx)) % 360
                s.too_slow = s.mt > cfg.TOO_SLOW_TIME
                fb_total = cfg.TOO_SLOW_FB_TIME if s.too_slow else trial.feedback_ms
                s.phase = "feedback"

            # ---- what to draw ----
            fill_start = False
            show_target = False
            cursor: tuple[float, float] | None = None
            hint = False
            clamp_angle = trial.tgt_angle + trial.rotation

            if s.phase == "search":
                hint = now - s.t_search_visit > cfg.SEARCH_HINT_DELAY
                if r <= geo.vis_radius or hint:
                    cursor = (s.hx, s.hy)       # once the hint appears the cursor is shown everywhere
            elif s.phase == "hold":
                if r <= geo.radius:
                    fill_start = True       # hand inside: cursor hidden, circle filled
                else:
                    cursor = (s.hx, s.hy)
            elif s.phase == "target":
                fill_start = True
                show_target = True
            elif s.phase == "reach":
                show_target = True
                if trial.clamped_fb:
                    cursor = polar_to_xy(geo, r, clamp_angle)   # angle clamped, distance follows the hand
            elif s.phase == "feedback":
                show_target = not s.too_slow
                elapsed = 0.0 if s.fb_start is None else now - s.fb_start
                if trial.clamped_fb and elapsed < trial.feedback_ms:
                    cursor = polar_to_xy(geo, geo.d, clamp_angle)   # endpoint cursor on the ring

            self._render_trial_frame(
                trial,
                fill_start=fill_start,
                show_target=show_target,
                cursor=cursor,
                hint=hint,
                too_slow=(s.phase == "feedback" and s.too_slow),
            )
            pygame.display.flip()

            # ---- timestamps tied to the first frame of a phase being on screen ----
            after_flip = _now_ms()
            if s.phase == "target" and s.target_onset is None:
                s.target_onset = after_flip
            if s.phase == "feedback" and s.fb_start is None:
                s.fb_start = after_flip
            elif s.phase == "feedback" and after_flip - s.fb_start >= fb_total:
                break

            self.clock.tick(cfg.CLAMP_MAX_FPS)

        # ---- store the trial ----
        rt = s.t_leave - s.target_onset
        search_time = s.target_onset - s.t_trial_search
        reach_feedback = "too_slow" if s.too_slow else "good_reach"

        cfg._start_time = start_dt.isoformat(timespec="milliseconds")
        cfg._end_time = datetime.datetime.now().isoformat(timespec="milliseconds")
        update_save_clamp(
            block_name=block_name(trial.num),
            trial_number=trial.num,
            trial_type="clamped_fb" if trial.clamped_fb else "no_fb",
            condition=f"tgt{trial.tgt_angle:g}_rot{trial.rotation:g}",
            reaction_time=rt,
            trial_sequence=self.trial_sequence,
            replay_index=replay_index,
            target_angle=trial.tgt_angle,
            rotation=trial.rotation,
            hand_fb_angle=s.hand_angle,
            movement_time=s.mt,
            search_time=search_time,
            reach_feedback=reach_feedback,
        )
        logger.info(
            "TRIAL_RESULT | trial=%d | replay=%d | block=%s | type=%s | tgt=%g | rot=%g | hand_angle=%.1f | "
            "rt=%.0f | mt=%.0f | search=%.0f | %s",
            trial.num, replay_index, block_name(trial.num),
            "clamped_fb" if trial.clamped_fb else "no_fb",
            trial.tgt_angle, trial.rotation, s.hand_angle, rt, s.mt, search_time, reach_feedback,
        )

    def _run_trial_and_post(self, trial: Trial, replay_index: int) -> None:
        """Run a trial, then the Reset phase: blank interval and, if due, a break message."""
        self._run_trial(trial, replay_index)

        # Reset: cursor and target hidden (start circle outline stays) for RESET_DELAY ms
        t0 = _now_ms()
        while _now_ms() - t0 < cfg.RESET_DELAY:
            self._poll()
            self._render_trial_frame(trial, fill_start=False, show_target=False, cursor=None)
            pygame.display.flip()
            self.clock.tick(cfg.CLAMP_MAX_FPS)

        if trial.between_blocks:
            message = BREAK_MESSAGES.get(trial.between_blocks)
            if message is None:
                logger.warning(f"Unknown between_blocks code {trial.between_blocks} after trial {trial.num}")
            else:
                self.show_message(message)

    # ----- whole task -----

    def run(self) -> pygame.Surface:
        """
        Run the complete task.

        :return: Active display surface after the task (may be updated by fullscreen toggle)
        :rtype: pygame.Surface
        """
        demo_last = cfg.CLAMP_BLOCKS[1][1]
        self._capture_mouse(True)
        try:
            self.show_message(INITIAL_MESSAGE)

            for trial in self.trials:
                self._run_trial_and_post(trial, 0)

                if trial.num in self.key_check_after:
                    self._key_check()
                if trial.num == demo_last:
                    self._understanding_check()

            logger.info("Clamp task finished")
        finally:
            self._capture_mouse(False)
            # Participant-level checks, also saved if the task is interrupted
            finalize_save(
                key_check=f"{self.key_correct}/{self.key_total}",
                understanding_check=f"{self.und_correct}/{self.und_attempts}",
            )
        return self.screen


def run_clamp_task(
    screen: pygame.Surface,
    event_handler: EventHandler,
    replay_instructions: Callable[[pygame.Surface], pygame.Surface] | None = None,
) -> pygame.Surface:
    """
    Run the clamp task (replaces the template's practice and test blocks).

    :param screen: Current display surface
    :type screen: pygame.Surface

    :param event_handler: Centralized event handler instance
    :type event_handler: EventHandler

    :param replay_instructions: Shows the task instructions again (used when the understanding
        check is answered wrongly); receives and returns the display surface
    :type replay_instructions: Callable | None

    :return: Active display surface after the task (may be updated by fullscreen toggle)
    :rtype: pygame.Surface
    """
    return ClampTask(screen, event_handler, replay_instructions).run()
