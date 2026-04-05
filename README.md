# COMP8090 Project

This repository contains two tasks for the COMP8090 Data Structures and Algorithms course.

---

## 📦 Task 1 - Smart POS

A GUI-based Point of Sale (POS) system for small retail stores, built with Python and PySide6.

**🛠️ Tech Stack:** Python 3.12, PySide6, SQLite, bcrypt, PyInstaller

**✨ Key Features:**
- Secure login with bcrypt password hashing and role-based access control (Manager / Cashier)
- Product browsing with real-time category filtering and keyword search
- Shopping cart with live stock validation and cash / card payment flows
- Automatic PDF receipt generation after every successful checkout
- Manager dashboard: product management, full transaction history, void transactions, user account management

See [Task1/README.md](Task1/README.md) for architecture, setup, and usage instructions.

---

## 📚 Task 2 - Heap & TimSort (Self-Study Report)

From-scratch Python implementations of two topics not covered in the introductory course:

| Topic | Description |
|---|---|
| MinHeap | Complete binary tree; smallest element always at root — demonstrated with K-th largest element selection (`O(n log k)`) and OS priority task scheduling |
| TimSort | Hybrid Insertion Sort + Merge Sort; default sort in Python and Java — demonstrated with stability and stress tests |

No external dependencies required — pure Python 3.6+.

See [Task2/README.md](Task2/README.md) for usage and example output.
