# Plan Audit Report

## Audit identity and input provenance
- Audit identity: `audit-5a3d0daaea6a1f1f`
- Generated at: `2026-09-03T22:10:02.585283+00:00` (provenance only; finding IDs do not contain this time)
- Plan workspace: `/home/michael/.config/opencode/.plans/1788473325297-pipeline-smoke-test`
- Proposal baseline: `/home/michael/.config/opencode/.proposals/1788473283228-pipeline-smoke-test`
- Baseline mode: `authoritative`
- Proposal metadata (status/readiness/owner facts): ```json
{
  "created": "1788473283228",
  "created-at": "2026-09-03T00:00:00Z",
  "decision-owner": "user",
  "readiness": "decision-ready",
  "slug": "pipeline-smoke-test",
  "source-documents": [
    "other/heading-policy.md"
  ],
  "status": "draft",
  "title": "Proposal to plan to execute smoke test"
}
```
- Plan metadata: ```json
{}
```
- Historical assignment inventory: `None` (comparison only)
- Copied-snapshot origin: `None`; capture time: `None`
- Audit output: `/home/michael/.config/opencode/.smoke/pipeline-reports/pre-execution-audit.md`
- Read-only boundary: only the caller-declared new report may be written.
- Input manifest:
```json
[
  {
    "bytes": 2629,
    "path": "draft.json",
    "resolved": "/home/michael/.config/opencode/.plans/1788473325297-pipeline-smoke-test/draft.json",
    "sha256": "7215706f1d12d4787f72772a62a95f007c9dfdcdac36d53db1da58b4fee4151a",
    "tree": "plan"
  },
  {
    "bytes": 2820,
    "path": "other/PROPOSAL.md",
    "resolved": "/home/michael/.config/opencode/.plans/1788473325297-pipeline-smoke-test/other/PROPOSAL.md",
    "sha256": "30f2471c454b7e563527d63c1ec921413f69399418f48538fc7163788d6a2010",
    "tree": "plan"
  },
  {
    "bytes": 199,
    "path": "other/heading-policy.md",
    "resolved": "/home/michael/.config/opencode/.plans/1788473325297-pipeline-smoke-test/other/heading-policy.md",
    "sha256": "01571beaa9d7d5756527f0a36807528d26ba19ea24f077d921a044ce843ecedd",
    "tree": "plan"
  },
  {
    "bytes": 2629,
    "path": "tasks.json",
    "resolved": "/home/michael/.config/opencode/.plans/1788473325297-pipeline-smoke-test/tasks.json",
    "sha256": "7215706f1d12d4787f72772a62a95f007c9dfdcdac36d53db1da58b4fee4151a",
    "tree": "plan"
  },
  {
    "bytes": 1877,
    "path": "tasks.md",
    "resolved": "/home/michael/.config/opencode/.plans/1788473325297-pipeline-smoke-test/tasks.md",
    "sha256": "5b67ca099330594a63e3c1351dbbf288b8612d7973fe9ede3851f74859be7f06",
    "tree": "plan"
  },
  {
    "bytes": 2820,
    "path": "PROPOSAL.md",
    "resolved": "/home/michael/.config/opencode/.proposals/1788473283228-pipeline-smoke-test/PROPOSAL.md",
    "sha256": "30f2471c454b7e563527d63c1ec921413f69399418f48538fc7163788d6a2010",
    "tree": "proposal"
  },
  {
    "bytes": 199,
    "path": "other/heading-policy.md",
    "resolved": "/home/michael/.config/opencode/.proposals/1788473283228-pipeline-smoke-test/other/heading-policy.md",
    "sha256": "01571beaa9d7d5756527f0a36807528d26ba19ea24f077d921a044ce843ecedd",
    "tree": "proposal"
  },
  {
    "bytes": 3453,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/agent-factory/SKILL.md",
    "sha256": "84c2dc84505c338b6629ba825563932d8cbc52d50a9192c80c3b1853e95691af",
    "tree": "skill:agent-factory"
  },
  {
    "bytes": 2937,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/command-factory/SKILL.md",
    "sha256": "92dd7803a4eeeae1467653c256430eac826a849a5c8268f5aedc5580eb07e964",
    "tree": "skill:command-factory"
  },
  {
    "bytes": 5579,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/customize-opencode/SKILL.md",
    "sha256": "49e678325c0ed3e8d93ca9156bd2c8094d86245bc33cda1d384e222971bd2077",
    "tree": "skill:customize-opencode"
  },
  {
    "bytes": 6484,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/generic-analysis/SKILL.md",
    "sha256": "cb7946684335ea4280993355ee054cd03ff3cc7d3c548c24c18025ebc78a90f1",
    "tree": "skill:generic-analysis"
  },
  {
    "bytes": 3153,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/generic-executor/SKILL.md",
    "sha256": "7e7ce7cad8662f3c6fdddeac12b27886a1329ac837269520cdb1ae9428e7754d",
    "tree": "skill:generic-executor"
  },
  {
    "bytes": 5276,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/plan-audit/SKILL.md",
    "sha256": "c3e38ef32823d3f9e94b4ce21f98e99f7991d82da216cf8390c15cc519d197a7",
    "tree": "skill:plan-audit"
  },
  {
    "bytes": 6999,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/plan-writer/SKILL.md",
    "sha256": "1a496a05cd2d7a5d3ddb03d2071c42e3eee28fc894f6267d6353f9d30947e9f3",
    "tree": "skill:plan-writer"
  },
  {
    "bytes": 8969,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/proposal/SKILL.md",
    "sha256": "94e2a4a571e9ff47b4d6e5786ea1c0e8b7fd6ad1e98e4b28d8a38cb6f19e970a",
    "tree": "skill:proposal"
  },
  {
    "bytes": 1220,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-authoring-guide/SKILL.md",
    "sha256": "c455dde684fac8379be3237245f5a5172eb5d2df6f176c708c5b9de6e6cf14bd",
    "tree": "skill:skill-authoring-guide"
  },
  {
    "bytes": 3199,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-bash-conventions/SKILL.md",
    "sha256": "357b7e7d88011c5c993102cc323748899c06911de862cca5ff7901cca176ef5f",
    "tree": "skill:skill-bash-conventions"
  },
  {
    "bytes": 2637,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-factory/SKILL.md",
    "sha256": "758f422cc58af63a9661e952bcd0f4e25d24e4750f286cef793947e9dfc3137a",
    "tree": "skill:skill-factory"
  },
  {
    "bytes": 1432,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-maintenance-reference/SKILL.md",
    "sha256": "36bfc11f2332abb45bc3b8a4373e749e981c2e7c0e39de80f40631f624f83917",
    "tree": "skill:skill-maintenance-reference"
  },
  {
    "bytes": 3217,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-node-script-conventions/SKILL.md",
    "sha256": "bce4baef695a2bd4d830cc39e2ccb919e71b7089eb43b14092835f91daadb62c",
    "tree": "skill:skill-node-script-conventions"
  },
  {
    "bytes": 1870,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-reviewer/SKILL.md",
    "sha256": "e314f0845ca38ab1fa6220baa3b68a84c36e1cbc34a77cc462bc3718c9961316",
    "tree": "skill:skill-reviewer"
  },
  {
    "bytes": 6942,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-script-bash-test-writer/SKILL.md",
    "sha256": "e3ae5dc664cd34807cbc16eb9bc5d8bfffdd286581030ab86a49015a426e6e85",
    "tree": "skill:skill-script-bash-test-writer"
  },
  {
    "bytes": 6830,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-script-bash-writer/SKILL.md",
    "sha256": "88466a5bb340c19d24c6627d9801ac89beba7e5717327b1547ed773eb0c98fed",
    "tree": "skill:skill-script-bash-writer"
  },
  {
    "bytes": 4938,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-script-node-test-writer/SKILL.md",
    "sha256": "cdc696302799dadad5ac4b446f098c90bed44c7cd4f0b8c8c1f0c7f171bfb7e1",
    "tree": "skill:skill-script-node-test-writer"
  },
  {
    "bytes": 6447,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-script-node-writer/SKILL.md",
    "sha256": "281b8c4e4da9b757bcf60c6b346a6076ed3a6dc066a7890e05d88310184980bf",
    "tree": "skill:skill-script-node-writer"
  },
  {
    "bytes": 3513,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-script-python-test-writer/SKILL.md",
    "sha256": "6cbeb70877d84ce9d9c7f1508674c43fd0008f9a2ef2c4b468c17cffb72986b9",
    "tree": "skill:skill-script-python-test-writer"
  },
  {
    "bytes": 3788,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-script-python-writer/SKILL.md",
    "sha256": "7f25afe8091bae02625a08b8e61515a152524879b61fb2ae2a499603338d6f0d",
    "tree": "skill:skill-script-python-writer"
  },
  {
    "bytes": 2189,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/skill-template-library/SKILL.md",
    "sha256": "23bcac3c676d0c62388815be1eb607c1968cb221f8c31c6b49ecaad46ed7208d",
    "tree": "skill:skill-template-library"
  },
  {
    "bytes": 2261,
    "path": "SKILL.md",
    "resolved": "/home/michael/.config/opencode/skills/task-contract/SKILL.md",
    "sha256": "d9eaab18caf006b29620da1c4de8f3b4d88378ffa801a68040994749fc39be3c",
    "tree": "skill:task-contract"
  }
]
```
- Fresh collector command:
  `uv run --project ~/.config/opencode/scripts/python collect-skills --class operation --class documentation`
