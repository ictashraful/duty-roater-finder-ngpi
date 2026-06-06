# Room & Floor Persistence Fix

## Problem
When users logged out from the control room dashboard, all custom room numbers and floor numbers that were renamed or modified would reset to the default values. This was because the data was stored only in Streamlit's session state, which is cleared when the session ends (e.g., on logout).

## Solution
Implemented **persistent JSON file storage** to save and load custom rooms and floors across sessions.

### Changes Made

#### 1. **Added Imports**
- Added `import json` to support JSON file handling

#### 2. **Persistence Functions** (lines 27-74)
Created four utility functions for persistence:

- **`ensure_config_dir()`**: Creates `.config` directory if it doesn't exist
- **`load_custom_rooms()`**: Loads rooms from `custom_rooms.json` or returns defaults
- **`load_custom_floors()`**: Loads floors from `custom_floors.json` or returns defaults
- **`save_custom_rooms(rooms)`**: Saves rooms to JSON file
- **`save_custom_floors(floors)`**: Saves floors to JSON file

#### 3. **Session State Initialization** (lines 79-83)
Updated initialization to load from persistent storage:
```python
if "custom_rooms" not in st.session_state:
    st.session_state["custom_rooms"] = load_custom_rooms()

if "custom_floors" not in st.session_state:
    st.session_state["custom_floors"] = load_custom_floors()
```

#### 4. **Save Calls Added** 
Added `save_*()` function calls after every modification:

- **Add Room**: Line 487 - saves after appending new room
- **Rename Room**: Line 507 - saves after renaming
- **Delete Room**: Line 519 - saves after deleting
- **Add Floor**: Line 552 - saves after appending new floor
- **Rename Floor**: Line 568 - saves after renaming
- **Delete Floor**: Line 580 - saves after deleting

### How It Works

1. **On App Start**: 
   - If `.config/custom_rooms.json` and `.config/custom_floors.json` exist, they are loaded
   - If they don't exist, default values are used

2. **During Session**:
   - All add/rename/delete operations are performed in session state (for instant UI updates)
   - After each operation, the updated list is saved to JSON file

3. **On Logout/New Session**:
   - Previous session state is cleared
   - New session loads from `.config/` JSON files
   - User's custom rooms and floors are restored

### Storage Location
- **Rooms**: `.config/custom_rooms.json`
- **Floors**: `.config/custom_floors.json`

These files are created automatically in the app's working directory.

### Error Handling
- If files can't be loaded, defaults are used
- If files can't be saved, errors are printed to console (doesn't crash the app)
- Graceful fallback to defaults ensures app always works

## Testing
✅ All persistence functions tested and working:
- Default loading when no files exist
- Saving custom data to JSON files
- Loading saved data on restart
- Multiple load/save cycles maintain data integrity

## User Experience
Now when users:
1. ✅ Configure rooms and floors in the Control Room Dashboard
2. ✅ Log out
3. ✅ Log back in
4. **Their custom rooms and floors will be preserved!**
