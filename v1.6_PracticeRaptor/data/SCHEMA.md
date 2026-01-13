# PracticeRaptor v1.6 - Data Schema Documentation

**Version:** 1.6
**Date:** 2024-01
**Status:** Foundation for future relational database

---

## Overview

This document describes the normalized data structure for PracticeRaptor v1.6. The JSON files in this directory represent a **normalized relational schema** that will be migrated to SQLite/PostgreSQL in future versions.

### Design Principles

1. **Normalization** - Data is split into atomic tables to avoid redundancy
2. **Separation of Concerns** - Problems, Users, and Submissions are independent
3. **Lazy Loading** - Problems split into lightweight (list) and heavyweight (details) parts
4. **Localization** - Multilingual content as separate records (not dictionaries)
5. **Statistics from Submissions** - No separate Progress table; stats computed dynamically

---

## Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PROBLEMS (Core)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐         ┌──────────────────┐      ┌─────────────────┐ │
│  │  problems   │◄───────►│ problem_selectors │      │ problem_        │ │
│  │             │         │   (metadata)      │      │ descriptions    │ │
│  │  - id       │         │  - difficulty     │      │  - complexity   │ │
│  └──────┬──────┘         │  - categories     │      └────────┬────────┘ │
│         │                │  - languages      │               │          │
│         │                └──────────────────┘                │          │
└─────────┼──────────────────────────────────────────────────┼──────────┘
          │                                                   │
          │  ┌──────────────────────────────────────────────┼──────────┐
          │  │          LOCALIZED CONTENT                    │          │
          │  ├───────────────────────────────────────────────┼──────────┤
          ├─►│  titles          (problem_id, language, text) │          │
          ├─►│  descriptions    (problem_id, language, text) │          │
          ├─►│  editorials      (problem_id, language, text) │◄─────────┤
          ├─►│  hints           (problem_id, language, text) │          │
          │  └───────────────────────────────────────────────┘          │
          │                                                              │
          │  ┌──────────────────────────────────────────────┐           │
          │  │       LANGUAGE-SPECIFIC CONTENT              │           │
          │  ├──────────────────────────────────────────────┤           │
          ├─►│  signatures         (problem_id, prog_lang)  │           │
          ├─►│  canonical_solutions (problem_id, prog_lang) │           │
          ├─►│  test_cases         (problem_id, prog_lang)  │           │
          │  └──────────────────────────────────────────────┘           │
          │                                                              │
          │  ┌──────────────────────────────────────────────┐           │
          │  │             EXAMPLES                         │           │
          │  ├──────────────────────────────────────────────┤           │
          ├─►│  examples       (example_id, problem_id)     │           │
          │  │                 (input, output)              │           │
          │  └─────────────────────┬────────────────────────┘           │
          │                        │                                    │
          │                        ├─►explanations (example_id, lang)   │
          │                                                              │
          └─►tags (problem_id, tag)                                     │
                                                                         │
┌─────────────────────────────────────────────────────────────────────────┤
│                          USERS & SETTINGS                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────┐                  ┌─────────────────┐                    │
│  │   users    │◄────────────────►│    settings     │                    │
│  │            │                  │   (user prefs)  │                    │
│  │ - id       │                  │  - language     │                    │
│  │ - name     │                  │  - prog_lang    │                    │
│  │ - email    │                  │  - editor       │                    │
│  │ - password │                  │  - filters      │                    │
│  └─────┬──────┘                  └─────────────────┘                    │
│        │                                                                 │
└────────┼─────────────────────────────────────────────────────────────────┘
         │
         │  ┌──────────────────────────────────────────────┐
         │  │          USER WORK                           │
         │  ├──────────────────────────────────────────────┤
         ├─►│  drafts      (user_id, problem_id, code)     │
         │  │              (autosave snapshots)            │
         │  └──────────────────────────────────────────────┘
         │
         │  ┌──────────────────────────────────────────────┐
         │  │      SUBMISSIONS (Source of Truth)           │
         │  ├──────────────────────────────────────────────┤
         └─►│  submissions (user_id, problem_id, code)     │
            │              (successful solutions only)     │
            │              execution_time, memory, etc.    │
            │                                              │
            │  Stats computed from this table:             │
            │   - Solved problems                          │
            │   - Languages used                           │
            │   - Best time/memory                         │
            │   - Streak                                   │
            └──────────────────────────────────────────────┘
