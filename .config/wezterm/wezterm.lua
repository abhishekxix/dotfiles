local wezterm = require("wezterm")

local config = wezterm.config_builder()

config.color_scheme = "Tokyo Night"
config.font = wezterm.font("JetbrainsMono NF")
config.font_size = 13
config.window_background_opacity = 0.95
config.enable_tab_bar = false

return config
