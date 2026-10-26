# ./src/core/clamp.py
"""
Clamp task (task phase of the experiment).

Implements Clamp_Task_Procedure.pdf. On each trial the participant moves a (hidden) mouse
cursor from the central start circle through a blue target. In clamp trials the visible cursor
is not controlled by the hand: its angle is fixed relative to the target (target angle +
rotation) while its distance follows the hand. The main measure is the hand angle when the
hand crosses the target ring.

Trial structure: the trials are generated at start-up (no trial files). A cycle is the three
target angles once each in random order. Blocks: no_feedback_baseline (no cursor; skipped while its cycle count is 0), feedback_baseline (cursor follows the hand),
clamp_demo (4 fixed demonstration reaches), clamp (clamped cursor, rotation = +/-ROTATION by
mapping) and after_effect (no cursor). Angles are counter-clockwise from +x; + = CCW, - = CW.

Flow (run_clamp_task):
    initial screen -> trials (with break messages) -> understanding check after the clamp
    demonstration (replays the task instructions and the four demonstration trials until
    answered correctly).

All timing uses time.perf_counter(); the display loop is frame-based (vsync).
"""


from __future__ import annotations

import array
import datetime
import math
import random
import time
from dataclasses import dataclass
from typing import Callable

import pygame

import utils.config as cfg
from utils.event_handler import ControlState, EventHandler
from utils.logger import get_logger
from utils.saves import update_save_clamp, save_trajectory, finalize_hand_variables
from ui.pygame_render import toggle_full_screen


logger = get_logger("./src/core/clamp")


# ---------- Messages (Clamp_Task_Procedure.pdf, Table 4 and Section 6) ----------

INITIAL_MESSAGE = [
    "Move the white dot to the center.",
    "The white dot will disappear during your reach.",
    "Quickly move to the blue target.",
    "Press SPACE BAR when you are ready to proceed.",
]

AFTER_NO_FB_BASELINE_MESSAGE = [
    "The white dot will now be visible during your reach and will follow your hand.",
    "Continue moving quickly to the blue target.",
    "Press SPACE BAR when you are ready to proceed.",
]

AFTER_BASELINE_MESSAGE = [
    "The white dot will now be present, but will NOT be under your control.",
    "IGNORE the white dot as best as you can and continue aiming DIRECTLY towards the blue target.",
    "This will be a practice trial",
    "Press SPACE BAR when you are ready to proceed.",
]

AFTER_DEMO_MESSAGE = [
    "Again, the white dot will NOT be under your control.",
    "IGNORE the white dot as best as you can and continue aiming DIRECTLY towards the blue target.",
    "Press SPACE BAR when you are ready to proceed.",
]

AFTER_CLAMP_MESSAGE = [
    "The white dot will now be hidden.",
    "Continue aiming DIRECTLY towards the blue target.",
    "Press SPACE BAR when you are ready to proceed.",
]

UNDERSTANDING_QUESTION = [
    "This is an instruction understanding check.",
    "Press 'a' if you should ignore the white dot and aim directly towards the target.",
    "Press 'b' if you should be aiming away from the target.",
]
UNDERSTANDING_CORRECT_KEY = "a"

MOVE_FASTER_TEXT = "Please move faster and further"
PAUSE_LINES = ["Please take a short break and wait.", "The task will continue in {n} seconds."]
SEARCH_HINT_TEXT = "To find your cursor, try moving your mouse to the center of the screen."


# ---------- Trials ----------

@dataclass(frozen=True)
class Trial:
    """One trial of the task."""
    num: int                    # trial number over the whole task (1..CLAMP_N_TRIALS)
    block: str                  # no_feedback_baseline / feedback_baseline / clamp_demo / clamp / after_effect
    cn: int | None              # cycle number within the block (None for clamp_demo)
    tn: int                     # trial number within the block
    phase: str | None           # early / late / None
    tgt_angle: float            # target angle (deg, counter-clockwise from +x)
    rotation: float             # clamp rotation (deg, + = CCW)
    cursor_fb: str              # veridical_fb / clamped_fb / no_fb
    clamp_direction: str | None # CCW / CW for clamp_demo and clamp, None otherwise
    feedback_ms: int            # endpoint feedback duration (ms)
    break_message: list[str] | None     # message shown after this trial
    pause_s: int = 0                    # countdown pause (s) shown after this trial, before the message


