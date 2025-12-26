local wezterm = require("wezterm")

local config = wezterm.config_builder()

config.color_scheme = "Tokyo Night"
config.font = wezterm.font("JetbrainsMono NF")
config.font_size = 13
config.window_background_opacity = 0.95
config.enable_tab_bar = false

config.keys = {
  {
    key = "m",
    mods = "CMD",
    action = wezterm.action.DisableDefaultAssignment,
  },
  {
    key = "n",
    mods = "CTRL|SHIFT",
    action = wezterm.action.DisableDefaultAssignment,
  },
  {
    key = "t",
    mods = "CTRL|SHIFT",
    action = wezterm.action.DisableDefaultAssignment,
  },
  {
    key = "w",
    mods = "CTRL|SHIFT",
    action = wezterm.action.DisableDefaultAssignment,
  },
  {
    key = "Tab",
    mods = "CTRL|SHIFT",
    action = wezterm.action.DisableDefaultAssignment,
  },
  {
    key = "Tab",
    mods = "CTRL",
    action = wezterm.action.DisableDefaultAssignment,
  },
  {
    key = "r",
    mods = "CTRL|SHIFT",
    action = wezterm.action.DisableDefaultAssignment,
  },
  {
    key = "Space",
    mods = "CTRL|SHIFT",
    action = wezterm.action.DisableDefaultAssignment,
  },
  {
    key = "Space",
    mods = "CTRL|SHIFT",
    action = wezterm.action.DisableDefaultAssignment,
  },
  {
    key = "m",
    mods = "CMD",
    action = wezterm.action.DisableDefaultAssignment,
  },
}

for i = 1, 9, 1 do
  table.insert(config.keys, {
    key = tostring(i),
    mods = "CTRL|SHIFT",
    action = wezterm.action.DisableDefaultAssignment,
  })
end

return config
