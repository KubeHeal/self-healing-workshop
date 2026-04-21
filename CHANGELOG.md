# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned — v1.0.0 (Tracked Issues)

#### Content / Lab Exercises
- CPU throttling mitigation lab exercise using Coordination Engine throttle detection — [#4](https://github.com/KubeHeal/self-healing-workshop/issues/4)
- Right-sizing workflow and disk-full ETA lab exercises — [#5](https://github.com/KubeHeal/self-healing-workshop/issues/5)

#### Infrastructure
- Add `LICENSE` file; pin Antora version from `master` to `1.0` for reproducible builds — [#3](https://github.com/KubeHeal/self-healing-workshop/issues/3)
- Pin `content.sources` refs to CE/MCP/operator release tags and cut `v1.0.0` tag — [#6](https://github.com/KubeHeal/self-healing-workshop/issues/6)
- Verify `deploy-pages` and `build-python-examples` CI workflows pass; document branch protection — [#1](https://github.com/KubeHeal/self-healing-workshop/issues/1)

#### Documentation
- Add `RELEASE.md` with Antora version pin procedure and cross-repo reference checklist — [#2](https://github.com/KubeHeal/self-healing-workshop/issues/2)
- Add `CONTRIBUTING.md` with AsciiDoc authoring guide, Antora local preview, and PR checklist — [#7](https://github.com/KubeHeal/self-healing-workshop/issues/7)

---

## [0.9.0] - 2026-04-21

> Initial development baseline — **IN DEVELOPMENT**, not yet ready for production workshops.

### Added — Workshop Modules

| Module | Title | Status |
|--------|-------|--------|
| Module 0 | Introduction & Architecture | ✅ Complete |
| Module 1 | ML Model Training with Tekton | ✅ Complete |
| Module 2 | Deploy MCP Server & Configure Lightspeed | ✅ Complete |
| Module 3 | End-to-End Self-Healing with Lightspeed | ✅ Complete |
| Module 4 | Extra Credit — Advanced ML (LSTM, ensemble) | ✅ Complete |
| Module 5 | Notebook Catalog & Use Cases (33+ notebooks) | ✅ Complete |

### Added — Deployment

- Antora-based lab guide under `content/` with RHDP Showroom theme
- `site.yml` configured for `content.sources` from local `.` path
- AgnosticD V2 deployment path under `agnosticd/` (primary for RHDP workshops)
- Fork-and-deploy path for developer/contributor use
- `manifests/` for Kubernetes resource definitions
- `roles/` for Ansible automation roles
- `scripts/` for helper scripts
- Antora UI bundle from `rhpds/rhdp_showroom_theme` (RHDP Showroom theme)

### Known Issues (to be fixed in v1.0.0)

- `LICENSE` file missing — blocking open-source contribution ([#3](https://github.com/KubeHeal/self-healing-workshop/issues/3))
- Antora version pinned to `master` rather than a stable release ([#3](https://github.com/KubeHeal/self-healing-workshop/issues/3))
- CPU throttling, right-sizing, and disk-full exercises not yet written ([#4](https://github.com/KubeHeal/self-healing-workshop/issues/4), [#5](https://github.com/KubeHeal/self-healing-workshop/issues/5))
- Cross-repo content source refs not pinned to release tags ([#6](https://github.com/KubeHeal/self-healing-workshop/issues/6))
