# Delegator Simplification — Design Plan

## 1. Current State Summary

The delegator (`agents/delegator.md`) currently orchestrates a 6-step workflow that interleaves task tracking (todo-writer) and task display (display-tasks) with status updates throughout execution. After decomposition, it:

1. Displays the task table with a `pending` status map (step 3).
2. Writes all tasks to a todo tracker (step 4).
3. For each task, marks `in_progress` via todowriter (step 5a), redisplays with `in_progress` status (step 5b), delegates and waits (steps 5c–5d), marks `completed`/`cancelled` via todowriter (step 5e), and redisplays with final status (step 5f).

The `display-tasks` skill (`skills/display-tasks/SKILL.md`) accepts a `Status` map as optonal input, renders a `Status` column in its output table, and applies the supplied status (defaulting to `pending`).

The goal is to remove all todo tracking, eliminate redisplay calls (keep only the initial display), and strip status awareness from `display-tasks` — all while preserving the recently added lenient normalization logic in parsing.

---

## 2. Goal 1 — Stop Calling `todo-writer` From The Delegator

### Current Behavior

| Location | What happens |
|---|---|
| `agents/delegator.md` step 4 (lines 37–40) | Loads `todo-writer`, builds a `todos` array from packets, calls `todowrite` with full array. |
| `agents/delegator.md` step 5a (line 44) | Loads `todo-writer`, sets current packet status to `in_progress`, calls `todowrite` with full array. |
| `agents/delegator.md` step 5e (line 48) | Loads `todo-writer`, sets current packet status to `completed`/`cancelled`, calls `todowrite` with full array. |

**Total: 3 call sites.**

### Desired Behavior

Zero call sites. The delegator does not load `todo-writer` and does not invoke `todowrite` at any point.

### Specific Edits

#### File: `agents/delegator.md`

