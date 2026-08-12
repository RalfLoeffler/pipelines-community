# VS Code setup for `pipelines-community`

This repository must be opened as the VS Code workspace root:

```text
D:\repos\pipelines-community
```

Do not open `D:\repos` or the sibling
`D:\repos\protocolqc-xnat-scaffold` as the workspace when working on this
repository.

## Open the correct workspace

From PowerShell:

```powershell
code --reuse-window "D:\repos\pipelines-community"
```

Or use **File → Open Folder...** and select `D:\repos\pipelines-community`.
The Explorer should show `AGENTS.md`, `doc`, `specs`, `src`, and `tests` at its
top level. VS Code commonly hides `.git`; verify the Git root with the commands
below instead of relying on the Explorer.

Opening a folder in VS Code and launching a new Codex/code session are related
but separate actions. Start the new session after opening the correct folder so
the platform assigns the correct working directory and writable workspace.

## Verify the workspace before editing

Open a new integrated PowerShell terminal with **Terminal → New Terminal** and
run:

```powershell
Get-Location
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
```

For this checkout, the expected results are:

```text
D:\repos\pipelines-community
local-qwen-task
```

If `git rev-parse --show-toplevel` reports another repository, stop. Close the
VS Code window or code session and reopen `D:\repos\pipelines-community`. Do
not rely on a prompt mentioning the correct path to repair an already-created
session sandbox.

The same guard is recorded in `AGENTS.md` for Codex and other repository-aware
agents.

## Start with the Mamba environment

The expected environment is `pipelines-community`. From PowerShell, activate
it before launching VS Code:

```powershell
mamba activate pipelines-community
Set-Location "D:\repos\pipelines-community"
code --reuse-window .
```

Verify the environment in the integrated terminal:

```powershell
$env:CONDA_DEFAULT_ENV
python -c "import sys; print(sys.executable)"
```

Expected values are:

```text
pipelines-community
C:\Users\z3528919\.local\share\mamba\envs\pipelines-community\python.exe
```

The absolute interpreter path is machine-specific. Use **Python: Select
Interpreter** in VS Code and choose the interpreter belonging to the
`pipelines-community` environment rather than committing that path in shared
workspace settings. Enable `Python: Terminal Activate Environment` so new
terminals activate the selected interpreter.

If PowerShell does not recognize `mamba activate`, initialize Mamba once for
PowerShell, restart the terminal, and retry:

```powershell
mamba shell init --shell powershell
```

For commands that must not depend on shell activation, use:

```powershell
mamba run -n pipelines-community python -c "import sys; print(sys.executable)"
mamba run -n pipelines-community python -m pytest -q
```

Starting Codex from the activated terminal helps it inherit the environment,
but environment activation does not set the repository workspace. Verify both
the Mamba environment and the Git root independently.

## Git and local-work precautions

The current branch is `local-qwen-task` and tracks
`origin/local-qwen-task`. Inspect status before changing files:

```powershell
git status --short --branch
git diff --check
```

The ProtocolQC implementation, specification, resource, requirements, and
authored documentation are currently local working-tree additions. Do not use
**Source Control → Discard All Changes**, `git reset --hard`, or broad cleanup
commands while these files are under review. Preserve unrelated untracked files
listed by `git status`.

## Documentation locations

The repository intentionally uses two documentation locations:

- `doc/` contains maintained, hand-authored documentation, including
  `doc/repository_analysis.md` and `doc/protocol-qc/README.md`.
- `docs/` is ignored/generated output used by CI for `docs/pipelines` and
  `docs/build/html`.

Do not rename CI-generated `docs/` paths to `doc/`. Add or update maintained
documentation under `doc/`.

## Python interpreter and tests

Select the interpreter for the environment that contains the repository’s
declared dependencies using **Python: Select Interpreter**. The committed
packages define their build and test extras in:

- `src/au.edu.sydney.sydneyimaging/pyproject.toml`
- `src/au.edu.unsw.rinsw/pyproject.toml`

The root dependency used by CI is in `requirements.txt`. The local ProtocolQC
scaffold has separate declarations in
`requirements/quality-control/protocol-qc.txt` and
`specs/australian-imaging-service-community-unsw/au/edu/unsw/rinsw/protocolqc.yaml`.

Use the repository’s documented commands from the integrated terminal:

```powershell
python -m pytest -q
python -m pytest -q tests\test_docs.py
python -m pytest -q src\au.edu.unsw.rinsw\australianimagingservice\community\au\edu\unsw\rinsw\protocol_qc\tests
```

The ProtocolQC-focused command requires pytest and its runtime dependencies to
be installed. The current environment may not contain pytest; record that as a
validation limitation rather than installing or upgrading dependencies without
approval. CI’s package-test and documentation-build commands are defined in
`.github/workflows/ci-cd.yml`.

## Codex and VS Code sessions

If using Codex from the VS Code terminal:

1. Open `D:\repos\pipelines-community` as the VS Code folder.
2. Start a fresh code session from that folder.
3. State the expected repository and branch in the initial request when the
   task is non-trivial.
4. Let the first action verify `Get-Location`, Git top-level, and branch before
   any edit.

### Hard stop for a wrong sandbox

A terminal in the right directory does not prove that a code session has the
right sandbox. Before asking Codex to inspect or edit, use this exact initial
instruction:

```text
Before doing anything, verify Get-Location, git rev-parse --show-toplevel, and
git branch --show-current. Confirm that the session's cwd and writable workspace
are D:\repos\pipelines-community and stop without editing if they differ.
```

If the code-session interface displays its environment or workspace context,
check that both its current directory and writable workspace root are
`D:\repos\pipelines-community`. If either points to another repository, close
the session and start a new one after opening this folder in VS Code. Changing
directories in a terminal or naming the intended path in a prompt does not
rebind an existing session's sandbox.

For the local agent workflow, review `README_codex.md`, `.codex/config.toml`,
and `.codex/agents/`. Restart Codex after changing project agent configuration.
The project-local Codex configuration controls agent behavior and concurrency;
it does not rebind the platform sandbox root after a session has started.

## Troubleshooting a wrong workspace

If a session reports or edits
`D:\repos\protocolqc-xnat-scaffold`, the session was initialized with the
wrong workspace. `workdir` can direct an individual shell command to another
directory, but it does not change the session’s sandbox root or the default
file-edit target.

Fix it by:

1. Closing the current code session.
2. Opening `D:\repos\pipelines-community` as the VS Code workspace.
3. Starting a new terminal and verifying the commands above.
4. Starting a new Codex/code session from that workspace.

If the correct repository is outside the session’s writable sandbox, the tool
may request filesystem approval. Opening the correct folder at session startup
is the preferred fix.
