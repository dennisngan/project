"""
MaxHeap Data Structure Implementation
======================================
A Max Heap is a complete binary tree where each parent node is greater than
or equal to its children. The largest element is always at the root (index 0).

Heap Property:  parent >= left_child  AND  parent >= right_child

Internal representation uses a Python list (array-based):
    - Parent index:      (i - 1) // 2
    - Left child index:  2 * i + 1
    - Right child index: 2 * i + 2

Time Complexity:
    - insert():   O(log n) — appends then bubbles up
    - remove():   O(log n) — swaps root with last, then sinks down
    - peek():     O(1)     — returns root without removal
    - size():     O(1)
    - is_empty(): O(1)

Space Complexity: O(n) for storing n elements
"""


class MaxHeap:

    def __init__(self):
        """Initialize an empty heap as an internal list."""
        self.heap = []

    def _left_child(self, index):
        """Return the index of the left child of the node at 'index'."""
        return index * 2 + 1

    def _right_child(self, index):
        """Return the index of the right child of the node at 'index'."""
        return index * 2 + 2

    def _parent(self, index):
        """Return the index of the parent of the node at 'index'."""
        return (index - 1) // 2

    def _swap(self, index1, index2):
        """Swap two elements in the heap by their indices."""
        self.heap[index1], self.heap[index2] = self.heap[index2], self.heap[index1]

    def _sink_down(self, index):
        """
        Restore the heap property by moving a node DOWN the tree.
        Called after removal when the last element is placed at the root.
        Repeatedly swaps the node with its largest child until the
        max-heap property is satisfied.
        """
        max_index = index
        while True:
            left_index = self._left_child(index)
            right_index = self._right_child(index)

            # Check if left child exists and is greater than current max
            if left_index < len(self.heap) and self.heap[left_index] > self.heap[max_index]:
                max_index = left_index

            # Check if right child exists and is greater than current max
            if right_index < len(self.heap) and self.heap[right_index] > self.heap[max_index]:
                max_index = right_index

            # If a larger child was found, swap and continue sinking
            if max_index != index:
                self._swap(max_index, index)
                index = max_index
            else:
                # Heap property is restored; stop
                return

    def insert(self, value):
        """
        Insert a new value into the heap.
        Steps:
            1. Append the value to the end of the list.
            2. Bubble UP: compare with parent and swap if larger,
               repeating until the heap property is restored.
        """
        self.heap.append(value)
        current = len(self.heap) - 1

        # Bubble up while current node is greater than its parent
        while current > 0 and self.heap[current] > self.heap[self._parent(current)]:
            self._swap(current, self._parent(current))
            current = self._parent(current)

    def remove(self):
        """
        Remove and return the maximum value (root) from the heap.
        Steps:
            1. Save the root value (the maximum).
            2. Move the last element to the root position.
            3. Sink DOWN: restore the heap property from the root.
        Returns None if the heap is empty.
        """
        if len(self.heap) == 0:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        max_value = self.heap[0]
        # Replace root with the last element and shrink the heap
        self.heap[0] = self.heap.pop()
        # Restore heap property from the root downward
        self._sink_down(0)

        return max_value

    def peek(self):
        """Return the maximum value without removing it. Returns None if empty."""
        if len(self.heap) == 0:
            return None
        return self.heap[0]

    def size(self):
        """Return the number of elements in the heap."""
        return len(self.heap)

    def is_empty(self):
        """Return True if the heap contains no elements."""
        return len(self.heap) == 0


