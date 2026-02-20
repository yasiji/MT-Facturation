# Branching And Pull Request Policy

## Branching
- `main`: protected production-ready branch.
- `feature/<scope>`: feature implementation branches.
- `fix/<scope>`: bug fix branches.
- `chore/<scope>`: maintenance and non-functional changes.

## Pull Request Rules
- No direct push to `main`.
- At least one approval required.
- All CI checks must pass before merge.
- Squash merge is default unless history preservation is required.

## Commit Quality
- Keep commits scoped and descriptive.
- Link related tasks or journal references in PR description.
- Include testing evidence in PR checklist.
