import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Define the storage directory relative to this file
STORAGE_DIR = Path(__file__).parent.parent.parent.parent / "data"
CHATS_FILE = STORAGE_DIR / "chats.json"

def ensure_storage_exists():
    """Create storage directory and files if they don't exist"""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not CHATS_FILE.exists():
        with open(CHATS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def save_chats(chats: List[Dict[str, Any]]) -> bool:
    """Save chats to JSON file"""
    try:
        ensure_storage_exists()
        with open(CHATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(chats, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving chats: {e}")
        return False

def load_chats() -> List[Dict[str, Any]]:
    """Load chats from JSON file"""
    try:
        ensure_storage_exists()
        with open(CHATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Error decoding chats file, returning empty list")
        return []
    except Exception as e:
        print(f"Error loading chats: {e}")
        return []

def update_chat(chat_id: str, updated_chat: Dict[str, Any]) -> bool:
    """Update a specific chat in storage"""
    try:
        chats = load_chats()
        for i, chat in enumerate(chats):
            if chat.get('id') == chat_id:
                chats[i] = updated_chat
                return save_chats(chats)
        return False
    except Exception as e:
        print(f"Error updating chat: {e}")
        return False

def delete_chat(chat_id: str) -> bool:
    """Delete a specific chat from storage"""
    try:
        chats = load_chats()
        filtered_chats = [chat for chat in chats if chat.get('id') != chat_id]
        return save_chats(filtered_chats)
    except Exception as e:
        print(f"Error deleting chat: {e}")
        return False

def chat_exists(chat_id: str) -> bool:
    """Check if a chat exists in storage"""
    try:
        chats = load_chats()
        return any(chat.get('id') == chat_id for chat in chats)
    except Exception as e:
        print(f"Error checking chat existence: {e}")
        return False