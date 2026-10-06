# Joystick File Guide (`*_gss_joystick_*.csv`)

This document explains how to read and interpret each column of the CSV file that records frame-by-frame joystick movement during the GSS task.

Each row represents an **instantaneous reading of the stick** at a given moment, not necessarily a completed response.

## Columns

### `timestamp_ms`
Timestamp in milliseconds, measured from the program's internal clock. It is used to order events and compute relative reaction times between rows.

### `trial_index`
The trial number that the reading belongs to. It increments each time a response is confirmed.

### `block`
Name of the block or phase of the task during which the reading was taken (e.g., color practice, Stroop practice, speed/accuracy blocks, test blocks, etc.).

### `x_raw` and `y_raw`
Raw stick position on each axis, exactly as reported by the physical controller. The normal range is **-1.0 to 1.0**, where `0.0` means the stick is centered (at rest).

**How to interpret the sign:**

| Axis | Negative value | Positive value |
|---|---|---|
| `x_raw` | Left | Right |
| `y_raw` | Up | Down |

> Note: the vertical axis is inverted relative to standard math intuition: negative `y_raw` values correspond to "up" and positive values to "down".

Example: `x_raw = -0.8`, `y_raw = 0.1` → the stick is tilted strongly to the left and slightly downward.

### `magnitude`
Indicates **how far from center** the stick is, regardless of direction. It is derived by combining `x_raw` and `y_raw` (Euclidean distance from the center).

- `0` → stick fully centered.
- Values close to `1` → stick pushed to its maximum in that direction.
- Useful for telling whether a movement was "strong" or barely noticeable, independent of where it was pointing.

### `angle_deg`
Angle (in degrees, from `0°` to `360°`) that the stick is pointing toward, computed from `x_raw` and `y_raw`. It behaves like a compass:

- **0° ≈ up**
- **90° ≈ right**
- **180° ≈ down**
- **270° ≈ left**

Intermediate values represent diagonal directions (e.g., ~45° would be "up-right").

### `direction`
A **categorical label** that summarizes `angle_deg` and `magnitude` into one of five possible values:

| Value | Criterion |
|---|---|
| `rest` | The stick is essentially centered (`magnitude` below ~0.1), regardless of angle. |
| `up` | The angle falls outside the ranges below (zone around 0°/360°). |
| `right` | Angle between 45° and 135° (zone around 90°). |
| `down` | Angle between 135° and 225° (zone around 180°). |
| `left` | Angle between 225° and 315° (zone around 270°). |

> Note: this classification uses a different rest threshold than the one that determines whether a movement counts as an actual task "response". A row can show a `direction` other than `rest` without being registered as an official participant response, because this column only describes the physical stick movement, not the task's decision.

### `event`
Marks the **type of moment** that row represents within the trial flow. It can take three values:

| Value | When it is logged |
|---|---|
| `stim_onset` | At the exact moment the stimulus appears on screen (start of the trial, or reset after a fullscreen toggle). On these rows `x_raw` and `y_raw` are stored as `0.0` because they mark a timing reference point, not an actual stick reading. |
| *(empty)* | A routine reading taken every frame while waiting for the participant's response. This is the "continuous sampling" of stick movement during the trial. |
| `response_registered` | The exact frame where the system detected and accepted a valid response (the stick left the dead zone and was classified into a valid direction for the task). |

In short: look for `stim_onset` to know when the trial started, empty rows to see the full movement trajectory, and `response_registered` to identify the precise moment used to compute reaction time and trial correctness.
