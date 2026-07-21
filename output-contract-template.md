# Worker Agent Output Contract Template

## Overview

This template provides a standardized format for worker agent responses, ensuring consistent reporting of task execution results for the delegator.

## Table Structure

```markdown
| What Was Done | Accomplishments | Files Modified | Skills Loaded |
|---------------|-----------------|----------------|---------------|
| [Description of actions taken] | [Key achievements and outcomes] | [List of file paths changed] | [List of skill names used] |
```

## Column Definitions

### What Was Done
- **Purpose**: Document the sequence of actions taken during task execution
- **Format**: Concise paragraph or bullet list describing steps performed
- **Content**: Include execution steps, decisions made, and problem-solving approaches
- **Examples**:
  - "Read configuration files and parsed JSON schema"
  - "Generated 3 new test files using pytest framework"
  - "Analyzed codebase and identified 5 security vulnerabilities"

### Accomplishments
- **Purpose**: Highlight key achievements and measurable outcomes
- **Format**: Bullet list of specific, quantifiable results
- **Content**: Include success metrics, completion status, and value delivered
- **Examples**:
  - "Reduced build time by 15% through cache optimization"
  - "Completed 100% of unit test coverage for module X"
  - "Resolved 3 blocking issues preventing deployment"

### Files Modified
- **Purpose**: Provide complete audit trail of file system changes
- **Format**: Markdown list of absolute or relative file paths
- **Content**: Include file path, action taken (created/modified/deleted), and brief descriptor
- **Examples**:
  - `src/config.ts` - Modified: Updated environment variable defaults
  - `tests/unit/api.test.ts` - Created: Added API endpoint tests
  - `docs/README.md` - Deleted: Replaced with new documentation structure

### Skills Loaded
- **Purpose**: Track which specialized capabilities were utilized
- **Format**: Comma-separated list of skill names
- **Content**: Include skill names exactly as registered in the skill catalog
- **Examples**:
  - `skill-bash-conventions, skill-script-bash-writer`
  - `task-delegation, generic-analysis`
  - `skill-node-script-conventions, skill-script-node-writer`

## Example Output Contracts

### Example 1: Script Generation Task

| What Was Done | Accomplishments | Files Modified | Skills Loaded |
|---------------|-----------------|----------------|---------------|
| Analyzed task requirements, reviewed skill documentation, and generated a new bash script with CLI entry point and library modules | Created `scripts/shell/deploy.sh` with full argument parsing and error handling; Implemented 3 reusable library functions | `scripts/shell/deploy.sh` - Created: Main deployment script with version checking and rollback support<br>`scripts/shell/lib/utils.sh` - Created: Shared utility functions for path handling and JSON parsing | `skill-bash-conventions`, `skill-script-bash-writer` |

### Example 2: Code Analysis Task

| What Was Done | Accomplishments | Files Modified | Skills Loaded |
|---------------|-----------------|----------------|---------------|
| Scanned repository for security vulnerabilities using static analysis patterns, reviewed 47 files, and documented findings | Identified 8 potential security issues across 3 files; Documented remediation steps for each finding | `security-audit/audit-report.md` - Created: Full security audit report with findings and recommendations<br>`security-audit/affected-files.json` - Created: JSON list of files requiring attention | `generic-analysis`, `skill-orchestration-reference` |

### Example 3: Documentation Update Task

| What Was Done | Accomplishments | Files Modified | Skills Loaded |
|---------------|-----------------|----------------|---------------|
| Reviewed existing documentation, updated API reference section, and regenerated table of contents | Improved documentation coverage by 25%; Added 15 new code examples | `docs/api-reference.md` - Modified: Updated endpoint documentation with request/response examples<br>`docs/README.md` - Modified: Regenerated table of contents with new sections | `skill-orchestration-reference` |

### Example 4: Task Delegation Task

| What Was Done | Accomplishments | Files Modified | Skills Loaded |
|---------------|-----------------|----------------|---------------|
| Decomposed complex request into 5 atomic tasks, assigned skills, and created task packets for worker execution | Reduced task complexity by 60%; Enabled parallel execution of independent tasks | `.tasks/task-001.json` - Created: Task packet for configuration analysis<br>.tasks/task-002.json - Created: Task packet for dependency review<br>.tasks/task-003.json - Created: Task packet for test coverage analysis | `breakdown-tasks`, `task-delegation` |

## Validation Rules

### Completeness Requirements

1. **All columns must be populated** - Empty columns indicate incomplete reporting
2. **Files Modified must be specific** - Use absolute paths or clear relative paths
3. **Skills Loaded must match registered skills** - No typos or variations allowed
4. **Accomplishments should be measurable** - Include numbers, percentages, or completion status

### Format Requirements

1. **Table must use valid Markdown syntax** - Proper column alignment and separators
2. **File paths must use backticks** - Inline code formatting for readability
3. **Bullet lists for multiple items** - Use `-` or `*` for list items within cells
4. **Consistent tense** - Use past tense for completed actions

### Quality Checks

- [ ] Every action in "What Was Done" has a corresponding accomplishment
- [ ] All modified files are listed with clear action descriptors
- [ ] All skills used are named exactly as registered in the skill catalog
- [ ] No placeholder text or template artifacts remain in output
- [ ] File paths are resolvable from the workspace root

### Error Conditions

- `BLOCKED: Missing output contract section` - A required column is entirely empty
- `BLOCKED: Invalid skill name` - A skill in "Skills Loaded" is not registered
- `BLOCKED: Ambiguous file path` - A file path cannot be resolved from workspace root
- `PARTIAL: Incomplete accomplishments` - Some accomplishments lack measurable metrics

## Usage Guidelines

### When to Use This Template

- All worker agent response outputs
- Task execution summaries for delegator review
- Cross-worker consistency enforcement
- Audit trail preservation

### Best Practices

1. **Be specific** - Include concrete details rather than general statements
2. **Quantify results** - Use numbers, percentages, and counts where possible
3. **Maintain consistency** - Follow the same format across all task types
4. **Document exceptions** - Note any deviations from standard procedures

### Template Extension

When new task types require additional reporting dimensions, extend this template by adding columns while maintaining the core four-column structure for baseline consistency.
