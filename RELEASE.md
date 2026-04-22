# Release Guide — self-healing-workshop

This document covers the release process for the Self-Healing Workshop, including
Antora version pinning, cross-repo reference management, and the AgnosticD/RHDP
catalog submission checklist.

---

## Versioning Policy

The workshop uses **Semantic Versioning** (`MAJOR.MINOR.PATCH`):

| Increment | When |
|-----------|------|
| **MAJOR** | Complete workshop restructure, major curriculum change |
| **MINOR** | New lab modules or exercises, new deployment path |
| **PATCH** | Content fixes, broken link repairs, image tag bumps |

Workshop releases are tied to KubeHeal Suite releases — a workshop version always
references specific tagged versions of the Coordination Engine, MCP server, and
AIOps Platform.

---

## Antora Version Pin Procedure

The `site.yml` must reference a stable Antora release (not `master`) before cutting `v1.0.0`.

### Update `site.yml`

```yaml
# Before (unsafe — tracks master branch):
content:
  sources:
    - url: .
      start_path: content

# After (pinned to a release tag):
content:
  sources:
    - url: https://github.com/KubeHeal/openshift-coordination-engine.git
      tags: [v1.1.0]
      start_path: docs/antora
    - url: https://github.com/KubeHeal/openshift-cluster-health-mcp.git
      tags: [v0.2.0]
      start_path: docs/antora
    - url: .
      start_path: content
```

### Update Antora CLI version in CI

```yaml
# .github/workflows/build.yml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
- run: npm install -g @antora/cli@3.1 @antora/site-generator@3.1
```

---

## Cross-Repo Reference Checklist

Before cutting a workshop release, verify all external references are pinned:

| Component | Reference Type | Target Tag |
|-----------|---------------|------------|
| `openshift-coordination-engine` | Antora content source | `v1.1.0` |
| `openshift-cluster-health-mcp` | Antora content source | `v0.2.0` |
| `openshift-aiops-platform` | Antora content source | `v1.0.0` |
| RHDP Showroom UI bundle | `site.yml` `ui.bundle.url` | Pinned release URL |

---

## Release Checklist

### 1. Pre-Release

- [ ] All issues in the target milestone are closed or moved to next milestone
- [ ] `CHANGELOG.md` `[Unreleased]` section is accurate
- [ ] `LICENSE` file present (closes [#3](https://github.com/KubeHeal/self-healing-workshop/issues/3))
- [ ] Antora version pinned in `site.yml` (not `master`)
- [ ] All cross-repo content source refs pinned to release tags (closes [#6](https://github.com/KubeHeal/self-healing-workshop/issues/6))
- [ ] CI green: `deploy-pages` and `build-python-examples` workflows pass (closes [#1](https://github.com/KubeHeal/self-healing-workshop/issues/1))
- [ ] New lab exercises validated by a test student run-through

### 2. Update CHANGELOG

```bash
# Move [Unreleased] to versioned section
# ## [1.0.0] - $(date +%Y-%m-%d)
git add CHANGELOG.md
git commit -s -m "release: prepare v1.0.0 — update CHANGELOG"
```

### 3. Tag and Push

```bash
VERSION=v1.0.0
git tag -a "$VERSION" -m "Release $VERSION"
git push origin main --tags
```

### 4. GitHub Release

```bash
gh release create "$VERSION" \
  --repo KubeHeal/self-healing-workshop \
  --title "self-healing-workshop $VERSION" \
  --notes-file <(sed -n "/^## \[$VERSION\]/,/^## \[/p" CHANGELOG.md | head -n -1) \
  --draft
```

---

## AgnosticD / RHDP Catalog Submission

The workshop is designed for deployment via AgnosticD V2 on the Red Hat Demo Platform.
Before submitting to the RHDP catalog:

- [ ] `agnosticd/` deployment automation tested end-to-end on RHDP sandbox
- [ ] `agnosticd_user_info` data pipeline verified (credentials flowing to students)
- [ ] Start/stop/status lifecycle tested
- [ ] Showroom lab guide renders correctly on RHDP
- [ ] Workshop duration estimate documented in catalog entry
- [ ] Prerequisite cluster topology (OCP 4.19+ recommended; 4.21 current; RHOAI, GPU node) documented

---

## Related Documentation

- [CHANGELOG.md](./CHANGELOG.md) — full version history
- [CONTRIBUTING.md](./CONTRIBUTING.md) — content authoring guide
- [README.adoc](./README.adoc) — workshop overview and deployment options
- [GitHub Issues](https://github.com/KubeHeal/self-healing-workshop/issues)
