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

- [x] **Implement proper logging** (all files)
- [x] **Remove unused code**
- [x] **Add named constants for magic numbers**
- [x] **Consistent method naming convention**
- [x] **Clarify config file purpose** (Clarified via logging and method documentation that it's a keyd config)

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
- [x] ~~Sprint 3: Code Quality~~ (2025-12-30)
  - Centralized logging system (src/core/logger.py)
  - Removed dead code (window_move_left)
  - Named constants for delays
  - Standardized private method naming (_)
  - Documented config/reload relationship with keyd