```

---

## Tables (JSON Files)

### Problem Tables

#### 1. `problems/problems.json`
**Purpose:** Core problem registry (minimal data)

| Field | Type | Description |
|-------|------|-------------|
| problem_id | int | Primary key |

**Example:**
```json
{"problem_id": 1}
```

---

#### 2. `problems/problem_selectors.json`
**Purpose:** Metadata for filtering and problem list display

| Field | Type | Description |
|-------|------|-------------|
| problem_id | int | Foreign key → problems |
| supported_languages | array[string] | Interface languages (en, ru) |
| supported_programming_languages | array[string] | Code languages (python3, java) |
| difficulty | enum | easy, medium, hard |
| categories | array[enum] | Array, String, Hash Table, etc. |

**Example:**
```json
{
  "problem_id": 1,
  "supported_languages": ["en", "ru"],
  "supported_programming_languages": ["python3", "java"],
  "difficulty": "easy",
  "categories": ["Array", "Hash Table"]
}
```

**Usage:** Loaded for problem list, enables filtering without loading descriptions.

---

#### 3. `problems/problem_descriptions.json`
**Purpose:** Heavy metadata (loaded only for detail view)

| Field | Type | Description |
|-------|------|-------------|
| problem_id | int | Foreign key → problems |
| complexity | enum | O(n), O(log n), O(n²), etc. |

**Example:**
```json
{"problem_id": 1, "complexity": "O(n)"}
```

---

### Localized Content Tables

#### 4. `problems/titles.json`
**Purpose:** Problem titles in different languages

| Field | Type | Description |
|-------|------|-------------|
| problem_id | int | Foreign key → problems |
| language | enum | en, ru |
| title | string | Localized title |

**Example:**
```json
{"problem_id": 1, "language": "en", "title": "Two Sum"}
{"problem_id": 1, "language": "ru", "title": "Два числа"}
```

**Query Pattern:** `SELECT title WHERE problem_id=1 AND language='ru'`

---

#### 5. `problems/descriptions.json`
**Purpose:** Problem descriptions in different languages

| Field | Type | Description |
|-------|------|-------------|
| problem_id | int | Foreign key → problems |
| language | enum | en, ru |
| description | text | Full problem description |

---

#### 6. `problems/editorials.json`
**Purpose:** Solution explanations in different languages

| Field | Type | Description |
|-------|------|-------------|
| problem_id | int | Foreign key → problems |
| language | enum | en, ru |
| editorial | text | How to solve the problem |

---

#### 7. `problems/hints.json`
**Purpose:** Hints in different languages

| Field | Type | Description |
|-------|------|-------------|
| problem_id | int | Foreign key → problems |
| language | enum | en, ru |
| hint | text | Hint text |

---

### Language-Specific Content

#### 8. `problems/signatures.json`
**Purpose:** Function signatures for different programming languages

| Field | Type | Description |
|-------|------|-------------|
| problem_id | int | Foreign key → problems |
| programming_language | enum | python3, java |
| signature | string | Function signature code |

**Example:**
```json
{
  "problem_id": 1,
  "programming_language": "python3",
  "signature": "def two_sum(nums: list[int], target: int) -> list[int]:"
}
```

---

#### 9. `problems/canonical_solutions.json`
**Purpose:** Reference solutions with different approaches

| Field | Type | Description |
|-------|------|-------------|
| canonical_solution_id | int | Primary key |
| problem_id | int | Foreign key → problems |
| programming_language | enum | python3, java |
| name | string | Solution approach name |
| complexity | string | Time/space complexity |
| canonical_solution | text | Solution code |

**Example:**
```json
{
  "canonical_solution_id": 1,
  "problem_id": 1,
  "programming_language": "python3",
  "name": "Hash Map (One Pass)",
  "complexity": "O(n)",
  "canonical_solution": "def two_sum(...):\n    ..."
}
```

**Note:** Multiple solutions per problem are supported.

---

#### 10. `problems/test_cases.json`
**Purpose:** Executable test code for validation

| Field | Type | Description |
|-------|------|-------------|
| test_case_id | int | Primary key |
| problem_id | int | Foreign key → problems |
| programming_language | enum | python3, java |
| test | text | Executable test code |
| is_example | bool | True if shown in examples |

**Example:**
```json
{
  "test_case_id": 1,
  "problem_id": 1,
  "programming_language": "python3",
  "test": "assert two_sum([2, 7, 11, 15], 9) == [0, 1]",
  "is_example": true
}
```

**Execution Model:**
- Quick check: run only `is_example=true` tests
- Full submission: run all tests

---

### Examples

#### 11. `problems/examples.json`
**Purpose:** Input/output examples (language-independent)

| Field | Type | Description |
|-------|------|-------------|
| example_id | int | Primary key |
| problem_id | int | Foreign key → problems |
| input | string | Example input |
| output | string | Expected output |

**Example:**
```json
{
  "example_id": 1,
  "problem_id": 1,
  "input": "[2, 7, 11, 15], target = 9",
  "output": "[0, 1]"
}
```

---

#### 12. `problems/explanations.json`
**Purpose:** Localized explanations for examples

| Field | Type | Description |
|-------|------|-------------|
| example_id | int | Foreign key → examples |
| language | enum | en, ru |
| explanation | text | Why this output? |

---

#### 13. `problems/tags.json`
**Purpose:** Flexible tagging system (not enum)

| Field | Type | Description |
|-------|------|-------------|
| problem_id | int | Foreign key → problems |
| tag | string | Free-form tag |

**Example:**
```json
{"problem_id": 1, "tag": "array"}
{"problem_id": 1, "tag": "hash-table"}
{"problem_id": 1, "tag": "interview"}
```

**Note:** Unlike categories (enum), tags are flexible strings.

---

### User Tables

#### 14. `users/users.json`
**Purpose:** User accounts with authentication

| Field | Type | Description |
|-------|------|-------------|
| user_id | int | Primary key |
| user_name | string | Username (unique) |
| hash_password | string | Hashed password (bcrypt) |
| email | string | Email (unique) |

**Example:**
```json
{
  "user_id": 1,
  "user_name": "alexei",
  "hash_password": "$2b$12$...",
  "email": "alexei@example.com"
}
```

**Security:** Never store plain-text passwords. Use bcrypt/argon2.

---

#### 15. `users/settings.json`
**Purpose:** User preferences and session state

| Field | Type | Description |
|-------|------|-------------|
| user_id | int | Foreign key → users |
| language | enum | Interface language (en, ru) |
| programming_language | enum | Default code language |
| text_editor | enum | CLI editor preference |
| select_problem_id | int? | Currently selected problem |
| select_difficulty | enum? | Current difficulty filter |
| select_tags | array[string] | Current tag filters |
| select_category | enum? | Current category filter |
| select_status | enum? | Current status filter |

**Example:**
```json
{
  "user_id": 1,
  "language": "ru",
  "programming_language": "python3",
  "text_editor": "vim",
  "select_problem_id": null,
  "select_difficulty": "easy",
  "select_tags": ["array", "hash-table"],
  "select_category": "Array",
  "select_status": null
}
```

**Note:** `select_*` fields store current session filters.

---

### User Work Tables

#### 16. `drafts/drafts.json`
**Purpose:** Auto-saved user code (snapshots)

| Field | Type | Description |
|-------|------|-------------|
| draft_id | int | Primary key |
| user_id | int | Foreign key → users |
| problem_id | int | Foreign key → problems |
| programming_language | enum | Language used |
| code | text | User's code (incomplete) |
| created_at | timestamp | First save |
| updated_at | timestamp | Last save |

**Example:**
```json
{
  "draft_id": 1,
  "user_id": 1,
  "problem_id": 1,
  "programming_language": "python3",
  "code": "def two_sum(...):\n    # Work in progress",
  "created_at": "2024-01-15T14:20:00Z",
  "updated_at": "2024-01-15T14:35:00Z"
}
```

**Lifecycle:**
- Created: when user starts editing
- Updated: on code check, every N seconds, on exit
- Deleted: when submission succeeds (optional)

**Unique Constraint:** (user_id, problem_id, programming_language)

---

#### 17. `submissions/submissions.json`
**Purpose:** Successful solutions (source of truth for statistics)

| Field | Type | Description |
|-------|------|-------------|
| submission_id | int | Primary key |
| user_id | int | Foreign key → users |
| problem_id | int | Foreign key → problems |
| programming_language | enum | Language used |
| code | text | Accepted solution code |
| result | enum | accepted (always) |
| total_time_ms | int | Execution time |
| memory_used_kb | int | Memory used |
| created_at | timestamp | Submission date |

**Example:**
```json
{
  "submission_id": 1,
  "user_id": 1,
  "problem_id": 1,
  "programming_language": "python3",
  "code": "def two_sum(...):\n    ...",
  "result": "accepted",
  "total_time_ms": 45,
  "memory_used_kb": 14200,
  "created_at": "2024-01-15T15:30:00Z"
}
```

**Important:**
- Only successful (accepted) submissions are stored
- Failed attempts are NOT stored (no separate attempts table)
- Multiple submissions per (user, problem) allowed (different languages, improvements)

---

## Statistics Computation

**No separate Progress table!** All statistics are computed dynamically from `submissions`:

### Problem Status (per user)
```sql
-- Is problem solved?
SELECT COUNT(*) > 0 as is_solved
FROM submissions
WHERE user_id = ? AND problem_id = ?
```

### Languages Solved
```sql
-- Which languages did user solve problem in?
SELECT DISTINCT programming_language
FROM submissions
WHERE user_id = ? AND problem_id = ?
```

### Total Solved Count
```sql
-- How many problems has user solved?
SELECT COUNT(DISTINCT problem_id)
FROM submissions
WHERE user_id = ?
```

### Solved by Difficulty
```sql
-- Breakdown by difficulty
SELECT ps.difficulty, COUNT(DISTINCT s.problem_id) as count
FROM submissions s
JOIN problem_selectors ps ON s.problem_id = ps.problem_id
WHERE s.user_id = ?
GROUP BY ps.difficulty
```

### Best Time/Memory
```sql
-- Best performance for a problem
SELECT MIN(total_time_ms) as best_time, MIN(memory_used_kb) as best_memory
FROM submissions
WHERE user_id = ? AND problem_id = ?
```

### Streak Calculation
```sql
-- Days with at least one submission
SELECT DATE(created_at) as date
FROM submissions
WHERE user_id = ?
GROUP BY DATE(created_at)
ORDER BY date DESC
```
Then compute consecutive days in application code.

---

## Domain Models ↔ Tables Mapping

### Loading a Problem

**For Problem List:**
```
SELECT p.problem_id, ps.difficulty, ps.categories
FROM problems p
JOIN problem_selectors ps ON p.problem_id = ps.problem_id

