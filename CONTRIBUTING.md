# Contributing to Effy

First, thank you for contributing! Effy is an open-source project and we love to receive contributions from our community — you!

## Commit Message Guidelines

We use [python-semantic-release](https://python-semantic-release.readthedocs.io/) to automate our versioning and changelog generation. Because of this, **all commits must follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard.**

### Format

```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

The `<type>` must be one of the following:

- **`feat`**: A new feature. This will trigger a **MINOR** version bump (e.g. `0.1.0-alpha.1` -> `0.2.0-alpha.1`).
- **`fix`**: A bug fix. This will trigger a **PATCH** version bump (e.g. `0.1.0-alpha.1` -> `0.1.1-alpha.1`).
- **`perf`**: A code change that improves performance. This will trigger a **PATCH** version bump.
- **`docs`**: Documentation only changes.
- **`style`**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
- **`refactor`**: A code change that neither fixes a bug nor adds a feature.
- **`test`**: Adding missing tests or correcting existing tests.
- **`chore`**: Changes to the build process or auxiliary tools and libraries such as documentation generation.

### Breaking Changes

If your commit introduces a breaking change (API modification, renaming core classes, etc.), you **MUST** include `BREAKING CHANGE:` in the footer, or append an `!` after the type/scope (e.g., `feat!: rewrite renderer`). This triggers a **MAJOR** version bump.

### Examples

**Adding a new feature:**
```
feat(render): add hardware acceleration support for Metal
```

**Fixing a bug:**
```
fix(audio): prevent division by zero in mixer when volume is 0
```

**Breaking change:**
```
feat(window)!: change create_window signature to accept named arguments
```

### Release Process

Currently, Effy is in the **alpha** stage. Merging to the `master` branch will automatically generate an alpha tag (e.g., `v0.2.0-alpha.1`) and release the package.
