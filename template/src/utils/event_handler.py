# ./src/utils/event_handler.py
"""
This module defines a centralized event handling abstraction for the experiment.

The EventHandler is responsible for:
- Collecting raw pygame events from external input sources.
- Translating device-specific events into standardized, high-level control signals.
- Providing a clean interface between low-level input events and experiment logic.

Design principles:
- Decoupling: experiment flow should not directly depend on pygame event types.
- Edge-trigger semantics: control flags are valid for a single frame only.
- Passive role: this module does NOT execute actions or call external functions.
"""


from __future__ import annotations

import pygame
from dataclasses import dataclass

import utils.config as cfg


@dataclass
class ControlState:
    """
    Snapshot of control signals for a single frame.

    All fields are edge-triggered:
    - A value of True indicates that the corresponding input event occurred during the current frame.
    - All fields are reset at the beginning of the next polling cycle.
    """
    quit: bool = False
    toggle_full_screen: bool = False
    version_1: bool = False
    version_2: bool = False
    next_page: bool = False
    option_1: bool = False
    option_2: bool = False


class EventHandler:
    """
    Centralized event handler for collecting and normalizing input events.

    The EventHandler polls pygame events each frame and converts them into a ControlState object that can be safely consumed by the experiment loop.
    """

    def __init__(self) -> None:
        self._state = ControlState()

    def poll(self) -> ControlState:
        """
        Poll pygame events and return a control-state snapshot for the current frame.

        :return: ControlState
        """
        # Reset state every frame (edge-triggered behavior)
        self._state = ControlState()

        for event in pygame.event.get():
            self._process_event(event)

        return self._state

    def _process_event(self, event: pygame.event.Event) -> None:
        """
        Translate a single pygame event into control signals.

        :param event: A single pygame event retrieved from the event queue
        :type event: pygame.event.Event

        :return: None
        """
        # Quit pygame (x)
        if event.type == pygame.QUIT:
            self._state.quit = True
            return

        # Handle keypress (keydown)
        if event.type == pygame.KEYDOWN:
            self._process_keydown(event.key)

    def _process_keydown(self, key: int) -> None:
        """
        Handle keyboard keydown events and update control flags.

        :param key: Pygame key code (e.g., pygame.K_ESCAPE)
        :type key: int

        :return: None
        """
        # Toggle full screen (ESC)
        if key == pygame.K_ESCAPE:
            self._state.toggle_full_screen = True
        
        # Proceed to next page (SPACE)
        elif key == pygame.K_SPACE:
            self._state.next_page = True

        # Select [Version 1] (1)
        elif key == pygame.K_1:
            self._state.version_1 = True
        
        # Select [Version 2] (2)
        elif key == pygame.K_2:
            self._state.version_2 = True

        # Select [Option 1] for response to stimuli (d)
        elif key == pygame.K_d:
            if cfg.VERSION == 1:
                self._state.option_1 = True
            else:   # cfg.VERSION == 2
                self._state.option_2 = True

        # Select [Option 2] for response to stimuli (k)
        elif key == pygame.K_k:
            if cfg.VERSION == 1:
                self._state.option_2 = True
            else:   # cfg.VERSION == 2
                self._state.option_1 = True
        
        # TODO: Add additional input mappings and proper docstrings if necessary