SELECT t.title
FROM titles t
WHERE t.problem_id = ? AND t.language = ?

-- Check if solved (from submissions)
SELECT COUNT(*) > 0 as is_solved
FROM submissions
WHERE user_id = ? AND problem_id = ?
```

**Domain Models Created:**
- `Problem(problem_id, status=SOLVED/NOT_STARTED)`
- `ProblemSelector(difficulty, categories, ...)`
- `Title(title)`

---

**For Problem Details:**
```
-- Load description
SELECT description FROM descriptions WHERE problem_id = ? AND language = ?

-- Load examples
SELECT * FROM examples WHERE problem_id = ?
SELECT * FROM explanations WHERE example_id IN (...) AND language = ?

-- Load hints
SELECT hint FROM hints WHERE problem_id = ? AND language = ?

-- Load complexity
SELECT complexity FROM problem_descriptions WHERE problem_id = ?
```

**Domain Models Created:**
- `ProblemDescription(complexity, examples)`
- `Description(description)`
- `Example(input, output)`
- `Explanation(explanation)`
- `Hint(hint)`

---

### Creating a Solution Object

```
-- Load signature
SELECT signature FROM signatures WHERE problem_id = ? AND programming_language = ?

-- Load canonical solutions
SELECT * FROM canonical_solutions WHERE problem_id = ? AND programming_language = ?