- Collector success: `True`; return code: `0`; captured at: `2026-09-03T22:10:02.416236+00:00`
- Collector working directory: `/home/michael/.config/opencode`
- Collector configured project root: `/home/michael/.config/opencode`; config directory: `/home/michael/.config/opencode`
- Collector output digest: `9d3b19effb5873ec93875b026237f3598da89a98a4acc2580d022a7b686c3546`
- Fresh collector array:
```json
[
  {
    "class": "operation",
    "description": "Use when creating or updating one agents/ contract.",
    "name": "agent-factory",
    "path": "/home/michael/.config/opencode/skills/agent-factory/SKILL.md",
    "selection": {
      "not_for": [
        "command",
        "skill",
        "or arbitrary repository file creation; delegation; runtime agent execution"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "create agent"
        ],
        "inputs": [
          "agent specification"
        ],
        "outputs": [
          "agent file"
        ]
      },
      "use_when": [
        "creating or updating one agents/ contract"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when creating or updating one commands/ contract.",
    "name": "command-factory",
    "path": "/home/michael/.config/opencode/skills/command-factory/SKILL.md",
    "selection": {
      "not_for": [
        "agent",
        "skill",
        "or arbitrary repository file creation; planning; delegation"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "create command"
        ],
        "inputs": [
          "command specification"
        ],
        "outputs": [
          "command file"
        ]
      },
      "use_when": [
        "creating or updating one commands/ contract"
      ]
    },
    "source": "global"
  },
  {
    "class": "documentation",
    "description": "Use when reference is needed for OpenCode worker packet execution-engine behavior.",
    "name": "customize-opencode",
    "path": "/home/michael/.config/opencode/skills/customize-opencode/SKILL.md",
    "selection": {
      "not_for": [
        "modifying an OpenCode configuration"
      ],
      "role": "reference",
      "tags": {
        "environments": [
          "OpenCode"
        ],
        "inputs": [
          "worker packet"
        ],
        "outputs": [
          "execution engine reference"
        ],
        "topics": [
          "OpenCode packet execution"
        ]
      },
      "use_when": [
        "the packet execution engine contract needs reference"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when analyzing a problem, request, artifact, or decision to produce an evidence-calibrated assessment and next actions.",
    "name": "generic-analysis",
    "path": "/home/michael/.config/opencode/skills/generic-analysis/SKILL.md",
    "selection": {
      "not_for": [
        "authoring a decision proposal or executable plan"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "analyze",
          "assess"
        ],
        "inputs": [
          "problem",
          "request",
          "artifact",
          "decision"
        ],
        "outputs": [
          "analysis",
          "evidence-calibrated assessment"
        ],
        "topics": [
          "cross-domain reasoning"
        ]
      },
      "use_when": [
        "a problem or decision needs evidence-based analysis"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when executing one bounded ordinary file-maintenance result without a specialized owner.",
    "name": "generic-executor",
    "path": "/home/michael/.config/opencode/skills/generic-executor/SKILL.md",
    "selection": {
      "not_for": [
        "commands",
        "agents",
        "skills",
        "scripts",
        "plans",
        "proposals",
        "audits",
        "destructive operations",
        "packet orchestration",
        "delegation",
        "specialized-owner work"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "execute maintenance"
        ],
        "inputs": [
          "explicit specification"
        ],
        "outputs": [
          "maintenance result"
        ]
      },
      "use_when": [
        "executing one bounded ordinary file-maintenance result without a specialized owner"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when auditing one immutable proposal-derived plan snapshot without changing audited inputs.",
    "name": "plan-audit",
    "path": "/home/michael/.config/opencode/skills/plan-audit/SKILL.md",
    "selection": {
      "not_for": [
        "creating or revising a plan",
        "repairing findings or assigning replacement skills",
        "approving a proposal or changing readiness"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "audit"
        ],
        "constraints": [
          "read-only",
          "immutable snapshot",
          "external report only"
        ],
        "inputs": [
          "plan workspace",
          "proposal baseline",
          "task packet"
        ],
        "outputs": [
          "UTF-8 Markdown audit report"
        ],
        "topics": [
          "proposal traceability",
          "task atomicity",
          "exact skill assignment"
        ]
      },
      "use_when": [
        "a caller requests an independent audit of one plan and proposal input snapshot"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when creating a source-document plan workspace that produces executable task JSON.",
    "name": "plan-writer",
    "path": "/home/michael/.config/opencode/skills/plan-writer/SKILL.md",
    "selection": {
      "not_for": [
        "general analysis or decision proposal authoring"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "create executable plan"
        ],
        "constraints": [
          "source grounded"
        ],
        "inputs": [
          "source documents"
        ],
        "outputs": [
          "plan workspace",
          "executable task JSON"
        ],
        "topics": [
          "implementation planning"
        ]
      },
      "use_when": [
        "source documents must become an executable plan workspace"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when creating an evidence-based decision proposal from source documents.",
    "name": "proposal",
    "path": "/home/michael/.config/opencode/skills/proposal/SKILL.md",
    "selection": {
      "not_for": [
        "general assessment or executable task planning"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "create decision proposal"
        ],
        "constraints": [
          "source grounded"
        ],
        "inputs": [
          "source documents"
        ],
        "outputs": [
          "decision proposal"
        ],
        "topics": [
          "decision making"
        ]
      },
      "use_when": [
        "source documents must become a durable decision proposal"
      ]
    },
    "source": "global"
  },
  {
    "class": "documentation",
    "description": "Use when authoring or reviewing a readable, discriminative skill selection profile.",
    "name": "skill-authoring-guide",
    "path": "/home/michael/.config/opencode/skills/skill-authoring-guide/SKILL.md",
    "selection": {
      "not_for": [
        "creating or updating skill implementation files"
      ],
      "role": "reference",
      "tags": {
        "outputs": [
          "valid skill metadata"
        ],
        "topics": [
          "skill selection profiles",
          "skill authoring"
        ]
      },
      "use_when": [
        "creating or reviewing direct-selection metadata"
      ]
    },
    "source": "global"
  },
  {
    "class": "documentation",
    "description": "Use when referencing shared Bash script conventions for OpenCode, including portability, ShellCheck, errors, and output.",
    "name": "skill-bash-conventions",
    "path": "/home/michael/.config/opencode/skills/skill-bash-conventions/SKILL.md",
    "selection": {
      "not_for": [
        "generating Bash scripts or tests"
      ],
      "role": "reference",
      "tags": {
        "constraints": [
          "ShellCheck compliance"
        ],
        "environments": [
          "OpenCode"
        ],
        "inputs": [
          "Bash script requirements"
        ],
        "outputs": [
          "portable shell conventions"
        ],
        "topics": [
          "Bash scripts"
        ]
      },
      "use_when": [
        "Bash script authoring needs shared platform conventions"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when creating or updating one OpenCode skill workspace from requirements and source material.",
    "name": "skill-factory",
    "path": "/home/michael/.config/opencode/skills/skill-factory/SKILL.md",
    "selection": {
      "not_for": [
        "reviewing one existing skill, migrating a family, choosing taxonomy, or maintaining passive guidance"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "create skill",
          "update skill"
        ],
        "constraints": [
          "direct selection profile"
        ],
        "inputs": [
          "skill requirements",
          "source material"
        ],
        "outputs": [
          "validated skill workspace"
        ],
        "topics": [
          "OpenCode skills"
        ]
      },
      "use_when": [
        "creating or updating one selected skill workspace under skills/<name>/"
      ]
    },
    "source": "global"
  },
  {
    "class": "documentation",
    "description": "Use when referencing maintenance workflows, migration procedures, validation checks, or known pitfalls for skill maintenance.",
    "name": "skill-maintenance-reference",
    "path": "/home/michael/.config/opencode/skills/skill-maintenance-reference/SKILL.md",
    "selection": {
      "not_for": [
        "creating or updating skill implementation files"
      ],
      "role": "reference",
      "tags": {
        "constraints": [
          "migration validation"
        ],
        "outputs": [
          "maintenance guidance"
        ],
        "topics": [
          "skill maintenance"
        ]
      },
      "use_when": [
        "maintaining or migrating an existing skill workspace"
      ]
    },
    "source": "global"
  },
  {
    "class": "documentation",
    "description": "Use when referencing shared Node/TypeScript script conventions for OpenCode, including tooling, testing, and coverage.",
    "name": "skill-node-script-conventions",
    "path": "/home/michael/.config/opencode/skills/skill-node-script-conventions/SKILL.md",
    "selection": {
      "not_for": [
        "generating Node scripts or tests"
      ],
      "role": "reference",
      "tags": {
        "constraints": [
          "Bun tooling"
        ],
        "environments": [
          "OpenCode"
        ],
        "inputs": [
          "Node script requirements"
        ],
        "outputs": [
          "script convention guidance"
        ],
        "topics": [
          "Node TypeScript scripts"
        ]
      },
      "use_when": [
        "Node or TypeScript script authoring needs shared conventions"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when assessing one existing skill workspace for evidence-linked conformance findings and a bounded disposition.",
    "name": "skill-reviewer",
    "path": "/home/michael/.config/opencode/skills/skill-reviewer/SKILL.md",
    "selection": {
      "not_for": [
        "creating or editing a skill, migrating a family, choosing taxonomy, or replacing validators"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "assess",
          "review"
        ],
        "constraints": [
          "read-only review",
          "one workspace"
        ],
        "inputs": [
          "existing skill workspace",
          "class contract",
          "selection profile"
        ],
        "outputs": [
          "conformance analysis"
        ],
        "topics": [
          "skill conformance",
          "validation evidence"
        ]
      },
      "use_when": [
        "a maintainer needs findings and a pass/fail recommendation for one existing skill"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when generating bats-core test files for existing Bash scripts under scripts/shell/.",
    "name": "skill-script-bash-test-writer",
    "path": "/home/michael/.config/opencode/skills/skill-script-bash-test-writer/SKILL.md",
    "selection": {
      "not_for": [
        "creating the Bash implementation"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "write Bash tests"
        ],
        "environments": [
          "bats-core"
        ],
        "inputs": [
          "existing Bash script"
        ],
        "outputs": [
          "bats-core test suite"
        ],
        "topics": [
          "script testing"
        ]
      },
      "use_when": [
        "an existing shell script needs bats-core tests"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when generating deterministic Bash scripts from requirements, including CLI entry points, libraries, tests, and Makefile registration.",
    "name": "skill-script-bash-writer",
    "path": "/home/michael/.config/opencode/skills/skill-script-bash-writer/SKILL.md",
    "selection": {
      "not_for": [
        "adding tests to an existing Bash script"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "create Bash script"
        ],
        "constraints": [
          "deterministic generation"
        ],
        "inputs": [
          "Bash script requirements"
        ],
        "outputs": [
          "registered Bash implementation"
        ],
        "topics": [
          "script implementation"
        ]
      },
      "use_when": [
        "a shell script and its registered implementation must be created"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when generating Bun test files for existing Node scripts under scripts/node/, including CLI and library tests.",
    "name": "skill-script-node-test-writer",
    "path": "/home/michael/.config/opencode/skills/skill-script-node-test-writer/SKILL.md",
    "selection": {
      "not_for": [
        "creating the Node implementation"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "write Node tests"
        ],
        "environments": [
          "Bun test"
        ],
        "inputs": [
          "existing Node script"
        ],
        "outputs": [
          "Bun test suite"
        ],
        "topics": [
          "script testing"
        ]
      },
      "use_when": [
        "an existing Node script needs Bun tests"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when generating deterministic TypeScript Node scripts from requirements, including CLI entry points, libraries, tests, and registration.",
    "name": "skill-script-node-writer",
    "path": "/home/michael/.config/opencode/skills/skill-script-node-writer/SKILL.md",
    "selection": {
      "not_for": [
        "adding tests to an existing Node script"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "create Node script"
        ],
        "constraints": [
          "deterministic generation"
        ],
        "environments": [
          "Bun"
        ],
        "inputs": [
          "Node or TypeScript script requirements"
        ],
        "outputs": [
          "registered Node implementation"
        ],
        "topics": [
          "script implementation"
        ]
      },
      "use_when": [
        "a TypeScript Node script and its project registration must be created"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when generating pytest files for existing Python scripts under scripts/python/, including CLI and library tests.",
    "name": "skill-script-python-test-writer",
    "path": "/home/michael/.config/opencode/skills/skill-script-python-test-writer/SKILL.md",
    "selection": {
      "not_for": [
        "creating the Python implementation"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "write Python tests"
        ],
        "environments": [
          "pytest"
        ],
        "inputs": [
          "existing Python script"
        ],
        "outputs": [
          "pytest test suite"
        ],
        "topics": [
          "script testing"
        ]
      },
      "use_when": [
        "an existing Python script needs pytest coverage"
      ]
    },
    "source": "global"
  },
  {
    "class": "operation",
    "description": "Use when generating deterministic Python scripts from requirements, including CLI entry points, libraries, tests, and registration.",
    "name": "skill-script-python-writer",
    "path": "/home/michael/.config/opencode/skills/skill-script-python-writer/SKILL.md",
    "selection": {
      "not_for": [
        "adding tests to an existing Python script"
      ],
      "role": "owner",
      "tags": {
        "actions": [
          "create Python script"
        ],
        "constraints": [
          "deterministic generation"
        ],
        "inputs": [
          "Python script requirements"
        ],
        "outputs": [
          "registered Python implementation"
        ],
        "topics": [
          "script implementation"
        ]
      },
      "use_when": [
        "a Python script and its project registration must be created"
      ]
    },
    "source": "global"
  },
  {
    "class": "documentation",
    "description": "Use when referencing skill templates, schemas, or snippets for skill authoring.",
    "name": "skill-template-library",
    "path": "/home/michael/.config/opencode/skills/skill-template-library/SKILL.md",
    "selection": {
      "not_for": [
        "executing a skill workflow",
        "maintaining an existing skill",
        "assigning task skills"
      ],
      "role": "reference",
      "supports": [
        "skill-factory"
      ],
      "tags": {
        "actions": [
          "reference",
          "scaffold",
          "select"
        ],
        "constraints": [
          "documentation-only",
          "canonical examples"
        ],
        "environments": [
          "OpenCode"
        ],
        "inputs": [
          "skill requirements",
          "source material"
        ],
        "outputs": [
          "selection profile",
          "skill scaffold"
        ],
        "topics": [
          "skill authoring",
          "templates",
          "schemas",
          "snippets"
        ]
      },
      "use_when": [
        "an author needs a class-aware skill profile or canonical template"
      ]
    },
    "source": "global"
  },
  {
    "class": "documentation",
    "description": "Use when referencing shared semantics for authoring one atomic task and its traceable result.",
    "name": "task-contract",
    "path": "/home/michael/.config/opencode/skills/task-contract/SKILL.md",
    "selection": {
      "not_for": [
        "decomposing a request into tasks",
        "creating a plan workspace",
        "executing a task packet",
        "validating task JSON structure"
      ],
      "role": "reference",
      "supports": [
        "breakdown-tasks",
        "plan-writer"
      ],
      "tags": {
        "actions": [
          "reference",
          "explain"
        ],
        "constraints": [
          "passive",
          "documentation-only",
          "non-transitive"
        ],
        "inputs": [
          "task request",
          "task metadata"
        ],
        "outputs": [
          "shared task-contract context"
        ],
        "topics": [
          "task identity",
          "atomicity",
          "verification alignment",
          "dependencies",
          "coupling",
          "traceability"
        ]
      },
      "use_when": [
        "the request needs shared semantics for a task boundary, result, verification, dependency, coupling, or traceability"
      ]
    },
    "source": "global"
  }
]
```

