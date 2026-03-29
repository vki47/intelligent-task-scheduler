"""
Core Data Structures: PriorityQueue, Stack, Queue, LinkedList
"""


class PriorityQueue:
    """
    Priority Queue (Min-Heap) implementation
    Used to efficiently retrieve the task with the highest priority (lowest score)
    """
    
    def __init__(self):
        self.heap = []
    
    def parent(self, index):
        """Get parent index"""
        return (index - 1) // 2
    
    def left_child(self, index):
        """Get left child index"""
        return 2 * index + 1
    
    def right_child(self, index):
        """Get right child index"""
        return 2 * index + 2
    
    def swap(self, i, j):
        """Swap two elements in the heap"""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def heapify_up(self, index):
        """Heapify up - maintain min-heap property when inserting"""
        if index == 0:
            return
        
        parent = self.parent(index)
        if self.heap[parent].priority_score > self.heap[index].priority_score:
            self.swap(parent, index)
            self.heapify_up(parent)
    
    def heapify_down(self, index):
        """Heapify down - maintain min-heap property when removing"""
        left = self.left_child(index)
        right = self.right_child(index)
        smallest = index
        
        if left < len(self.heap) and \
           self.heap[left].priority_score < self.heap[smallest].priority_score:
            smallest = left
        
        if right < len(self.heap) and \
           self.heap[right].priority_score < self.heap[smallest].priority_score:
            smallest = right
        
        if smallest != index:
            self.swap(index, smallest)
            self.heapify_down(smallest)
    
    def enqueue(self, task):
        """Insert a task into the priority queue"""
        self.heap.append(task)
        self.heapify_up(len(self.heap) - 1)
    
    def dequeue(self):
        """Remove and return the task with the highest priority (lowest score)"""
        if self.is_empty():
            return None
        
        min_task = self.heap[0]
        last = self.heap.pop()
        
        if len(self.heap) > 0:
            self.heap[0] = last
            self.heapify_down(0)
        
        return min_task
    
    def peek(self):
        """Peek at the highest priority task without removing it"""
        return None if self.is_empty() else self.heap[0]
    
    def is_empty(self):
        """Check if the queue is empty"""
        return len(self.heap) == 0
    
    def size(self):
        """Get the size of the queue"""
        return len(self.heap)
    
    def remove(self, task_id):
        """Remove a specific task by ID"""
        index = next((i for i, task in enumerate(self.heap) if task.id == task_id), -1)
        if index == -1:
            return False
        
        last = self.heap.pop()
        if index == len(self.heap):
            return True
        
        self.heap[index] = last
        self.heapify_down(index)
        self.heapify_up(index)
        return True
    
    def rebuild(self):
        """Rebuild the heap (useful after updating priorities)"""
        tasks = list(self.heap)
        self.heap = []
        for task in tasks:
            self.enqueue(task)
    
    def to_array(self):
        """Get all tasks as an array (sorted by priority)"""
        return sorted(self.heap, key=lambda t: t.priority_score)


class Stack:
    """Stack implementation for undo/redo functionality"""
    
    def __init__(self):
        self.items = []
    
    def push(self, item):
        """Push an item onto the stack"""
        self.items.append(item)
    
    def pop(self):
        """Pop an item from the stack"""
        if self.is_empty():
            return None
        return self.items.pop()
    
    def peek(self):
        """Peek at the top item without removing it"""
        return None if self.is_empty() else self.items[-1]
    
    def is_empty(self):
        """Check if the stack is empty"""
        return len(self.items) == 0
    
    def size(self):
        """Get the size of the stack"""
        return len(self.items)
    
    def clear(self):
        """Clear the stack"""
        self.items = []
    
    def to_array(self):
        """Get all items as an array"""
        return list(self.items)


class Queue:
    """Queue implementation for work sessions"""
    
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        """Enqueue an item (add to rear)"""
        self.items.append(item)
    
    def dequeue(self):
        """Dequeue an item (remove from front)"""
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def front(self):
        """Peek at the front item without removing it"""
        return None if self.is_empty() else self.items[0]
    
    def is_empty(self):
        """Check if the queue is empty"""
        return len(self.items) == 0
    
    def size(self):
        """Get the size of the queue"""
        return len(self.items)
    
    def clear(self):
        """Clear the queue"""
        self.items = []
    
    def to_array(self):
        """Get all items as an array"""
        return list(self.items)
    
    def remove(self, item_id):
        """Remove a specific item by ID"""
        index = next((i for i, item in enumerate(self.items) if item.id == item_id), -1)
        if index != -1:
            self.items.pop(index)
            return True
        return False


class ListNode:
    """Linked List Node"""
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """Linked List implementation for task history"""
    
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0
    
    def append(self, data):
        """Append a node to the end of the list"""
        new_node = ListNode(data)
        
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        
        self.length += 1
        return new_node
    
    def prepend(self, data):
        """Prepend a node to the beginning of the list"""
        new_node = ListNode(data)
        
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        
        self.length += 1
        return new_node
    
    def remove(self, data_id):
        """Remove a node by data ID"""
        if not self.head:
            return False
        
        if self.head.data.get('id') == data_id:
            self.head = self.head.next
            if not self.head:
                self.tail = None
            self.length -= 1
            return True
        
        current = self.head
        while current.next:
            if current.next.data.get('id') == data_id:
                current.next = current.next.next
                if not current.next:
                    self.tail = current
                self.length -= 1
                return True
            current = current.next
        
        return False
    
    def find(self, data_id):
        """Find a node by data ID"""
        current = self.head
        while current:
            if current.data.get('id') == data_id:
                return current.data
            current = current.next
        return None
    
    def to_array(self):
        """Get all nodes as an array"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def size(self):
        """Get the size of the list"""
        return self.length
    
    def is_empty(self):
        """Check if the list is empty"""
        return self.length == 0
    
    def clear(self):
        """Clear the list"""
        self.head = None
        self.tail = None
        self.length = 0