-- Load test cases
SELECT * FROM test_cases WHERE problem_id = ? AND programming_language = ?
```

**Domain Model Created:**
```python
Solution(
    problem_id=1,
    programming_language=ProgrammingLanguage.PYTHON,
    function_signature=Signature(...),
    canonical_solutions=(CanonicalSolution(...), ...),
    code="",  # User fills this
    tests=(TestCase(...), ...),
    test_cases=(0, 1, 2)  # Indices of is_example=true tests
)
```

---

### Saving a Draft

```
INSERT INTO drafts (user_id, problem_id, programming_language, code, created_at, updated_at)
VALUES (?, ?, ?, ?, NOW(), NOW())
ON CONFLICT (user_id, problem_id, programming_language)
DO UPDATE SET code = ?, updated_at = NOW()
```

---

### Saving a Submission

```
INSERT INTO submissions (user_id, problem_id, programming_language, code, result, total_time_ms, memory_used_kb, created_at)
VALUES (?, ?, ?, ?, 'accepted', ?, ?, NOW())
```

---

## Migration to Relational Database

### SQLite Schema (Future: Stage 1.7)

```sql
CREATE TABLE problems (
    problem_id INTEGER PRIMARY KEY
);

CREATE TABLE problem_selectors (
    problem_id INTEGER PRIMARY KEY REFERENCES problems(problem_id),
    supported_languages TEXT NOT NULL,  -- JSON array
    supported_programming_languages TEXT NOT NULL,  -- JSON array
    difficulty TEXT NOT NULL CHECK(difficulty IN ('easy', 'medium', 'hard')),
    categories TEXT NOT NULL  -- JSON array
);

