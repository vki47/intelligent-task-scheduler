"""Core DSA building blocks and scheduling strategy helpers."""

from collections import deque

from .c_core_adapter import simulate_strategy as c_simulate_strategy


STRATEGY_COMPLEXITY = {
    'priority': {
        'name': 'Priority Scheduling',
        'data_structure': 'Min-Heap (Priority Queue)',
        'insert': 'O(log n)',
        'remove': 'O(log n)',
        'peek': 'O(1)',
    },
    'fifo': {
        'name': 'FIFO Scheduling',
        'data_structure': 'Queue',
        'insert': 'O(1)',
        'remove': 'O(1)',
        'peek': 'O(1)',
    },
    'lifo': {
        'name': 'LIFO Scheduling',
        'data_structure': 'Stack',
        'insert': 'O(1)',
        'remove': 'O(1)',
        'peek': 'O(1)',
    },
}


class PriorityQueue:
    """Priority Queue (Min-Heap) implementation."""

    def __init__(self):
        self.heap = []

    def parent(self, index):
        return (index - 1) // 2

    def left_child(self, index):
        return 2 * index + 1

    def right_child(self, index):
        return 2 * index + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def heapify_up(self, index):
        if index == 0:
            return
        parent = self.parent(index)
        if self.heap[parent].priority_score > self.heap[index].priority_score:
            self.swap(parent, index)
            self.heapify_up(parent)

    def heapify_down(self, index):
        left = self.left_child(index)
        right = self.right_child(index)
        smallest = index

        if left < len(self.heap) and self.heap[left].priority_score < self.heap[smallest].priority_score:
            smallest = left
        if right < len(self.heap) and self.heap[right].priority_score < self.heap[smallest].priority_score:
            smallest = right
        if smallest != index:
            self.swap(index, smallest)
            self.heapify_down(smallest)

    def enqueue(self, task):
        self.heap.append(task)
        self.heapify_up(len(self.heap) - 1)

    def dequeue(self):
        if self.is_empty():
            return None
        min_task = self.heap[0]
        last = self.heap.pop()
        if self.heap:
            self.heap[0] = last
            self.heapify_down(0)
        return min_task

    def peek(self):
        return None if self.is_empty() else self.heap[0]

    def is_empty(self):
        return len(self.heap) == 0

    def size(self):
        return len(self.heap)

    def remove(self, task_id):
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
        tasks = list(self.heap)
        self.heap = []
        for task in tasks:
            self.enqueue(task)

    def to_array(self):
        return sorted(self.heap, key=lambda t: t.priority_score)

    def as_tree_nodes(self):
        """Return heap entries in array/tree order for visualization."""
        return list(self.heap)


class Stack:
    """Stack implementation."""

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        return None if self.is_empty() else self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def clear(self):
        self.items = []

    def to_array(self):
        return list(self.items)


class Queue:
    """Queue implementation."""

    def __init__(self):
        self.items = deque()

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.popleft()

    def front(self):
        return None if self.is_empty() else self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def clear(self):
        self.items = deque()

    def to_array(self):
        return list(self.items)

    def remove(self, item_id):
        for index, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[index]
                return True
        return False


class ListNode:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """Linked List implementation for task history."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def append(self, data):
        new_node = ListNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1
        return new_node

    def prepend(self, data):
        new_node = ListNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.length += 1
        return new_node

    def remove(self, data_id):
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

    def to_array(self):
        result, current = [], self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def size(self):
        return self.length

    def is_empty(self):
        return self.length == 0

    def clear(self):
        self.head = self.tail = None
        self.length = 0


def simulate_strategy(strategy, tasks):
    """Simulate completion order and average wait time for a strategy."""
    return c_simulate_strategy(strategy, tasks)
