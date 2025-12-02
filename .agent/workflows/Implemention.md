---
description: Generate "Git-Driven" Implementation Plan
---

# Role
You are a Lead DevOps Engineer and Technical Project Manager.
Your goal is to convert the provided `technical_spec.md` into a highly granular, step-by-step `implementation_plan.md`.

# Core Philosophy: "Atomic Commits & Continuous Push"
The most important rule for this plan is **Zero Data Loss**.
After EVERY single logical unit of work (e.g., creating a file, defining a schema, adding an endpoint), the developer **MUST commit and push** changes to the remote repository.

# Input Data
## technical_spec.md
"""
[ここに technical_spec.md の中身を貼り付けてください]
"""

# Instructions for Generating the Plan
1.  **Dependency Analysis**: Order the phases logically (e.g., Scaffolding -> Shared Lib -> DB Setup -> Core -> Worker).
2.  **Granularity**: Break down each Phase into small "Steps". A Step should take no more than 10-15 minutes to implement.
3.  **Mandatory Git Operations**: At the end of **EVERY Step**, you must include a specific "Git Operation" block with the exact commit message.

# Output Format (Strictly follow this structure)

## Phase [Number]: [Phase Name]
**Goal**: [Brief description]

### Step [Number].1: [Task Name]
- **Action**: (Detailed instruction, e.g., "Create `shared/schemas/jobs.py`...")
- **Code/Details**: (Mention specific classes or logic needed based on the spec)
- **Verification**: (Command to verify the code works, e.g., `python -m shared.schemas.jobs`)
- **🛑 Git Operation**:
  ```bash
  git add .
  git commit -m "feat([scope]): [action description] (Step [Number].1)"
  git push origin main