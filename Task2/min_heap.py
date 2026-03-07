"""
MinHeap Data Structure Implementation
======================================
A Min Heap is a complete binary tree where each parent node is less than
or equal to its children. The smallest element is always at the root (index 0).

Heap Property:  parent <= left_child  AND  parent <= right_child

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

class MinHeap:
    def __init__(self):
        """Initialise an empty heap as an internal list."""
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
        Repeatedly swaps the node with its smallest child until the
        min-heap property is satisfied.
        """
        min_index = index
        while True:
            left_index = self._left_child(index)
            right_index = self._right_child(index)

            # Check if left child exists and is smaller than current min
            if left_index < len(self.heap) and self.heap[left_index] < self.heap[min_index]:
                min_index = left_index

            # Check if right child exists and is smaller than current min
            if right_index < len(self.heap) and self.heap[right_index] < self.heap[min_index]:
                min_index = right_index

            # If a smaller child was found, swap and continue sinking
            if min_index != index:
                self._swap(min_index, index)
                index = min_index
            else:
                # Heap property is restored; stop
                return

    def insert(self, value):
        """
        Insert a new value into the heap.
        Steps:
            1. Append the value to the end of the list.
            2. Bubble UP: compare with parent and swap if smaller,
               repeating until the heap property is restored.
        """
        self.heap.append(value)
        current = len(self.heap) - 1

        # Bubble up while current node is smaller than its parent
        while current > 0 and self.heap[current] < self.heap[self._parent(current)]:
            self._swap(current, self._parent(current))
            current = self._parent(current)

    def remove(self):
        """
        Remove and return the minimum value (root) from the heap.
        Steps:
            1. Save the root value (the minimum).
            2. Move the last element to the root position.
            3. Sink DOWN: restore the heap property from the root.
        Returns None if the heap is empty.
        """
        if len(self.heap) == 0:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        min_value = self.heap[0]
        # Replace root with the last element and shrink the heap
        self.heap[0] = self.heap.pop()
        # Restore heap property from the root downward
        self._sink_down(0)

        return min_value

    def peek(self):
        """Return the minimum value without removing it. Returns None if empty."""
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
    print("       MinHeap — Demonstration and Test Cases")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Test 1: Building a heap by inserting elements one by one
    # ------------------------------------------------------------------
    print("\n--- Test 1: Insert elements into the MinHeap ---")
    min_heap = MinHeap()
    values = [95, 75, 80, 55, 60, 50, 65]
    for v in values:
        min_heap.insert(v)
        print(f"  Inserted {v:>3}  ->  heap = {min_heap.heap}")

    print(f"\n  Final heap after all inserts : {min_heap.heap}")
    print(f"  Peek (min element)           : {min_heap.peek()}")
    print(f"  Heap size                    : {min_heap.size()}")

    # ------------------------------------------------------------------
    # Test 2: Removing elements (always removes the minimum)
    # ------------------------------------------------------------------
    print("\n--- Test 2: Remove elements from the MinHeap ---")
    removed1 = min_heap.remove()
    print(f"  Removed: {removed1}  ->  heap = {min_heap.heap}")

    removed2 = min_heap.remove()
    print(f"  Removed: {removed2}  ->  heap = {min_heap.heap}")

    removed3 = min_heap.remove()
    print(f"  Removed: {removed3}  ->  heap = {min_heap.heap}")

    # ------------------------------------------------------------------
    # Test 3: Drain the entire heap to get a sorted (ascending) output
    # ------------------------------------------------------------------
    print("\n--- Test 3: Drain heap to get ascending order ---")
    min_heap2 = MinHeap()
    for v in [30, 10, 50, 40, 20]:
        min_heap2.insert(v)
    print(f"  Heap before drain: {min_heap2.heap}")

    sorted_asc = []
    while not min_heap2.is_empty():
        sorted_asc.append(min_heap2.remove())
    print(f"  Drained output   : {sorted_asc}")

    # ------------------------------------------------------------------
    # Test 4: Edge cases
    # ------------------------------------------------------------------
    print("\n--- Test 4: Edge cases ---")
    empty_heap = MinHeap()
    print(f"  Remove from empty heap : {empty_heap.remove()}")
    print(f"  Peek on empty heap     : {empty_heap.peek()}")
    print(f"  Is empty?              : {empty_heap.is_empty()}")

    empty_heap.insert(42)
    print(f"  After inserting 42     : peek = {empty_heap.peek()}, size = {empty_heap.size()}")
    print(f"  Remove single element  : {empty_heap.remove()}")
    print(f"  Is empty after remove? : {empty_heap.is_empty()}")

    # ------------------------------------------------------------------
    # Test 5: Practical application — K-th smallest element selection
    # ------------------------------------------------------------------
    # Finding the k-th smallest element in an unsorted list is a classic
    # use case for a MinHeap.  Insert all elements into the heap, then
    # call remove() exactly k times.  The last removed value is the
    # k-th smallest.
    #
    # Time complexity: O(n log n) for n insertions + O(k log n) for
    # k removals = O((n + k) log n).  For small k this is efficient
    # and avoids fully sorting the data.
    # ------------------------------------------------------------------
    print("\n--- Test 5: Application — K-th Smallest Element Selection ---")

    dataset = [47, 12, 85, 33, 6, 91, 23, 58, 74, 39]
    print(f"  Dataset: {dataset}\n")


    def find_kth_smallest(data, k):
        """
        Use a MinHeap to find the k-th smallest element.
        Insert all values, then remove k times — the k-th removal
        is the k-th smallest element.
        """
        heap = MinHeap()
        for val in data:
            heap.insert(val)

        result = None
        for i in range(1, k + 1):
            result = heap.remove()
            print(f"    Remove #{i}: {result}")
        return result


    for k in [1, 3, 5, len(dataset)]:
        print(f"  Finding k={k} smallest:")
        answer = find_kth_smallest(dataset, k)
        print(f"  -> The {k}-th smallest element is {answer}\n")

    print("\n" + "=" * 60)
    print("  All tests complete.")
    print("=" * 60)

    """
    EXPECTED OUTPUT:
    ================

    ============================================================
           MinHeap — Demonstration and Test Cases
    ============================================================

    --- Test 1: Insert elements into the MinHeap ---
      Inserted  95  ->  heap = [95]
      Inserted  75  ->  heap = [75, 95]
      Inserted  80  ->  heap = [75, 95, 80]
      Inserted  55  ->  heap = [55, 75, 80, 95]
      Inserted  60  ->  heap = [55, 60, 80, 95, 75]
      Inserted  50  ->  heap = [50, 60, 55, 95, 75, 80]
      Inserted  65  ->  heap = [50, 60, 55, 95, 75, 80, 65]

      Final heap after all inserts : [50, 60, 55, 95, 75, 80, 65]
      Peek (min element)           : 50
      Heap size                    : 7

    --- Test 2: Remove elements from the MinHeap ---
      Removed: 50  ->  heap = [55, 60, 65, 95, 75, 80]
      Removed: 55  ->  heap = [60, 75, 65, 95, 80]
      Removed: 60  ->  heap = [65, 75, 80, 95]

    --- Test 3: Drain heap to get ascending order ---
      Heap before drain: [10, 20, 50, 40, 30]
      Drained output   : [10, 20, 30, 40, 50]

    --- Test 4: Edge cases ---
      Remove from empty heap : None
      Peek on empty heap     : None
      Is empty?              : True
      After inserting 42     : peek = 42, size = 1
      Remove single element  : 42
      Is empty after remove? : True

    --- Test 5: Application — K-th Smallest Element Selection ---
      Dataset: [47, 12, 85, 33, 6, 91, 23, 58, 74, 39]

      Finding k=1 smallest:
        Remove #1: 6
      -> The 1-th smallest element is 6

      Finding k=3 smallest:
        Remove #1: 6
        Remove #2: 12
        Remove #3: 23
      -> The 3-th smallest element is 23

      Finding k=5 smallest:
        Remove #1: 6
        Remove #2: 12
        Remove #3: 23
        Remove #4: 33
        Remove #5: 39
      -> The 5-th smallest element is 39

      Finding k=10 smallest:
        Remove #1: 6
        Remove #2: 12
        Remove #3: 23
        Remove #4: 33
        Remove #5: 39
        Remove #6: 47
        Remove #7: 58
        Remove #8: 74
        Remove #9: 85
        Remove #10: 91
      -> The 10-th smallest element is 91

    ============================================================
      All tests complete.
    ============================================================
    """
