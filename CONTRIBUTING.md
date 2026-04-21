# Contributing to self-healing-workshop

Thank you for contributing to the Self-Healing Workshop. This guide covers content
authoring in AsciiDoc/Antora, local preview setup, and the PR checklist.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

---

## Developer Certificate of Origin (DCO)

All commits **must** be signed off:

```bash
git commit -s -m "feat: your change description"
# Appends: Signed-off-by: Your Name <your@email.com>
```

---

## Getting Started

### Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Node.js | 20+ | For Antora CLI |
| `@antora/cli` | 3.1+ | Local preview builds |
| Python | 3.11+ | Example scripts |
| OpenShift CLI (`oc`) | 4.18+ | Workshop step validation |

### Setup

```bash
git clone https://github.com/KubeHeal/self-healing-workshop.git
cd self-healing-workshop

# Install Antora for local preview
npm install -g @antora/cli @antora/site-generator

# Build the workshop site locally
antora --fetch site.yml

# Open in browser
open www/index.html      # macOS
xdg-open www/index.html  # Linux
```

---

## Content Structure

```
content/
├── modules/
│   ├── ROOT/
│   │   ├── nav.adoc          ← Navigation menu
│   │   └── pages/
│   │       ├── index.adoc    ← Landing page
│   │       ├── module-00/    ← Module 0: Introduction
│   │       ├── module-01/    ← Module 1: ML Training
│   │       ├── module-02/    ← Module 2: MCP Server
│   │       ├── module-03/    ← Module 3: Self-Healing Demo
│   │       ├── module-04/    ← Module 4: Advanced ML
│   │       └── module-05/    ← Module 5: Notebook Catalog
│   └── supplemental-ui/      ← Custom UI overrides
└── antora.yml                ← Antora component descriptor
```

---

## AsciiDoc Authoring Guide

### Page Header

Every page **must** begin with a title and the following attributes:

```asciidoc
= Page Title
:navtitle: Short Nav Title
:description: One-sentence description for search engines
```

### Student Instructions

Use the `[source]` block style for commands students must run:

```asciidoc
[source,bash,role="execute"]
----
oc get pods -n openshift-aiops
----
```

The `role="execute"` attribute enables one-click execution in the Showroom terminal.

### Callouts and Notes

```asciidoc
[NOTE]
====
Use this for tips that help but aren't critical.
====

[WARNING]
====
Use this for actions that could break the environment.
====

[IMPORTANT]
====
Use this for prerequisites or mandatory steps.
====
```

### Screenshots

Store screenshots under `content/modules/ROOT/assets/images/`:

```asciidoc
image::module-01/anomaly-detected.png[Anomaly Detection Dashboard,800]
```

---

## Branch Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| New module/exercise | `feat/<module>-<topic>` | `feat/module-03-throttle-lab` |
| Bug fix | `fix/<description>` | `fix/broken-oc-command` |
| Documentation | `docs/<description>` | `docs/update-prerequisites` |
| Infrastructure | `chore/<description>` | `chore/pin-antora-version` |

---

## Pull Request Process

1. Fork the repo and create a branch
2. Make your changes with DCO-signed commits
3. Build and preview the site locally: `antora --fetch site.yml`
4. Open a PR against `main` with:
   - A clear title and description
   - A link to the rendered page (screenshot or local preview URL)
   - Reference to related issues: `Closes #<number>`

### PR Checklist

- [ ] DCO sign-off on all commits (`git commit -s`)
- [ ] Local `antora --fetch site.yml` builds without errors or warnings
- [ ] All student commands tested against a real OCP cluster (or noted as untested)
- [ ] New exercises follow the `[source,bash,role="execute"]` pattern for Showroom
- [ ] `CHANGELOG.md` `[Unreleased]` section updated
- [ ] Cross-repo refs use pinned tags, not `main`/`master`

---

## Adding a New Lab Exercise

1. Create a new `.adoc` file in the appropriate `module-0x/` directory
2. Add it to `content/modules/ROOT/nav.adoc`
3. Update `CHANGELOG.md` `[Unreleased]` with a brief description
4. Open an issue referencing the new exercise (or reference an existing one)
5. Submit a PR following the process above

---

## Reporting Issues

Open an issue describing:
- Which module and step is affected
- OCP version and deployment path (AgnosticD or fork-and-deploy)
- Expected vs actual behavior
- Showroom terminal output (if applicable)

---

## Related Documentation

- [RELEASE.md](./RELEASE.md) — Antora pinning and release process
- [CHANGELOG.md](./CHANGELOG.md) — version history
- [README.adoc](./README.adoc) — workshop overview
- [GitHub Issues](https://github.com/KubeHeal/self-healing-workshop/issues)
