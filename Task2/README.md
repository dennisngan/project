# 🏔️ Heap & TimSort

A from-scratch Python implementation of the **MinHeap** data structure and the **TimSort** sorting algorithm.

## 📁 Project Structure

```
Task2/
├── README.md          
├── min_heap.py        # MinHeap implementation with test cases
└── timsort.py         # TimSort implementation with test cases
```

---

## 🚀 Usage

No dependencies — pure Python 3.6+. Run each file directly:

```bash
python min_heap.py   # MinHeap demo + K-th largest element selection + OS priority scheduler
python timsort.py    # TimSort demo + stability & stress tests
```

---

## 📸 Example Output

### 🔻 MinHeap

#### Test 1 — Insert elements

```
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
```

#### Test 2 — Remove elements

```
  Removed: 50  ->  heap = [55, 60, 65, 95, 75, 80]
  Removed: 55  ->  heap = [60, 75, 65, 95, 80]
  Removed: 60  ->  heap = [65, 75, 80, 95]
```

#### Test 3 — Drain heap (ascending order)

```
  Heap before drain: [10, 20, 50, 40, 30]
  Drained output   : [10, 20, 30, 40, 50]
```

#### Test 4 — Edge cases

```
  Remove from empty heap : None
  Peek on empty heap     : None
  Is empty?              : True
  After inserting 42     : peek = 42, size = 1
  Remove single element  : 42
  Is empty after remove? : True
```

#### Test 5 — Application: K-th Largest Element Selection

```
  Dataset: [47, 12, 85, 33, 6, 91, 23, 58, 74, 39]

  Finding k=1 largest  ->  1-th largest element is 91
  Finding k=3 largest  ->  3-th largest element is 74
  Finding k=5 largest  ->  5-th largest element is 47
  Finding k=10 largest ->  10-th largest element is 6
```

#### Test 6 — Application: OS Priority Task Scheduler

```
  Added [ 90] Idle:     Background log rotation
  Added [ 80] Low:      Disk defragmentation
  Added [ 10] Critical: Hardware interrupt handler
  Added [ 50] Medium:   File system sync
  Added [ 20] High:     I/O device request

  Processing [ 10] Critical: Hardware interrupt handler
  Processing [ 20] High:     I/O device request
  Processing [ 50] Medium:   File system sync
  Processing [ 80] Low:      Disk defragmentation
  Processing [ 90] Idle:     Background log rotation
```

---

### ⚡ TimSort

#### Test 1 — Basic unsorted list

```
  Before: [38, 27, 43, 3, 9, 82, 10]
  After : [3, 9, 10, 27, 38, 43, 82]
```

#### Test 2 — Already sorted list (best case)

```
  Before: [1, 2, 3, 4, 5, 6, 7, 8]
  After : [1, 2, 3, 4, 5, 6, 7, 8]
```

#### Test 3 — Reverse sorted list

```
  Before: [50, 40, 30, 20, 10]
  After : [10, 20, 30, 40, 50]
```

#### Test 4 — Duplicates

```
  Before: [5, 3, 8, 3, 5, 1, 8, 1]
  After : [1, 1, 3, 3, 5, 5, 8, 8]
```

#### Test 5 — Edge cases (single element & empty list)

```
  Single element before: [42]
  Single element after : [42]
  Empty list before    : []
  Empty list after     : []
```

#### Test 6 — Larger dataset (500 elements) stress test

```
  Before (first 30): [241, 94, 373, 297, 156, 103, 455, 371, 210, 388, ...] ...
  After  (first 30): [1, 1, 2, 3, 6, 8, 10, 13, 14, 15, 16, 20, 20, 21, 24, ...] ...
  Correctly sorted?  True
```

#### Test 7 — Stability: equal keys keep original order

```
  Before: [(3, 'A'), (1, 'B'), (2, 'C'), (1, 'D'), (3, 'E'), (2, 'F')]
  After : [(1, 'B'), (1, 'D'), (2, 'C'), (2, 'F'), (3, 'A'), (3, 'E')]
  Note: (1,'B') comes before (1,'D'), and (3,'A') before (3,'E')
        — original order is preserved for equal keys (stable).
```

#### Test 8 — Application: Sort students by grade

```
  Sorted by grade (ascending):
    Charlie    — 78
    Frank      — 78
    Alice      — 85
    Eve        — 88
    Bob        — 92
    Diana      — 95
```

---

## 📚 References

Peters, T. (2002). *listsort.txt* [Source code documentation]. CPython repository

Auger, N., Jugé, V., Nicaud, C., & Pivoteau, C. (2018). On the worst-case complexity of TimSort. In *26th Annual European Symposium on Algorithms (ESA 2018)*, Article 4. Schloss Dagstuhl–Leibniz-Zentrum für Informatik. https://doi.org/10.4230/LIPIcs.ESA.2018.4

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to algorithms* (4th ed.). MIT Press.

GeeksforGeeks. (n.d.). *Heap data structure*. Retrieved March 8, 2026, from https://www.geeksforgeeks.org/heap-data-structure/

GeeksforGeeks. (n.d.). *TimSort: Data structures and algorithms*. Retrieved March 8, 2026, from https://www.geeksforgeeks.org/timsort/

---