1. **Remove step 4 entirely** (lines 37–40):
   ```
   4. Track
      Load `todo-writer`.
      Build a `todos` array: one entry per packet (`content` = `## PURPOSE`, `status` = `pending`, `priority` per context).
      Invoke the `todowrite` tool once with the complete array.
   ```
   → Delete all four lines. Renumber subsequent steps (5 → 4, 6 → 5).

2. **Remove step 5a** (line 44 in original numbering, after removal step 4):
   ```
   a. **Mark in_progress**: Load `todo-writer`. Set its status to `in_progress` via `todowrite` with the full array.
   ```
   → Delete this line. Renumber sub-steps (b → a, c → b, d → c, e → d, f → e, g → f).

3. **Remove step 5e** (line 48 in original):
   ```
   e. **Mark completed or cancelled**: On success set `completed`; on BLOCKED/error set `cancelled`. Load `todo-writer` and invoke `todowrite` with the full array.
   ```
   → Delete this entire line.

4. **Update guardrail line 61** — remove `todo-writer` from the allow-list:
   ```
   - Never call skills other than `ask-question`, `display-tasks`, `task-delegation`, and `todo-writer` directly.
   ```
   → Change to:
   ```
   - Never call skills other than `ask-question`, `display-tasks`, and `task-delegation` directly.
   ```

#### File: `opencode.json`

5. **Line 80** — remove `"todo-writer"` from the delegator's skill allow-list:
   ```json
   "todo-writer": "allow",
   ```
   → Delete this line (leaving the comma on the preceding line if needed, or adjusting JSON delimiters).

---

## 3. Goal 2 — Display Task List Only After Breakdown (No Redisplay)

### Current Behavior

| Location | What happens |
|---|---|
| `agents/delegator.md` step 3 (lines 31–35) | Loads `display-tasks`, builds status map (`packet index → pending`), invokes display, renders table. → **Keep this.** |
| `agents/delegator.md` step 5b (line 45) | Loads `display-tasks`, updates status map for current index to `in_progress`, renders table. |
| `agents/delegator.md` step 5f (line 49) | Loads `display-tasks`, updates status map for current index to `completed`/`cancelled`, renders table. |

**Total: 3 call sites; keep 1 (step 3), remove 2 (steps 5b, 5f).**

### Desired Behavior

Only one display call, right after decomposition (the current step 3). No status map is built — the display is a simple static table without a status column. No redisplay during execution.

### Specific Edits

#### File: `agents/delegator.md`

1. **Simplify step 3** (lines 32–34): Remove status map construction and status map parameter from the `display-tasks` invocation:
   ```
   Load `display-tasks`.
   Build a status map with each packet index → `pending`.
   Invoke `display-tasks` with the full packets and the status map.
   ```
   → Change to:
   ```
   Load `display-tasks`.
   Invoke `display-tasks` with the full packets.
   ```
   Keep the render line: `Render the resulting Markdown table to the user.`

2. **Remove step 5b** (line 45 in original, will be line 5a after Goal 1 renumbering):
   ```
   b. **Redisplay with in_progress**: Load `display-tasks`. Update the status map for this packet index to `in_progress`. Render the updated Markdown table to the user.
   ```
   → Delete this line entirely.

3. **Remove step 5f** (line 49 in original, will be line 5d after Goal 1 and sub-step renumbering):
   ```
   f. **Redisplay with final status**: Load `display-tasks`. Update the status map for this packet index to `completed` or `cancelled`. Render the updated Markdown table to the user.
   ```
   → Delete this line entirely.

---

## 4. Goal 3 — Drop Status From `display-tasks` Skill

### Current Behavior

| Location | What it does |
|---|---|
| `skills/display-tasks/SKILL.md` line 13 | "Accepts full delegation packet text plus optional externally supplied status values." |
| Lines 16–17 | Defines optional `Status` map input with default `pending`. |
| Lines 26–28 | Output table includes a `Status` column header and corresponding column in rows. |
| Lines 41–42 | Extraction rule 4: uses supplied status or defaults to `pending`. |
| Line 48 | Execution step 3: applies status from supplied map or defaults to `pending`. |
| Line 57 | Guardrail: "The delegator decides when to call this skill and what status applies." |

### Desired Behavior

The skill is a pure rendering helper with no status awareness:
- Input: only delegation packets (no status map).
- Output: table with columns `Purpose`, `Files`, `Skill` (no `Status` column).
- Extraction rules: no status extraction.
- Execution: no status application step.

### Specific Edits

#### File: `skills/display-tasks/SKILL.md`

1. **Line 13** — Simplify input description:
   ```
   Accepts full delegation packet text plus optional externally supplied status values.
   ```
   → Change to:
   ```
   Accepts full delegation packet text.
   ```

2. **Lines 15–17** — Remove Status input block:
   ```
   - **Packets**: One or more delegation packets containing standard headers (`## PURPOSE`, `## FILES TO READ`, `## FILES TO WRITE`, `## SKILLS`, etc.).
   - **Status** (optional): A map of packet index to status string.
     If absent for a given packet, render `pending`.
   ```
   → Change to:
   ```
   - **Packets**: One or more delegation packets containing standard headers (`## PURPOSE`, `## FILES TO READ`, `## FILES TO WRITE`, `## SKILLS`, etc.).
   ```

3. **Lines 26–28** — Remove Status column from output format:
   ```
   | Purpose | Status | Files | Skill |
   | ------- | ------ | ----- | ----- |
   | ...     | ...    | ...   | ...   |
   ```
   → Change to:
   ```
   | Purpose | Files | Skill |
   | ------- | ----- | ----- |
   | ...     | ...   | ...   |
   ```

4. **Lines 41–42** — Remove extraction rule 4 entirely:
   ```
   4. **Status** — Use the supplied status for this packet's index.
      If no status is supplied, render `pending`.
   ```
   → Delete both lines. Renumber the list if there are subsequent rules (there are none; this is the last rule).

5. **Line 48** — Remove status application from execution plan:
   ```
   3. Apply status from supplied map or default to `pending`.
   4. Produce output per [Output Format](#output-format).
   ```
   → Change to:
   ```
   3. Produce output per [Output Format](#output-format).
   ```

6. **Line 57** — Update guardrail to remove status reference:
   ```
   - Do not own workflow decisions, task state, or delegation logic.
     The delegator decides when to call this skill and what status applies.
   ```
   → Change to:
   ```
   - Do not own workflow decisions, task state, or delegation logic.
     The delegator decides when to call this skill.
   ```

---

## 5. Goal 4 — Preserve Lenient Normalization Behavior

The existing lenient normalization in `delegator.md` must be kept unchanged. It operates on decomposition output before packet splitting.

### Current Behavior

| Location | Description |
|---|---|
| `agents/delegator.md` step 2, lines 27–28 | Normalize: discard leading/trailing prose without `## PURPOSE`, trim whitespace from packet segments, treat `## EXECUTION INSTRUCTION` as `## EXECUTION INSTRUCTIONS`. |
| `agents/delegator.md` line 46 (step 5c) | Passes the normalized packet to `task-delegation`. |
| `agents/delegator.md` line 63 (guardrail) | Lists the three allowed normalization operations. |
| `agents/delegator.md` line 67 (guardrail) | Ensures original or normalized packet (not rendered display) is passed to `task-delegation`. |

### Desired Behavior

All four references remain unchanged after the simplification. No edits are needed.

### Verification

After all Goal 1–3 edits, confirm that lines corresponding to 27–28, 46, 63, and 67 (in the final file) still contain the normalization logic exactly as written. These lines are not touched by any of the planned deletions.

---

## 6. Recommended Implementation Task Ordering

Each task is atomic. Dependencies are listed in parentheses.

| Order | Task | File(s) | Dependencies | Description |
|---|---|---|---|---|
| 1 | **Drop Status from display-tasks input** | `skills/display-tasks/SKILL.md` | None | Remove optional `Status` map from Input section (lines 13, 16–17). |
| 2 | **Drop Status from display-tasks output format** | `skills/display-tasks/SKILL.md` | Task 1 | Remove `Status` column from output table (lines 26–28). |
| 3 | **Drop Status extraction rule** | `skills/display-tasks/SKILL.md` | Task 1 | Remove extraction rule 4 (lines 41–42). |
| 4 | **Drop Status from display-tasks execution plan** | `skills/display-tasks/SKILL.md` | Task 1 | Remove "Apply status" step (line 48). |
| 5 | **Drop Status from display-tasks guardrail** | `skills/display-tasks/SKILL.md` | Task 1 | Simplify guardrail text referencing status (line 57). |
| 6 | **Remove todo-writer call sites and simplify step 3** | `agents/delegator.md` | Tasks 1–5 | Remove step 4 (todo tracking), step 5a (mark in_progress), step 5e (mark completed/cancelled). Simplify step 3 to remove status map building. Renumber steps. |
| 7 | **Remove redisplay calls** | `agents/delegator.md` | Task 6 | Remove step 5b (redisplay in_progress) and step 5f (redisplay final status). Renumber sub-steps. |
| 8 | **Update delegator guardrail** | `agents/delegator.md` | Task 6 | Remove `todo-writer` from the skills allow-list in guardrails (line 61). |
| 9 | **Remove todo-writer from opencode.json** | `opencode.json` | Task 8 | Remove `"todo-writer": "allow"` from delegator skill permissions (line 80). Adjust commas to keep valid JSON. |

**Key dependencies:**
- display-tasks changes (tasks 1–5) should be done **before** delegator.md changes (tasks 6–7) so the delegator never references a status parameter that no longer exists.
- opencode.json change (task 9) can be done last; it is purely administrative.
- Tasks 1–5 could be done in a single pass (they're all in one file); they are broken out for clarity.

---

## 7. Files Affected Summary

| File | Nature of Changes |
|---|---|
| `agents/delegator.md` | Remove 3 todo-writer call sites (step 4, 5a, 5e). Remove 2 redisplay calls (5b, 5f). Simplify step 3 display invocation (drop status map). Update guardrails. Renumber steps/sub-steps. **No changes to lenient normalization lines.** |
| `skills/display-tasks/SKILL.md` | Remove Status map from Input. Remove Status column from Output Format table. Remove extraction rule 4. Remove status application from Execution Plan. Simplify guardrail. |
| `opencode.json` | Remove `"todo-writer": "allow"` from delegator skill permissions. |

**Preserved intact:** All lenient normalization logic in `delegator.md` (lines 27–28, 46, 63, 67 in current numbering). `todo-writer/SKILL.md` untouched (other agents may still use it).