CREATE TABLE problem_descriptions (
    problem_id INTEGER PRIMARY KEY REFERENCES problems(problem_id),
    complexity TEXT NOT NULL
);

CREATE TABLE titles (
    problem_id INTEGER REFERENCES problems(problem_id),
    language TEXT NOT NULL CHECK(language IN ('en', 'ru')),
    title TEXT NOT NULL,
    PRIMARY KEY (problem_id, language)
);

CREATE TABLE descriptions (
    problem_id INTEGER REFERENCES problems(problem_id),
    language TEXT NOT NULL CHECK(language IN ('en', 'ru')),
    description TEXT NOT NULL,
    PRIMARY KEY (problem_id, language)
);

-- ... (similar for other tables)

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL UNIQUE,
    hash_password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE submissions (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    problem_id INTEGER NOT NULL REFERENCES problems(problem_id),
    programming_language TEXT NOT NULL,
    code TEXT NOT NULL,
    result TEXT NOT NULL DEFAULT 'accepted',
    total_time_ms INTEGER NOT NULL,
    memory_used_kb INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_submissions_user ON submissions(user_id);
CREATE INDEX idx_submissions_problem ON submissions(problem_id);
CREATE INDEX idx_submissions_user_problem ON submissions(user_id, problem_id);
```

### PostgreSQL Schema (Future: Stage 1.7+)

Similar to SQLite but with:
- Proper ENUM types instead of CHECK constraints
- JSONB for array fields
- Better indexing (GIN indexes for JSONB)
- Partitioning for submissions table (by date)

---

## File Structure Summary

```
v1.6_PracticeRaptor/data/
├── SCHEMA.md                           # This file
│
├── problems/
│   ├── problems.json                   # Core registry
│   ├── problem_selectors.json          # Filtering metadata
│   ├── problem_descriptions.json       # Heavy metadata
│   ├── titles.json                     # Localized titles
│   ├── descriptions.json               # Localized descriptions
│   ├── editorials.json                 # Localized editorials
│   ├── hints.json                      # Localized hints
│   ├── examples.json                   # Input/output examples
│   ├── explanations.json               # Localized explanations
│   ├── signatures.json                 # Function signatures
│   ├── canonical_solutions.json        # Reference solutions
│   ├── test_cases.json                 # Executable tests
│   └── tags.json                       # Flexible tags
│
├── users/
│   ├── users.json                      # User accounts
│   └── settings.json                   # User preferences
│
├── drafts/
│   └── drafts.json                     # Auto-saved code
│
└── submissions/
    └── submissions.json                # Successful solutions (stats source)
```

**Total:** 17 tables (JSON files)

---

## Key Architectural Decisions

### 1. Why Normalize Localization?
**Instead of:**
```json
{"title": {"en": "Two Sum", "ru": "Два числа"}}
```

**We use:**
```json
{"problem_id": 1, "language": "en", "title": "Two Sum"}
{"problem_id": 1, "language": "ru", "title": "Два числа"}
```

**Benefits:**
- Direct SQL queries: `WHERE language = 'ru'`
- Easy to add new languages
- Standard relational design
- Better for database indexing

### 2. Why Split Problems into 3 Parts?
- **problems** - Core registry (always loaded)
- **problem_selectors** - For list view and filtering (lightweight)
- **problem_descriptions** - For detail view (heavyweight)

**Benefits:**
- Fast list rendering (don't load descriptions)
- Efficient filtering (no need to parse heavy data)
- Scales to hundreds of problems

### 3. Why No Progress Table?
**Progress/Statistics are computed from submissions:**
- Single source of truth
- No synchronization issues
- Submissions never deleted, so history is preserved
- Easy to audit and recalculate

**Trade-off:**
- Slightly slower stats queries
- But: submissions table is small (only successful solutions)
- Caching layer can be added later if needed

### 4. Why Executable Test Code?
**Instead of:**
```json
{"input": {"nums": [2,7], "target": 9}, "expected": [0,1]}
```

**We use:**
```json
{"test": "assert two_sum([2, 7], 9) == [0, 1]"}
```

**Benefits:**
- Language-agnostic architecture
- Supports complex test logic
- No need to parse/serialize data types
- Executor microservices handle language specifics

### 5. Why Separate Tags and Categories?
- **Categories** - Fixed enum (Array, String, Tree, etc.)
- **Tags** - Flexible strings (interview, hard-to-debug, etc.)

**Benefits:**
- Categories: structured filtering
- Tags: organic growth, community tagging
- Best of both worlds

---

## Next Steps

### Stage 1.6 (Current)
- ✅ Define normalized JSON schema
- ✅ Create example data
- [ ] Implement JSON repositories
- [ ] Migrate existing v1.5 data

### Stage 1.7 (Storage Abstraction)
- [ ] Create SQLite schema
- [ ] Implement SQLite repositories
- [ ] Create migration script: JSON → SQLite
- [ ] Add PostgreSQL support

### Stage 1.8+ (Production)
- [ ] Add database indexes
- [ ] Implement caching layer (Redis)
- [ ] Add database migrations (Alembic)
- [ ] Partition submissions table by date

---

## Conclusion

This normalized schema provides:
- ✅ Clean separation of concerns
- ✅ Support for multiple languages (interface + code)
- ✅ Efficient lazy loading
- ✅ Single source of truth (submissions)
- ✅ Easy migration to relational databases
- ✅ Scalability for hundreds of problems and thousands of users

The JSON structure directly maps to future SQL tables, making migration straightforward.