## Overall disposition
- **FAIL**
- Rollup precedence: `BLOCKED` > `FAIL` > `CONDITIONAL PASS` > `PASS`.
- This disposition is audit evidence only; it is not approval, acceptance, readiness, implementation completion, or permission to repair.

## Proposal compliance
- Source comparison: authoritative baseline remains primary; see manifest and source-drift diagnostics.
### Disposition: FAIL
- Coverage: complete
- Confidence: HIGH
- Criteria:
  - decision traceability
  - scope and exclusion traceability
  - design-constraint traceability
  - implementation-target traceability
  - verification traceability
  - source identity and labels
  - write-boundary preservation
- Diagnostics:
- **PC-DESIGN-CONSTRAINT-TRACEABILITY-a63f951cffe8** — `FAIL` — missing design-constraint traceability
  - Criterion: `DESIGN-CONSTRAINT-TRACEABILITY`; location: `plan tasks and brief`; confidence: `HIGH`.
  - Expected: proposal material traceable to plan
  - Observed: no trace marker
  - Impact: proposal-derived scope is untraceable
- Evidence gaps:
  - None.

## Task atomicity
- Structural and conceptual coverage are reported separately.
### Disposition: PASS
- Coverage: complete
- Confidence: HIGH
- Criteria:
  - published schema
  - conceptual split test
  - one purpose/result/verification boundary
  - dependencies and predecessor reads
  - coupling evidence
- Diagnostics:
- None.
- Evidence gaps:
  - None.

## Skill assignment
- Assignment authority: the one fresh exact operation/documentation collector array.
### Disposition: PASS
- Coverage: complete
- Confidence: HIGH
- Criteria:
  - one-to-three cardinality
  - fresh collector reconciliation
  - winning name/class/path
  - SKILL.md inspection
  - contract fit and authority safety
- Diagnostics:
- None.
- Evidence gaps:
  - None.

## Evidence gaps and open decisions
- None.

## Remediation handoff
- Correction owner: `plan-writer`.
- The auditor performed no correction, replacement assignment, publication, or self-certification.
- Stable findings requiring bounded review:
  - `PC-DESIGN-CONSTRAINT-TRACEABILITY-a63f951cffe8` — revise only the plan-owned boundary identified by the finding, preserve sources and labels, then rerun this exact audit.
