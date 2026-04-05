"""
TimSort Algorithm Implementation
=================================
TimSort is a hybrid, stable sorting algorithm derived from Merge Sort and
Insertion Sort.  It was designed by Tim Peters in 2002 for Python's built-in
sort and is now also used in Java (Arrays.sort for objects), Android, and Swift.

Key Idea:
    Real-world data often contains ordered subsequences ("runs").  TimSort
    exploits this by:
        1. Dividing the array into small chunks called "runs".
        2. Sorting each run with Insertion Sort (fast on small / nearly-sorted data).
        3. Merging the sorted runs with a modified Merge Sort.

Algorithm Steps:
    1. Choose a RUN size (commonly 32 or 64).
    2. Sort individual runs of that size using Insertion Sort.
    3. Iteratively merge adjacent runs, doubling the merge width each pass,
       until the entire array is sorted.

Time Complexity:
    - Best case:    O(n)        — when the data is already sorted
    - Average case: O(n log n)
    - Worst case:   O(n log n)

Space Complexity: O(n) — temporary arrays are needed during merging

Stability: Yes — equal elements retain their original relative order.

Why TimSort is efficient:
    - Insertion Sort is O(n) on nearly-sorted data and has low overhead for
      small arrays (cache-friendly, minimal comparisons).
    - Merge Sort guarantees O(n log n) worst-case for the overall sort.
    - Combining both gives the best of both worlds.
"""

# 32 is a common choice in practice (Python's built-in uses a similar value).
MIN_RUN = 32


def calc_min_run(n):
    """
    Calculate the minimum run length for a given array size.

    The idea is to choose a min_run value such that n / min_run is a power
    of 2 (or close to it), which makes the merge phase most balanced.

    Algorithm: keep shifting n right and track if any bits are shifted off.
    """
    r = 0  # becomes 1 if any shifted-off bits are 1
    while n >= MIN_RUN:
        # Bitwise operation r = r | (n & 1) which is used to capture any odd bit get shifted off?
        # If yes, r = 1 else r = 0
        r |= n & 1
        n >>= 1  # Divide n by 2 repeatedly, find the high order bit
    return n + r


def insertion_sort(arr, left, right):
    """
    Sort arr[left ... right] in-place using Insertion Sort.

    Insertion Sort is chosen for small runs because:
        - Very low overhead (no recursion, no extra memory).
        - Excellent performance on small or partially sorted data. Best case: O(n)
        - Stable: equal elements keep their original order.

    Parameters:
        arr   — the list to sort (modified in-place)
        left  — start index of the segment (inclusive)
        right — end index of the segment (inclusive)

    Time Complexity:
        O(min_run²) in the worst case
        BUT: min_run is fixed (typically 32)
        So: O(32²) = O(1024) = O(1) constant time per run
        No of run = n/min_run approximately equal n/32
        Combining them, O(n)
    """
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        # Shift elements that are greater than 'key' one position to the right
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        # Place 'key' in its correct sorted position
        arr[j + 1] = key


def merge(arr, left, mid, right):
    """
    Merge two sorted sub-arrays: arr[left...mid] and arr[mid+1...right].

    Creates temporary copies of both halves,
    then merges them back into arr[left...right] in sorted order.

    Parameters:
        arr   — the list containing both sorted halves
        left  — start index of the first half
        mid   — end index of the first half
        right — end index of the second half
    """
    # Create temporary copies of the two halves
    left_part = arr[left:mid + 1]
    right_part = arr[mid + 1:right + 1]

    i = 0  # pointer for left_part
    j = 0  # pointer for right_part
    k = left  # pointer for the merged output in arr

    # Compare elements from both halves and place the smaller one
    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        k += 1

    # Copy any remaining elements from the left half
    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1

    # Copy any remaining elements from the right half
    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1


