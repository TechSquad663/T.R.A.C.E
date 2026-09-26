"""Unit tests for TRACE theme management and dark/light switching."""
import pytest
from app.theme import (
    ThemeManager,
    theme_manager,
    THEME_COLORS,
    DARK_THEME_COLORS,
    LIGHT_THEME_COLORS,
    DARK_STYLESHEET,
    LIGHT_STYLESHEET,
    get_stylesheet,
    get_theme_colors,
)


def test_theme_stylesheets_generated():
    """Verify both dark and light stylesheets are valid and distinct."""
    assert len(DARK_STYLESHEET) > 500
    assert len(LIGHT_STYLESHEET) > 500
    assert DARK_STYLESHEET != LIGHT_STYLESHEET

    # Dark should contain deep obsidian background
    assert "#0B0F19" in DARK_STYLESHEET
    # Light should contain crisp light slate background
    assert "#F1F5F9" in LIGHT_STYLESHEET


def test_theme_palettes_completeness():
    """Verify all expected forensic color tokens exist in both palettes."""
    expected_tokens = [
        "bg_dark", "bg_card", "bg_card_alt", "border", "border_light",
        "text_primary", "text_secondary", "text_muted", "accent_blue",
        "accent_purple", "accent_amber", "accent_orange", "accent_red",
        "accent_emerald", "accent_cyan"
    ]
    for token in expected_tokens:
        assert token in DARK_THEME_COLORS
        assert token in LIGHT_THEME_COLORS


def test_theme_manager_switching():
    """Verify switching themes updates current_theme, THEME_COLORS, and emits signals."""
    tm = ThemeManager.get_instance()
    received_signals = []
    
    def on_change(name):
        received_signals.append(name)
        
    tm.theme_changed.connect(on_change)

    # Switch to light
    tm.set_theme("light")
    assert tm.current_theme == "light"
    assert not tm.is_dark()
    assert THEME_COLORS["bg_dark"] == LIGHT_THEME_COLORS["bg_dark"]
    assert THEME_COLORS["text_primary"] == LIGHT_THEME_COLORS["text_primary"]
    assert "light" in received_signals

    # Toggle to dark
    tm.toggle_theme()
    assert tm.current_theme == "dark"
    assert tm.is_dark()
    assert THEME_COLORS["bg_dark"] == DARK_THEME_COLORS["bg_dark"]
    assert THEME_COLORS["text_primary"] == DARK_THEME_COLORS["text_primary"]
    assert "dark" in received_signals

    # Clean up signal connection
    tm.theme_changed.disconnect(on_change)