def build_trials(mapping: int | None) -> list[Trial]:
    """
    Generate the trial series for a participant.

    Mapping 1 gives a counter-clockwise clamp (+ROTATION), mapping 2 a clockwise one
    (-ROTATION); clamp_demo keeps its own fixed rotations. Within a cycle the three target
    angles come in random order.

    :param mapping: Task mapping (1 / 2)
    :type mapping: int | None

    :return: The trials in presentation order
    :rtype: list[Trial]
    """
    ccw = mapping != 2
    clamp_rotation = cfg.ROTATION if ccw else -cfg.ROTATION
    direction = "CCW" if ccw else "CW"
    n_targets = len(cfg.CLAMP_TARGET_ANGLES)

    trials: list[Trial] = []

    def add_cycles(block: str, cursor_fb: str, rotation: float, clamp_dir: str | None,
                   end_message: list[str] | None, pause_s: int = 0) -> None:
        n_cycles = cfg.CLAMP_CYCLES[block]
        if n_cycles == 0:
            return      # block disabled
        n_block = n_cycles * n_targets
        window = cfg.CLAMP_PHASE_TRIALS[block]
        assert 2 * window <= n_block, f"early/late windows overlap in {block}"
        tn = 0
        for cn in range(1, n_cycles + 1):
            order = list(cfg.CLAMP_TARGET_ANGLES)
            random.shuffle(order)
            for tgt in order:
                tn += 1
                phase = "early" if tn <= window else ("late" if tn > n_block - window else None)
                trials.append(Trial(
                    num=len(trials) + 1, block=block, cn=cn, tn=tn, phase=phase,
                    tgt_angle=float(tgt), rotation=float(rotation), cursor_fb=cursor_fb,
                    clamp_direction=clamp_dir, feedback_ms=cfg.CLAMP_FEEDBACK_MS,
                    break_message=end_message if tn == n_block else None,
                    pause_s=pause_s if tn == n_block else 0,
                ))

    add_cycles("no_feedback_baseline", "no_fb", 0.0, None, AFTER_NO_FB_BASELINE_MESSAGE)
    add_cycles("feedback_baseline", "veridical_fb", 0.0, None, AFTER_BASELINE_MESSAGE)

    for tn, (tgt, rot) in enumerate(cfg.CLAMP_DEMO_REACHES, start=1):
        trials.append(Trial(
            num=len(trials) + 1, block="clamp_demo", cn=None, tn=tn, phase=None,
            tgt_angle=float(tgt), rotation=float(rot), cursor_fb="clamped_fb",
            clamp_direction=direction, feedback_ms=cfg.CLAMP_FEEDBACK_MS,
            break_message=AFTER_DEMO_MESSAGE if tn == len(cfg.CLAMP_DEMO_REACHES) else None,
        ))

    add_cycles("clamp", "clamped_fb", clamp_rotation, direction, AFTER_CLAMP_MESSAGE, cfg.CLAMP_PAUSE_S)
    add_cycles("after_effect", "no_fb", 0.0, None, None)

    assert len(trials) == cfg.CLAMP_N_TRIALS
    return trials


