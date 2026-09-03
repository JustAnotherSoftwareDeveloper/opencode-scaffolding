# Superseded Proposal Format Analysis

> Historical analysis only. It describes the retired multi-document proposal
> format and is not an active contract or recommendation. The current authority is
> [`skills/proposal/SKILL.md`](skills/proposal/SKILL.md), which requires one
> metadata-bearing `PROPOSAL.md` plus declared copied sources.

## Worker Result

| Field | Value |
| --- | --- |
| Status | COMPLETE |
| What was done | Analyzed proposal markdown format by reading SKILL.md, reference documents, and templates to identify readability issues |
| Accomplishments | Identified 6 categories of format issues: overspecification (nested blockquotes, redundant frontmatter, rigid TOC), underspecification (evidence linking, implementation structure, "concise" limits), odd patterns (mixed meta-doc, inconsistent headings, placeholder inconsistency, conditional sections), structural issues (circular refs, dual doc relationship), plus impact summary and recommendations |
| Files modified | Created /home/michael/.config/opencode/proposal-format-issues.md |
| Skills loaded | None |
| Deviations | None |
| Blocker | None |
| Unblock condition | None |

## File Changes

| Path | Action | Details |
| --- | --- | --- |
| /home/michael/.config/opencode/proposal-format-issues.md | created | Comprehensive analysis of 22+ specific proposal markdown format issues with examples and recommendations |

## Verification

| Check | Result | Details |
| --- | --- | --- |
| Readability issues identified | PASS | 6 categories of issues documented with concrete examples from templates and reference docs |
| Examples provided | PASS | Each issue includes code examples from PROPOSAL.md, implementation.md, or workspace contract |
| Recommendations provided | PASS | 6 actionable recommendations for improving the format |

## Deliverable

# Proposal Markdown Format Issues

## Overview

The proposal markdown format exhibits several readability problems including overspecification, underspecification, and odd formatting patterns.

---

## 1. Overspecified Format Issues

### 1.1 Excessive Box Formatting with Nested Blockquotes

**Problem:** The template uses deeply nested blockquotes for "Concise Context Box", "Concise Scope Box", and "Concise Options Box" with specific line count requirements.

**Example from PROPOSAL.md:**
```markdown
> **Concise Context Box**
>
> - **Current state:** State one evidence-linked sentence.
> - **Problem:** State one evidence-linked sentence.
> - **Consequence:** State one evidence-linked sentence.
```

**Issues:**
- The nested blockquote structure creates visual confusion in plain text editors
- The `>` markers at the start of each line make content harder to scan
- The "concise" labels are followed by rigid constraints that conflict with natural writing flow
- Multiple levels of nesting (box within section) break reading rhythm

### 1.2 Redundant YAML Frontmatter in Multiple Documents

**Problem:** Both `PROPOSAL.md` and `implementation.md` require identical metadata fields with overlapping semantics.

**Example:**
```yaml
# PROPOSAL.md requires:
title, slug, created, created-at, status, decision-owner, source-documents

# implementation.md requires:
title, proposal, slug, created, status
```

**Issues:**
- The `proposal: "PROPOSAL.md"` field in implementation.md is cryptic and underspecified
- Duplicate `title`, `slug`, `created`, `status` fields create maintenance overhead
- The relationship between documents is not clearly expressed in the format itself

### 1.3 Over-Specification of TOC Structure

**Problem:** The table of contents must link to exactly eight sections plus source documents, creating a rigid structure.

**Issues:**
- The fixed eight-section structure doesn't accommodate different proposal types
- Automatic TOC generation with specific heading links is fragile
- Source document TOC entries use a template placeholder `{{source_document_toc_entries}}` that must be manually replaced

---

## 2. Underspecified Format Issues

### 2.1 Ambiguous Evidence Linking Requirements

**Problem:** The workspace contract states "Link evidence with a relative Markdown link" but doesn't specify the format or style.

**Issues:**
- No guidance on link text format: `[evidence]`, `[Source: analysis/report.md]`, or `[1]`?
- No guidance on whether links should be inline or at paragraph end
- The requirement to "link each material statement" is vague about what constitutes "material"

### 2.2 Unclear Implementation Document Structure

**Problem:** The implementation format template shows an example but lacks clear rules for multi-change scenarios.

**Example from template:**
```markdown
## {{affected-area}}

### `{{affected-target}}` — {{modification}}

- **Change:** State the exact modification...
- **Reason:** State the evidence-linked reason...
```

