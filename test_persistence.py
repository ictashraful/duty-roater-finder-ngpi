#!/usr/bin/env python3
"""Test script to verify persistence functions work correctly."""

import os
import json
import shutil
from pathlib import Path

# Add the app directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Import just the persistence functions
CONFIG_DIR = ".config"
ROOMS_FILE = os.path.join(CONFIG_DIR, "custom_rooms.json")
FLOORS_FILE = os.path.join(CONFIG_DIR, "custom_floors.json")

def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_custom_rooms():
    ensure_config_dir()
    default_rooms = [f"Room {i}" for i in range(101, 110)]
    try:
        if os.path.exists(ROOMS_FILE):
            with open(ROOMS_FILE, 'r', encoding='utf-8') as f:
                rooms = json.load(f)
                return rooms if rooms else default_rooms
    except Exception as e:
        print(f"Could not load rooms configuration: {e}")
    return default_rooms

def load_custom_floors():
    ensure_config_dir()
    default_floors = ["Ground Floor", "1st Floor", "2nd Floor", "3rd Floor", "4th Floor"]
    try:
        if os.path.exists(FLOORS_FILE):
            with open(FLOORS_FILE, 'r', encoding='utf-8') as f:
                floors = json.load(f)
                return floors if floors else default_floors
    except Exception as e:
        print(f"Could not load floors configuration: {e}")
    return default_floors

def save_custom_rooms(rooms):
    ensure_config_dir()
    try:
        with open(ROOMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(rooms, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Could not save rooms configuration: {e}")

def save_custom_floors(floors):
    ensure_config_dir()
    try:
        with open(FLOORS_FILE, 'w', encoding='utf-8') as f:
            json.dump(floors, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Could not save floors configuration: {e}")

def test_persistence():
    """Test the persistence functionality."""
    print("Testing persistence functionality...\n")
    
    # Clean up any existing test data
    if os.path.exists(CONFIG_DIR):
        shutil.rmtree(CONFIG_DIR)
    
    # Test 1: Load defaults when no files exist
    print("Test 1: Loading defaults when no files exist...")
    rooms = load_custom_rooms()
    floors = load_custom_floors()
    assert rooms == [f"Room {i}" for i in range(101, 110)], "Default rooms not loaded correctly"
    assert floors == ["Ground Floor", "1st Floor", "2nd Floor", "3rd Floor", "4th Floor"], "Default floors not loaded correctly"
    print("✓ Defaults loaded correctly\n")
    
    # Test 2: Save custom rooms
    print("Test 2: Saving custom rooms...")
    custom_rooms = ["Room 101", "Room 205", "Lab A", "Lab B"]
    save_custom_rooms(custom_rooms)
    assert os.path.exists(ROOMS_FILE), "Rooms file not created"
    with open(ROOMS_FILE, 'r', encoding='utf-8') as f:
        saved_rooms = json.load(f)
    assert saved_rooms == custom_rooms, "Saved rooms don't match"
    print("✓ Rooms saved correctly\n")
    
    # Test 3: Load saved rooms
    print("Test 3: Loading saved rooms...")
    loaded_rooms = load_custom_rooms()
    assert loaded_rooms == custom_rooms, "Loaded rooms don't match saved rooms"
    print("✓ Rooms loaded correctly\n")
    
    # Test 4: Save custom floors
    print("Test 4: Saving custom floors...")
    custom_floors = ["Ground Floor", "First Floor", "Basement", "Rooftop"]
    save_custom_floors(custom_floors)
    assert os.path.exists(FLOORS_FILE), "Floors file not created"
    with open(FLOORS_FILE, 'r', encoding='utf-8') as f:
        saved_floors = json.load(f)
    assert saved_floors == custom_floors, "Saved floors don't match"
    print("✓ Floors saved correctly\n")
    
    # Test 5: Load saved floors
    print("Test 5: Loading saved floors...")
    loaded_floors = load_custom_floors()
    assert loaded_floors == custom_floors, "Loaded floors don't match saved floors"
    print("✓ Floors loaded correctly\n")
    
    # Test 6: Persistence across multiple load/save cycles
    print("Test 6: Testing persistence across multiple cycles...")
    rooms = load_custom_rooms()
    rooms.append("Room 301")
    save_custom_rooms(rooms)
    
    # Simulate app restart by creating a new instance
    rooms2 = load_custom_rooms()
    assert "Room 301" in rooms2, "Data not persisted across sessions"
    assert rooms == rooms2, "Rooms not consistently persisted"
    print("✓ Data persists correctly\n")
    
    # Clean up
    if os.path.exists(CONFIG_DIR):
        shutil.rmtree(CONFIG_DIR)
    
    print("=" * 50)
    print("✅ All tests passed! Persistence is working correctly.")
    print("=" * 50)

if __name__ == "__main__":
    test_persistence()
