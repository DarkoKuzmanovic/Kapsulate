# Kapsulate Tasks

> **Note:** Mark tasks as complete by changing `[ ]` to `[x]`

---

## Sprint 1: Critical Fixes
*These issues prevent the app from working correctly and should be addressed first.*

- [x] **Fix hardcoded relative paths** (`main.py`)
- [x] **Handle DBus registration failure properly** (`listener.py`)
- [x] **Fix or remove `reload_config()`** (`main.py`)

---

## Sprint 2: Functionality Fixes
*These issues cause features to work incorrectly or provide poor user experience.*

- [x] **Add QCoreApplication to CLI** (`cli.py`)
- [x] **Show password feedback to user** (`listener.py`, `actions.py`)
- [x] **Add null check for screen in OSD** (`overlay.py`)
- [x] **Replace blocking `time.sleep()` with Qt timers** (`text_engine.py`)

---

## Sprint 3: Code Quality
*These improve maintainability and developer experience.*

- [ ] **Implement proper logging** (all files)
  - Replace `print()` statements with Python `logging` module
  - Add log levels (DEBUG, INFO, WARNING, ERROR)
  - Enable file output for debugging

- [ ] **Remove unused code**
  - `window_move_left()` empty method in `actions.py:48-54`
  - Unused imports in various files

- [ ] **Add named constants for magic numbers** (`text_engine.py`)
  - `0.05` and `0.1` delays should be named constants
  - Example: `KEY_RELEASE_DELAY = 0.05`

- [ ] **Consistent method naming convention**
  - Decide on underscore prefix for private methods
  - Apply consistently across all classes

- [ ] **Clarify config file purpose**
  - `kapsulate.conf` is a `keyd` config, not parsed by Python
  - Either: remove config menu items, or add actual Python config (JSON/TOML)

---

## Sprint 4: Enhancements (Future)
*Nice-to-have improvements for later.*

- [ ] **Listen for theme changes at runtime**
  - Update tray icon when user switches themes
  - Use DBus signal from `org.freedesktop.portal.Settings`

- [ ] **Add "About" dialog**
  - Show version, author, links

- [ ] **System startup integration**
  - Add `.desktop` file for autostart
  - Add "Start with system" toggle in menu

- [ ] **Error notification system**
  - Show tray notifications for errors instead of just printing

---

## Completed
*Move completed tasks here for reference.*

- [x] ~~Refactor system tray icon to use KDE-idiomatic approach~~ (2025-12-30)
- [x] ~~Sprint 1: Critical Fixes~~ (2025-12-30)
- [x] ~~Sprint 2: Functionality Fixes~~ (2025-12-30)
  - Added QCoreApplication to CLI
  - Added OSD feedback for passwords
  - Fixed OSD screen null crash
  - Moved text processing to background thread (non-blocking)