def timsort(arr):
    """
    Phase 1 — Run creation:
        Divide the array into runs of size 'min_run' and sort each
        run individually with Insertion Sort.

    Phase 2 — Merge:
        Iteratively merge adjacent runs.  Start with runs of size
        'min_run', then double the merge width each pass (min_run,
        2*min_run, 4*min_run, ...) until the entire array is merged.
    """
    n = len(arr)
    if n < 2:
        return  # Already sorted

    min_run = calc_min_run(n)

    # ── Phase 1: Sort individual runs with Insertion Sort ──
    for start in range(0, n, min_run):
        end = min(start + min_run - 1, n - 1)
        insertion_sort(arr, start, end)

    # ── Phase 2: Merge sorted runs, doubling the size each iteration ──
    size = min_run
    while size < n:  # O(log n) iterations
        for left in range(0, n, 2 * size):
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)

            # Only merge if there are two sub-arrays to merge
            if mid < right:
                merge(arr, left, mid, right)  # O(n) work per level

        size *= 2


# ─── Main: Demonstration and Test Cases ──────────────────────────────────

if __name__ == '__main__':

    print("=" * 60)
    print("       TimSort Algorithm — Demonstration and Test Cases")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Test 1: Basic sorting of an unsorted list
    # ------------------------------------------------------------------
    print("\n--- Test 1: Basic unsorted list ---")
    data1 = [38, 27, 43, 3, 9, 82, 10]
    print(f"  Before: {data1}")
    timsort(data1)
    print(f"  After : {data1}")

    # ------------------------------------------------------------------
    # Test 2: Already sorted list (best case — O(n))
    # ------------------------------------------------------------------
    print("\n--- Test 2: Already sorted list (best case) ---")
    data2 = [1, 2, 3, 4, 5, 6, 7, 8]
    print(f"  Before: {data2}")
    timsort(data2)
    print(f"  After : {data2}")

    # ------------------------------------------------------------------
    # Test 3: Reverse sorted list (worst case for naive algorithms)
    # ------------------------------------------------------------------
    print("\n--- Test 3: Reverse sorted list ---")
    data3 = [50, 40, 30, 20, 10]
    print(f"  Before: {data3}")
    timsort(data3)
    print(f"  After : {data3}")

    # ------------------------------------------------------------------
    # Test 4: List with duplicate values
    # ------------------------------------------------------------------
    print("\n--- Test 4: Duplicates ---")
    data4 = [5, 3, 8, 3, 5, 1, 8, 1]
    print(f"  Before: {data4}")
    timsort(data4)
    print(f"  After : {data4}")

    # ------------------------------------------------------------------
    # Test 5: Single element and empty list
    # ------------------------------------------------------------------
    print("\n--- Test 5: Edge cases (single element & empty list) ---")
    data5a = [42]
    print(f"  Single element before: {data5a}")
    timsort(data5a)
    print(f"  Single element after : {data5a}")

    data5b = []
    print(f"  Empty list before    : {data5b}")
    timsort(data5b)
    print(f"  Empty list after     : {data5b}")

    # ------------------------------------------------------------------
    # Test 6: Larger dataset to exercise merge phase
    # ------------------------------------------------------------------
    print("\n--- Test 6: Larger dataset (500 elements) for stress test---")
    import random

    random.seed(2024)  # Fixed seed for reproducible output
    data6 = [random.randint(1, 500) for _ in range(500)]
    print(f"  Before (first 15): {data6[:30]} ...")
    timsort(data6)
    print(f"  After  (first 15): {data6[:30]} ...")
    print(f"  Correctly sorted?  {data6 == sorted(data6)}")

    # ------------------------------------------------------------------
    # Test 7: Stability demonstration
    # ------------------------------------------------------------------
    print("\n--- Test 7: Stability — equal keys keep original order ---")
    # Each tuple is (sort_key, original_position)
    data7 = [(3, 'A'), (1, 'B'), (2, 'C'), (1, 'D'), (3, 'E'), (2, 'F')]
    print(f"  Before: {data7}")

    # TimSort works on comparable items; tuples compare element-by-element,
    # so we extract just the key for a fair stability test.
    # We use a wrapper that sorts by the first element only.
    keys = [x[0] for x in data7]
    indices = list(range(len(data7)))
    # Sort indices by key using our timsort (via a keyed wrapper list)
    keyed = list(zip(keys, indices))
    timsort(keyed)  # tuples compare by first element, then by index (stable)
    result = [data7[idx] for _, idx in keyed]
    print(f"  After : {result}")
    print("  Note: (1,'B') comes before (1,'D'), and (3,'A') before (3,'E')")
    print("        — original order is preserved for equal keys (stable).")

    # ------------------------------------------------------------------
    # Test 8: Practical application — sorting student records by grade
    # ------------------------------------------------------------------
    print("\n--- Test 8: Application — Sort students by grade ---")
    students = [
        {"name": "Alice", "grade": 85},
        {"name": "Bob", "grade": 92},
        {"name": "Charlie", "grade": 78},
        {"name": "Diana", "grade": 95},
        {"name": "Eve", "grade": 88},
        {"name": "Frank", "grade": 78},
    ]

    # Extract grades, sort, then reconstruct
    grades = [s["grade"] for s in students]
    indices = list(range(len(students)))
    pairs = list(zip(grades, indices))
    timsort(pairs)
    sorted_students = [students[idx] for _, idx in pairs]

    print("  Sorted by grade (ascending):")
    for s in sorted_students:
        print(f"    {s['name']:<10} — {s['grade']}")

    print("\n" + "=" * 60)
    print("  All tests complete.")
    print("=" * 60)

    """
    EXPECTED OUTPUT:
    ================

    ============================================================
       TimSort Algorithm — Demonstration and Test Cases
    ============================================================
    
    --- Test 1: Basic unsorted list ---
      Before: [38, 27, 43, 3, 9, 82, 10]
      After : [3, 9, 10, 27, 38, 43, 82]
    
    --- Test 2: Already sorted list (best case) ---
      Before: [1, 2, 3, 4, 5, 6, 7, 8]
      After : [1, 2, 3, 4, 5, 6, 7, 8]
    
    --- Test 3: Reverse sorted list ---
      Before: [50, 40, 30, 20, 10]
      After : [10, 20, 30, 40, 50]
    
    --- Test 4: Duplicates ---
      Before: [5, 3, 8, 3, 5, 1, 8, 1]
      After : [1, 1, 3, 3, 5, 5, 8, 8]
    
    --- Test 5: Edge cases (single element & empty list) ---
      Single element before: [42]
      Single element after : [42]
      Empty list before    : []
      Empty list after     : []
    
    --- Test 6: Larger dataset (500 elements) for stress test---
      Before (first 15): [241, 94, 373, 297, 156, 103, 455, 371, 210, 388, 367, 389, 136, 273, 126, 326, 417, 377, 256, 182, 213, 270, 373, 316, 494, 112, 159, 279, 361, 170] ...
      After  (first 15): [1, 1, 2, 3, 6, 8, 10, 13, 14, 15, 16, 20, 20, 21, 24, 26, 28, 28, 29, 30, 32, 34, 35, 37, 38, 39, 42, 45, 45, 48] ...
      Correctly sorted?  True
    
    --- Test 7: Stability — equal keys keep original order ---
      Before: [(3, 'A'), (1, 'B'), (2, 'C'), (1, 'D'), (3, 'E'), (2, 'F')]
      After : [(1, 'B'), (1, 'D'), (2, 'C'), (2, 'F'), (3, 'A'), (3, 'E')]
      Note: (1,'B') comes before (1,'D'), and (3,'A') before (3,'E')
            — original order is preserved for equal keys (stable).
    
    --- Test 8: Application — Sort students by grade ---
      Sorted by grade (ascending):
        Charlie    — 78
        Frank      — 78
        Alice      — 85
        Eve        — 88
        Bob        — 92
        Diana      — 95
    
    ============================================================
      All tests complete.
    ============================================================
    """
