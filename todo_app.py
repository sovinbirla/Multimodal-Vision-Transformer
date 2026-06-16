"""
To-Do List Application with Local Storage
A simple yet powerful CLI-based to-do list manager with persistent storage
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import sys


class TodoItem:
    """Represents a single to-do item"""
    
    def __init__(self, title: str, description: str = "", priority: str = "medium", item_id: Optional[int] = None):
        self.id = item_id or int(datetime.now().timestamp() * 1000)
        self.title = title
        self.description = description
        self.priority = priority  # low, medium, high
        self.completed = False
        self.created_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'completed': self.completed,
            'created_at': self.created_at,
            'completed_at': self.completed_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'TodoItem':
        """Create TodoItem from dictionary"""
        item = TodoItem(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            item_id=data['id']
        )
        item.completed = data.get('completed', False)
        item.created_at = data.get('created_at', datetime.now().isoformat())
        item.completed_at = data.get('completed_at')
        return item
    
    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        priority_icon = {"low": "▼", "medium": "●", "high": "▲"}[self.priority]
        return f"{status} [{priority_icon}] {self.title}"


class TodoList:
    """Main to-do list manager with local storage"""
    
    def __init__(self, storage_file: str = "todos.json"):
        self.storage_file = storage_file
        self.items: List[TodoItem] = []
        self.load()
    
    def load(self) -> None:
        """Load to-do items from local storage"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.items = [TodoItem.from_dict(item) for item in data]
                print(f"✓ Loaded {len(self.items)} to-do items from storage")
            except json.JSONDecodeError:
                print("⚠ Storage file corrupted, starting fresh")
                self.items = []
        else:
            print("📝 Starting with an empty to-do list")
    
    def save(self) -> None:
        """Save to-do items to local storage"""
        with open(self.storage_file, 'w') as f:
            json.dump([item.to_dict() for item in self.items], f, indent=2)
    
    def add_item(self, title: str, description: str = "", priority: str = "medium") -> TodoItem:
        """Add a new to-do item"""
        if not title.strip():
            raise ValueError("Title cannot be empty")
        
        item = TodoItem(title, description, priority)
        self.items.append(item)
        self.save()
        return item
    
    def remove_item(self, item_id: int) -> bool:
        """Remove a to-do item by ID"""
        original_length = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        
        if len(self.items) < original_length:
            self.save()
            return True
        return False
    
    def toggle_item(self, item_id: int) -> bool:
        """Toggle completion status of an item"""
        for item in self.items:
            if item.id == item_id:
                item.completed = not item.completed
                if item.completed:
                    item.completed_at = datetime.now().isoformat()
                else:
                    item.completed_at = None
                self.save()
                return True
        return False
    
    def update_item(self, item_id: int, title: Optional[str] = None, 
                   description: Optional[str] = None, priority: Optional[str] = None) -> bool:
        """Update an existing item"""
        for item in self.items:
            if item.id == item_id:
                if title is not None:
                    item.title = title
                if description is not None:
                    item.description = description
                if priority is not None and priority in ["low", "medium", "high"]:
                    item.priority = priority
                self.save()
                return True
        return False
    
    def get_item(self, item_id: int) -> Optional[TodoItem]:
        """Get a specific item by ID"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def get_all_items(self, filter_completed: Optional[bool] = None, 
                     filter_priority: Optional[str] = None) -> List[TodoItem]:
        """Get all items with optional filtering"""
        filtered = self.items
        
        if filter_completed is not None:
            filtered = [item for item in filtered if item.completed == filter_completed]
        
        if filter_priority is not None:
            filtered = [item for item in filtered if item.priority == filter_priority]
        
        return sorted(filtered, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x.priority])
    
    def clear_completed(self) -> int:
        """Clear all completed items"""
        original_length = len(self.items)
        self.items = [item for item in self.items if not item.completed]
        cleared = original_length - len(self.items)
        if cleared > 0:
            self.save()
        return cleared
    
    def get_stats(self) -> Dict:
        """Get statistics about the to-do list"""
        total = len(self.items)
        completed = sum(1 for item in self.items if item.completed)
        pending = total - completed
        
        high_priority = sum(1 for item in self.items if item.priority == "high" and not item.completed)
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'completion_rate': (completed / total * 100) if total > 0 else 0,
            'high_priority_pending': high_priority
        }


class TodoCLI:
    """Command-line interface for the to-do list"""
    
    def __init__(self):
        self.todo_list = TodoList()
    
    def display_menu(self) -> None:
        """Display main menu"""
        print("\n" + "="*50)
        print("📋 TO-DO LIST APPLICATION")
        print("="*50)
        print("1. View all items")
        print("2. Add new item")
        print("3. Complete/Uncomplete item")
        print("4. Update item")
        print("5. Delete item")
        print("6. View statistics")
        print("7. Clear completed items")
        print("8. Filter by priority")
        print("9. Exit")
        print("="*50)
    
    def view_items(self, pending_only: bool = False) -> None:
        """Display all items"""
        items = self.todo_list.get_all_items(filter_completed=False if pending_only else None)
        
        if not items:
            print("\n✨ No items to display")
            return
        
        print("\n" + "─"*50)
        for i, item in enumerate(items, 1):
            status = "✓ DONE" if item.completed else "○ TODO"
            priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}[item.priority]
            
            print(f"\n{i}. {item} {priority_color}")
            print(f"   ID: {item.id}")
            if item.description:
                print(f"   Description: {item.description}")
            print(f"   Created: {item.created_at}")
        print("─"*50)
    
    def add_item(self) -> None:
        """Add a new to-do item"""
        print("\n📝 Add New Item")
        title = input("Title: ").strip()
        
        if not title:
            print("⚠ Title cannot be empty")
            return
        
        description = input("Description (optional): ").strip()
        
        print("Priority: (1) Low  (2) Medium  (3) High")
        priority_choice = input("Select priority (default: medium): ").strip()
        priority_map = {"1": "low", "2": "medium", "3": "high"}
        priority = priority_map.get(priority_choice, "medium")
        
        item = self.todo_list.add_item(title, description, priority)
        print(f"✓ Added: {item.title}")
    
    def toggle_item(self) -> None:
        """Toggle item completion status"""
        self.view_items()
        try:
            item_id = int(input("\nEnter item ID to toggle: "))
            if self.todo_list.toggle_item(item_id):
                item = self.todo_list.get_item(item_id)
                status = "completed" if item.completed else "marked as pending"
                print(f"✓ Item {status}")
            else:
                print("⚠ Item not found")
        except ValueError:
            print("⚠ Invalid ID")
    
    def update_item(self) -> None:
        """Update an item"""
        self.view_items()
        try:
            item_id = int(input("\nEnter item ID to update: "))
            item = self.todo_list.get_item(item_id)
            
            if not item:
                print("⚠ Item not found")
                return
            
            print(f"\nUpdating: {item.title}")
            new_title = input("New title (press Enter to keep current): ").strip()
            new_desc = input("New description (press Enter to keep current): ").strip()
            new_priority = input("New priority - low/medium/high (press Enter to keep current): ").strip()
            
            self.todo_list.update_item(
                item_id,
                title=new_title if new_title else None,
                description=new_desc if new_desc else None,
                priority=new_priority if new_priority else None
            )
            print("✓ Item updated")
        except ValueError:
            print("⚠ Invalid ID")
    
    def delete_item(self) -> None:
        """Delete an item"""
        self.view_items()
        try:
            item_id = int(input("\nEnter item ID to delete: "))
            if self.todo_list.remove_item(item_id):
                print("✓ Item deleted")
            else:
                print("⚠ Item not found")
        except ValueError:
            print("⚠ Invalid ID")
    
    def show_stats(self) -> None:
        """Display statistics"""
        stats = self.todo_list.get_stats()
        print("\n" + "="*50)
        print("📊 STATISTICS")
        print("="*50)
        print(f"Total items: {stats['total']}")
        print(f"Completed: {stats['completed']}")
        print(f"Pending: {stats['pending']}")
        print(f"Completion rate: {stats['completion_rate']:.1f}%")
        print(f"High priority pending: {stats['high_priority_pending']}")
        print("="*50)
    
    def filter_by_priority(self) -> None:
        """Filter items by priority"""
        print("\nFilter by priority:")
        print("1. Low")
        print("2. Medium")
        print("3. High")
        
        choice = input("Select priority: ").strip()
        priority_map = {"1": "low", "2": "medium", "3": "high"}
        priority = priority_map.get(choice)
        
        if priority:
            items = self.todo_list.get_all_items(filter_priority=priority)
            if items:
                print(f"\n{priority.upper()} Priority Items:")
                for item in items:
                    print(f"  {item}")
            else:
                print(f"No {priority} priority items")
        else:
            print("⚠ Invalid choice")
    
    def run(self) -> None:
        """Run the CLI application"""
        print("\n🎉 Welcome to To-Do List Application!")
        
        while True:
            self.display_menu()
            choice = input("\nSelect an option (1-9): ").strip()
            
            if choice == "1":
                self.view_items()
            elif choice == "2":
                self.add_item()
            elif choice == "3":
                self.toggle_item()
            elif choice == "4":
                self.update_item()
            elif choice == "5":
                self.delete_item()
            elif choice == "6":
                self.show_stats()
            elif choice == "7":
                cleared = self.todo_list.clear_completed()
                print(f"✓ Cleared {cleared} completed items")
            elif choice == "8":
                self.filter_by_priority()
            elif choice == "9":
                print("\n👋 Goodbye!")
                sys.exit(0)
            else:
                print("⚠ Invalid option")


if __name__ == "__main__":
    cli = TodoCLI()
    cli.run()