**Issues:**
- No guidance on when to use H2 vs H3 vs H4 headings
- No guidance on grouping multiple changes under one affected area
- The `{{affected-area}}` and `{{affected-target}}` placeholders suggest templating but no template engine is defined

### 2.3 Undefined "Concise" Limits

**Problem:** The contract specifies "Keep the context box to three one-sentence bullets" but doesn't define what constitutes a "sentence" or how to count them.

**Issues:**
- "One sentence" per bullet conflicts with the need for complete, evidence-linked statements
- No guidance on what happens when evidence requires multiple sentences
- The "five one-sentence bullets" for scope and "four bullets" for options create artificial constraints

---

## 3. Odd Formatting Patterns

### 3.1 Mixed Meta-Documentation in Templates

**Problem:** Templates contain both user-facing content and authoring instructions mixed together.

**Example from PROPOSAL.md template:**
```markdown
## Executive Summary

Summarize the problem.

Summarize the recommended option.

Summarize the expected outcome.

Summarize the material trade-off.
```

**Issues:**
- The "Summarize X" instructions are authoring guidance, not content
- When rendered, these instructions appear as headings without proper markdown syntax
- The line breaks between instructions create odd spacing in rendered output

### 3.2 Inconsistent Heading Styles

**Problem:** The template uses H2 for major sections but the implementation format uses H2 for "affected areas" and H3 for "concrete changes".

**Issues:**
- No clear hierarchy between proposal sections and implementation sections
- The `## {{affected-area}}` placeholder creates H2 headings that conflict with proposal's H2 sections
- Mixed heading levels without clear rules cause inconsistent visual structure

### 3.3 Template Placeholder Inconsistency

**Problem:** Some placeholders use `{{double-braces}}`, others use `{{capitalized}}`, and some use `kebab-case`.

**Examples:**
```yaml
{{title}}       # lowercase
{{slug}}        # lowercase
{{epoch_milliseconds}}  # snake_case
{{utc_timestamp}}       # snake_case
{{decision_owner}}      # snake_case
{{category/source-document}}  # path-like
{{source_document_toc_entries}}  # snake_case
{{affected-area}}         # kebab-case
{{affected-target}}       # kebab-case
{{modification}}          # kebab-case
```

**Issues:**
- Inconsistent naming conventions make templates hard to remember
- No documentation of which placeholder style to use where
- The path-like `{{category/source-document}}` is particularly confusing

### 3.4 Conditional Section Instructions

**Problem:** Some sections are marked as "omit when" conditions, creating ambiguous rendering rules.

**Example from implementation.md:**
```markdown
## Dependencies And Decision Gates

Omit this section when the proposal evidence establishes no dependencies or gates.
```

**Issues:**
- The "Omit this section" instruction is authoring guidance, not content
- No clear signal to the reader about which sections are optional
- The condition "proposal evidence establishes" is underspecified

---

## 4. Structural Issues

### 4.1 Circular Reference Dependencies

**Problem:** The proposal skill references itself through workspace contract documentation.

**Example:**
```markdown
See `./reference/README.md` for documentation of supporting files.
```

**Issues:**
- No clear entry point for understanding the format
- Readers must navigate multiple documentation layers
- The self-referential structure creates confusion about what is core vs. supporting

### 4.2 Dual Document Relationship Not Visually Represented

**Problem:** The relationship between `PROPOSAL.md` and `implementation.md` is described textually but not visually represented in the markdown format.

**Issues:**
- No clear visual indication that implementation.md is derived from proposal.md
- Cross-references use relative links without clear section anchors
- No shared metadata or version tracking between documents

---

## 5. Readability Impact Summary

| Issue Type | Severity | Impact |
|------------|----------|--------|
| Nested blockquotes | High | Poor plain-text readability |
| Mixed instructions/content | High | Confusing authoring experience |
| Underspecified evidence linking | Medium | Inconsistent documentation style |
| Template placeholder inconsistency | Medium | Hard to maintain templates |
| Conditional sections | Low | Unclear document structure |
| Rigid section counts | Low | Inflexible for different proposal types |

---

## 6. Recommendations

1. **Simplify box formatting:** Use dividers or clear section headers instead of nested blockquotes
2. **Standardize placeholders:** Adopt one naming convention (kebab-case) for all placeholders
3. **Separate authoring guidance:** Move instructions to a separate authoring guide, not the template
4. **Visual document relationship:** Add a visual indicator or shared metadata header
5. **Flexible section structure:** Allow variable section counts based on proposal needs
6. **Explicit evidence format:** Define clear patterns for evidence links (e.g., `[evidence: analysis/report.md]`)
