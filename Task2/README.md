# 🏔️ Heap & TimSort

A from-scratch Python implementation of the **Heap** data structure (MaxHeap & MinHeap) and the **TimSort** sorting algorithm.

> **Self-Study Report — 8090SEF**

## 📁 Project Structure

```
Task2/
├── README.md          
├── max_heap.py        # MaxHeap implementation with test cases
├── min_heap.py        # MinHeap implementation with test cases
└── timsort.py         # TimSort implementation with test cases
```

---

## 🚀 Usage

No dependencies — pure Python 3.6+. Run each file directly:

```bash
python max_heap.py   # MaxHeap demo + priority task scheduler
python min_heap.py   # MinHeap demo + K-th smallest element selection
python timsort.py    # TimSort demo + stability & stress tests
```

---

## 📸 Example Output

### 🔺 MaxHeap — Priority Task Scheduler

```
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
```

### 🔻 MinHeap — K-th Smallest Element Selection

```
  Dataset: [47, 12, 85, 33, 6, 91, 23, 58, 74, 39]

  Finding k=1 smallest:
    Remove #1: 6
  -> The 1-th smallest element is 6

  Finding k=3 smallest:
    Remove #1: 6
    Remove #2: 12
    Remove #3: 23
  -> The 3-th smallest element is 23
```

### ⚡ TimSort — Stability Test

```
  Before: [(3, 'A'), (1, 'B'), (2, 'C'), (1, 'D'), (3, 'E'), (2, 'F')]
  After : [(1, 'B'), (1, 'D'), (2, 'C'), (2, 'F'), (3, 'A'), (3, 'E')]
  Note: (1,'B') comes before (1,'D'), and (3,'A') before (3,'E')
        — original order is preserved for equal keys (stable).
```

---

## 📚 References

Peters, T. (2002). *listsort.txt* [Source code documentation]. CPython repository

Auger, N., Jugé, V., Nicaud, C., & Pivoteau, C. (2018). On the worst-case complexity of TimSort. In *26th Annual European Symposium on Algorithms (ESA 2018)*, Article 4. Schloss Dagstuhl–Leibniz-Zentrum für Informatik. https://doi.org/10.4230/LIPIcs.ESA.2018.4

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to algorithms* (4th ed.). MIT Press.

GeeksforGeeks. (n.d.). *Heap data structure*. Retrieved March 8, 2026, from https://www.geeksforgeeks.org/heap-data-structure/

GeeksforGeeks. (n.d.). *TimSort: Data structures and algorithms*. Retrieved March 8, 2026, from https://www.geeksforgeeks.org/timsort/

---