def wrap_180(angle_deg: float) -> float:
    """Wrap an angle to [-180, 180)."""
    return (angle_deg + 180.0) % 360.0 - 180.0


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
    hand_x_end: float = 0.0         # hand position at the crossing, relative to the start (px, y positive = up)
    hand_y_end: float = 0.0
    error: float = 0.0
    too_slow: bool = False
    too_far: bool = False
    slow_msg: bool = False          # movement time above TOO_SLOW_MSG_TIME: show the message
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
        self.knock = self._make_knock()
        self.flip_sign = 1.0 if cfg.MAPPING != 2 else -1.0     # participant's clamp direction: CCW +1, CW -1

        self.trials = build_trials(cfg.MAPPING)
        logger.info(f"Trials generated: {len(self.trials)} (PID = {cfg.PID}, mapping = {cfg.MAPPING})")

        self.und_attempts = 0
        self.und_correct = 0

        self.capturing = False
        self.geo_version = 0    # incremented whenever the display (and geometry) is rebuilt
        self._rebuild()

    # ----- sound -----

    def _make_knock(self) -> pygame.mixer.Sound | None:
        """Synthesize the short 'knock' sound (no audio file needed); None if audio is unavailable."""
        try:
            rate = 44100
            pygame.mixer.quit()
            pygame.mixer.init(frequency=rate, size=-16, channels=1, buffer=512)
            dur = cfg.KNOCK_MS / 1000.0
            buf = array.array("h")
            for i in range(int(rate * dur)):
                t = i / rate
                env = math.exp(-t / (dur / 4.0))        # fast decay
                v = 0.7 * math.sin(2 * math.pi * cfg.KNOCK_FREQ * t) + 0.3 * math.sin(2 * math.pi * 2.3 * cfg.KNOCK_FREQ * t)
                buf.append(int(32767 * cfg.KNOCK_VOLUME * env * v))
            return pygame.mixer.Sound(buffer=buf.tobytes())
        except Exception as e:      # no audio device etc.: run silently
            logger.warning(f"Knock sound unavailable: {e}")
            return None

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
        message: str | None = None,
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
        if message:
            self._draw_centered(message, 2 * geo.h / 3, cfg.RED_RGB)   # below the start circle

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

    def show_pause(self, seconds: int) -> None:
        """Mandatory pause with a countdown; continues automatically when it reaches zero."""
        logger.info(f"PAUSE | {seconds} s")
        self._flush()
        t0 = _now_ms()
        while True:
            self._poll()
            remaining = seconds - (_now_ms() - t0) / 1000.0
            if remaining <= 0:
                return
            self._draw_lines([line.format(n=math.ceil(remaining)) for line in PAUSE_LINES])
            pygame.display.flip()
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

    def _understanding_check(self) -> None:
        """
        Understanding check after the clamp demonstration. On a wrong answer the task
        instructions and the four demonstration trials are replayed, then the question is
        asked again, until it is answered correctly.
        """
        demo_trials = [t for t in self.trials if t.block == "clamp_demo"]
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
            self.show_message(AFTER_BASELINE_MESSAGE)
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
        frames: list = []       # per-frame trajectory: (frame, time_ms, state, hand_x, hand_y, cursor)
        fb_total = trial.feedback_ms    # feedback period; becomes TOO_SLOW_FB_TIME for a too-slow reach

        while True:
            state = self._poll()

            # Display rebuilt (fullscreen toggled): geometry changed, restart this trial
            if geo_version != self.geo_version:
                logger.warning(f"Display changed during trial {trial.num}; trial restarted")
                geo_version = self.geo_version
                s = self._new_state()
                frames.clear()

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
                s.hand_x_end = s.hx - geo.cx
                s.hand_y_end = geo.cy - s.hy
                s.error = wrap_180(s.hand_angle - trial.tgt_angle)     # + = CCW, - = CW
                s.too_slow = s.mt > cfg.TOO_SLOW_TIME              # flag (> 500 ms)
                s.slow_msg = s.mt > cfg.TOO_SLOW_MSG_TIME          # message only above 750 ms
                s.too_far = abs(s.error) >= cfg.TOO_FAR_ERROR      # recorded only, no feedback shown
                fb_total = cfg.TOO_SLOW_FB_TIME if s.slow_msg else trial.feedback_ms
                if not s.too_slow and self.knock is not None:
                    self.knock.play()       # fast enough: knock, on every trial regardless of accuracy
                s.phase = "feedback"

            # ---- what to draw ----
            fill_start = False
            show_target = False
            cursor: tuple[float, float] | None = None
            hint = False
            message: str | None = None
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
                if trial.cursor_fb == "clamped_fb":
                    cursor = polar_to_xy(geo, r, clamp_angle)   # angle clamped, distance follows the hand
                elif trial.cursor_fb == "veridical_fb":
                    cursor = (s.hx, s.hy)                       # cursor follows the hand
            elif s.phase == "feedback":
                show_target = not s.slow_msg
                if s.slow_msg:
                    message = MOVE_FASTER_TEXT
                elapsed = 0.0 if s.fb_start is None else now - s.fb_start
                if elapsed < trial.feedback_ms and not s.slow_msg:     # the message replaces the cursor
                    if trial.cursor_fb == "clamped_fb":
                        cursor = polar_to_xy(geo, geo.d, clamp_angle)   # endpoint cursor on the ring
                    elif trial.cursor_fb == "veridical_fb":
                        cursor = polar_to_xy(geo, geo.d, s.hand_angle)  # endpoint cursor at the hand's angle

            frames.append((
                len(frames) + 1, now - s.t_trial_search, s.phase, s.hx - geo.cx, geo.cy - s.hy,
                None if cursor is None else (cursor[0] - geo.cx, geo.cy - cursor[1]),
            ))

            self._render_trial_frame(
                trial,
                fill_start=fill_start,
                show_target=show_target,
                cursor=cursor,
                hint=hint,
                message=message,
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
        good_reach = int(not (s.too_slow or s.too_far))

        cfg._start_time = start_dt.isoformat(timespec="milliseconds")
        cfg._end_time = datetime.datetime.now().isoformat(timespec="milliseconds")
        update_save_clamp(
            block_name=trial.block,
            cycle_number=trial.cn,
            block_trial_number=trial.tn,
            phase=trial.phase,
            trial_number=trial.num,
            cursor_feedback=trial.cursor_fb,
            condition=f"tgt{trial.tgt_angle:g}_rot{trial.rotation:g}",
            reaction_time=rt,
            replay_index=replay_index if trial.block == "clamp_demo" else None,
            target_angle=trial.tgt_angle,
            clamp_offset=trial.rotation,
            clamp_direction=trial.clamp_direction,
            hand_angle=s.hand_angle,
            hand_x_end=s.hand_x_end,
            hand_y_end=s.hand_y_end,
            hand=s.hand_angle - trial.tgt_angle,
            hand_flip=s.error * self.flip_sign,
            error=s.error,
            movement_time=s.mt,
            search_time=search_time,
            good_reach=good_reach,
            too_slow=int(s.too_slow),
            too_far=int(s.too_far),
        )
        save_trajectory(
            block_name=trial.block,
            trial_number=trial.num,
            replay_index=replay_index if trial.block == "clamp_demo" else None,
            frames=frames,
        )
        logger.info(
            "TRIAL_RESULT | trial=%d | replay=%d | block=%s | CN=%s | TN=%d | phase=%s | fb=%s | tgt=%g | rot=%g | "
            "hand_angle=%.1f | error=%.1f | rt=%.0f | mt=%.0f | search=%.0f | good=%d | slow=%d | far=%d",
            trial.num, replay_index, trial.block, trial.cn, trial.tn, trial.phase, trial.cursor_fb,
            trial.tgt_angle, trial.rotation, s.hand_angle, s.error, rt, s.mt, search_time, good_reach, int(s.too_slow), int(s.too_far),
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

        if trial.pause_s:
            self.show_pause(trial.pause_s)
        if trial.break_message:
            self.show_message(trial.break_message)

    # ----- whole task -----

    def run(self) -> pygame.Surface:
        """
        Run the complete task.

        :return: Active display surface after the task (may be updated by fullscreen toggle)
        :rtype: pygame.Surface
        """
        n_demo = len(cfg.CLAMP_DEMO_REACHES)
        self._capture_mouse(True)
        try:
            self.show_message(INITIAL_MESSAGE)

            for trial in self.trials:
                self._run_trial_and_post(trial, 0)

                if trial.block == "clamp_demo" and trial.tn == n_demo:
                    self._understanding_check()

            logger.info("Clamp task finished")
        finally:
            self._capture_mouse(False)
            try:
                finalize_hand_variables()       # moving average, residual, outlier removal, baseline, adaptation
            except Exception as e:
                logger.error(f"Hand variables post-processing failed: {e}")
            # Understanding check outcome is only logged (no results column)
            logger.info(f"Understanding check: {self.und_correct}/{self.und_attempts} (correct/attempts)")
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
