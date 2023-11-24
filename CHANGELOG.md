# 1.3.0 - 2023-11-24

### Added
- Zoom out click mode

### Fixed
- Prevent clicks outside of the canvas to be registered as canvas clicks
- Weird zoom in behaviour
  
### Improved
- I made the rendering process a lot faster with a new algorithm, its my first time with multiprocessing

# 1.2.0 - 2023-11-24

### Fixed
- Minor display issues
- Bug with click markers

### Added
- Click modes
- (dev) Flake8 linting and type-checking

# 1.1.0 - 2023-11-23

### Fixed
- Bug with state loading

# 1.0.0 - 2023-11-23

### Added 
- multithreading (multiprocessing)
- `--threads/-t` option
- `threads` command
- screenshot threads (also command and cmdline option)
- A lot of new bugs for sure...

### Improved 
- Code quality (a lot)

# 0.6.0 - 2023-11-16

### Added
- Load and save state commands
- `-ls/--load-state` option

### Fixed
- #30 screenshots wrongly centered

# 0.5.0 - 2023-11-13

### Added
- `precision` command

### Fixed
- Fixed #17 - Custom numeric precision not taken into account

# 0.4.0 - 2023-11-10

### Added
- Average divergence
- Allow cancelling screenshots
- `move_dist` command
- Value control commands without args now print out the current value
- `zoom_lvl` command
- `pos` command
- Show zoom level in canvas border subtitle
- `click_pos` command

# Fixed
- Some errors in help messages, and better formating

# 0.3.1 - 2023-11-06

### Fixed
- Fix random error at startup

# 0.3.0 - 2023-10-30

### Added
- Capture command
- CaptureFit command 
- MaxIter command
- Extra help for commands (`help command_name`)

### Fixed
- Errors in help messages

# 0.2.0 - 2023-10-30

### Added
- Command input below log panel
- `-v` / `--version` option
- Published on PyPI

### Fixed
- Minor imperfections

### Changed
- Bump click_extra to 4.7.1

# O.1.0-beta - 2023-10-26

### Added 

- Base code