if __name__ == '__main__':

    print("=" * 60)
    print("       MaxHeap — Demonstration and Test Cases")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Test 1: Building a heap by inserting elements one by one
    # ------------------------------------------------------------------
    print("\n--- Test 1: Insert elements into the MaxHeap ---")
    max_heap = MaxHeap()
    values = [95, 75, 80, 55, 60, 50, 65]
    for v in values:
        max_heap.insert(v)
        print(f"  Inserted {v:>3}  ->  heap = {max_heap.heap}")

    print(f"\n  Final heap after all inserts : {max_heap.heap}")
    print(f"  Peek (max element)           : {max_heap.peek()}")
    print(f"  Heap size                    : {max_heap.size()}")

    # ------------------------------------------------------------------
    # Test 2: Removing elements (always removes the maximum)
    # ------------------------------------------------------------------
    print("\n--- Test 2: Remove elements from the MaxHeap ---")
    removed1 = max_heap.remove()
    print(f"  Removed: {removed1}  ->  heap = {max_heap.heap}")

    removed2 = max_heap.remove()
    print(f"  Removed: {removed2}  ->  heap = {max_heap.heap}")

    removed3 = max_heap.remove()
    print(f"  Removed: {removed3}  ->  heap = {max_heap.heap}")

    # ------------------------------------------------------------------
    # Test 3: Drain the entire heap to get a sorted (descending) output
    # ------------------------------------------------------------------
    print("\n--- Test 3: Drain heap to get descending order ---")
    max_heap2 = MaxHeap()
    for v in [30, 10, 50, 40, 20]:
        max_heap2.insert(v)
    print(f"  Heap before drain: {max_heap2.heap}")

    sorted_desc = []
    while not max_heap2.is_empty():
        sorted_desc.append(max_heap2.remove())
    print(f"  Drained output   : {sorted_desc}")

    # ------------------------------------------------------------------
    # Test 4: Edge cases
    # ------------------------------------------------------------------
    print("\n--- Test 4: Edge cases ---")
    empty_heap = MaxHeap()
    print(f"  Remove from empty heap : {empty_heap.remove()}")
    print(f"  Peek on empty heap     : {empty_heap.peek()}")
    print(f"  Is empty?              : {empty_heap.is_empty()}")

    empty_heap.insert(42)
    print(f"  After inserting 42     : peek = {empty_heap.peek()}, size = {empty_heap.size()}")
    print(f"  Remove single element  : {empty_heap.remove()}")
    print(f"  Is empty after remove? : {empty_heap.is_empty()}")

    # ------------------------------------------------------------------
    # Test 5: Practical application — priority task scheduler
    # ------------------------------------------------------------------
    print("\n--- Test 5: Application — Priority Task Scheduler ---")
    print("  (Higher number = higher priority)\n")
    task_heap = MaxHeap()
    tasks = {
        10: "Low: Clean desk",
        50: "Medium: Review code",
        90: "Critical: Fix server crash",
        30: "Low: Update docs",
        70: "High: Deploy release"
    }

    for priority, desc in tasks.items():
        task_heap.insert(priority)
        print(f"  Added [{priority:>3}] {desc}")

    print()
    while not task_heap.is_empty():
        p = task_heap.remove()
        print(f"  Processing [{p:>3}] {tasks[p]}")

    print("\n" + "=" * 60)
    print("  All tests complete.")
    print("=" * 60)

    """
    EXPECTED OUTPUT:
    ================

    ============================================================
           MaxHeap — Demonstration and Test Cases
    ============================================================

    --- Test 1: Insert elements into the MaxHeap ---
      Inserted  95  ->  heap = [95]
      Inserted  75  ->  heap = [95, 75]
      Inserted  80  ->  heap = [95, 75, 80]
      Inserted  55  ->  heap = [95, 75, 80, 55]
      Inserted  60  ->  heap = [95, 75, 80, 55, 60]
      Inserted  50  ->  heap = [95, 75, 80, 55, 60, 50]
      Inserted  65  ->  heap = [95, 75, 80, 55, 60, 50, 65]

      Final heap after all inserts : [95, 75, 80, 55, 60, 50, 65]
      Peek (max element)           : 95
      Heap size                    : 7

    --- Test 2: Remove elements from the MaxHeap ---
      Removed: 95  ->  heap = [80, 75, 65, 55, 60, 50]
      Removed: 80  ->  heap = [75, 60, 65, 55, 50]
      Removed: 75  ->  heap = [65, 60, 50, 55]

    --- Test 3: Drain heap to get descending order ---
      Heap before drain: [50, 40, 30, 10, 20]
      Drained output   : [50, 40, 30, 20, 10]

    --- Test 4: Edge cases ---
      Remove from empty heap : None
      Peek on empty heap     : None
      Is empty?              : True
      After inserting 42     : peek = 42, size = 1
      Remove single element  : 42
      Is empty after remove? : True

    --- Test 5: Application — Priority Task Scheduler ---
      (Higher number = higher priority)

      Added [ 10] Low: Clean desk
      Added [ 50] Medium: Review code
      Added [ 90] Critical: Fix server crash
      Added [ 30] Low: Update docs
      Added [ 70] High: Deploy release

      Processing [ 90] Critical: Fix server crash
      Processing [ 70] High: Deploy release
      Processing [ 50] Medium: Review code
      Processing [ 30] Low: Update docs
      Processing [ 10] Low: Clean desk

    ============================================================
      All tests complete.
    ============================================================
    """
