# A Home Assistant Integration for Samsung The Frame Art Mode

### Background

This is a fork of @joakimjalden's Frame art switch integration which introduces a full platform supported by @NickWaterton's async `samsungtvws` library. This fork is specifically designed to work with the 2024 Frame TV model and has not been tested to work with any other models.

### Installation

The integration can be installed by copying all the files to `/<config directory>/custom_components/frame_art` and adding through the UI. You will need to press "Allow" on the TV.

## To Do

- [x] Add async support
- [x] Reliability fixes for 2024 Frame TVs
- [x] Switch to platform integration
- [x] Add config flow through UI
- [ ] Add services for setting art and TV settings
- [ ] Add sensors for TV settings (brightness)

## Why not implement directly in the Samsung TV integration?

This is the best idea long-term, however I don't have the time to put together a full PR and I'd rather just write the code myself. If anyone would like to, feel free to use my code.

