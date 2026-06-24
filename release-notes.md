# Release Notes

## Latest Changes

### Refactors

* ♻️ Refactor main Dockerfile to contain all logic, cache by uv. PR [#62](https://github.com/tiangolo/issue-manager/pull/62) by [@tiangolo](https://github.com/tiangolo).

### Internal

* ♻️ Migrate from plain pip to uv. PR [#60](https://github.com/tiangolo/issue-manager/pull/60) by [@tiangolo](https://github.com/tiangolo).
* 👷 Update issue-manager to 0.7.1. PR [#59](https://github.com/tiangolo/issue-manager/pull/59) by [@tiangolo](https://github.com/tiangolo).

## 0.7.1

### Fixes

* 🐛 Fix parsing empty config. PR [#58](https://github.com/tiangolo/issue-manager/pull/58) by [@tiangolo](https://github.com/tiangolo).

### Internal

* ⬆️ Update issue-manager to 0.7.0. PR [#57](https://github.com/tiangolo/issue-manager/pull/57) by [@tiangolo](https://github.com/tiangolo).
* ⬆ Bump python from 3.10-slim to 3.14.6-slim. PR [#52](https://github.com/tiangolo/issue-manager/pull/52) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump zizmorcore/zizmor-action from 0.5.3 to 0.5.6 in the github-actions group across 1 directory. PR [#55](https://github.com/tiangolo/issue-manager/pull/55) by [@dependabot[bot]](https://github.com/apps/dependabot).

## 0.7.0

### Features

* ✨ Add default labels `answered`, `waiting`, `invalid`, `maybe-ai`. PR [#56](https://github.com/tiangolo/issue-manager/pull/56) by [@tiangolo](https://github.com/tiangolo).

### Docs

* 📝 Fix formatting in `README.md`. PR [#41](https://github.com/tiangolo/issue-manager/pull/41) by [@tiangolo](https://github.com/tiangolo).

### Internal

* 🔒️ Add zizmor workflow security checks. PR [#54](https://github.com/tiangolo/issue-manager/pull/54) by [@tiangolo](https://github.com/tiangolo).
* ⬆️ Group Dependabot updates. PR [#53](https://github.com/tiangolo/issue-manager/pull/53) by [@tiangolo](https://github.com/tiangolo).
* ⬆ Bump the python-packages group across 1 directory with 2 updates. PR [#45](https://github.com/tiangolo/issue-manager/pull/45) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump the github-actions group across 1 directory with 4 updates. PR [#49](https://github.com/tiangolo/issue-manager/pull/49) by [@dependabot[bot]](https://github.com/apps/dependabot).
* 🔥 Remove config files now in central GitHub repo. PR [#47](https://github.com/tiangolo/issue-manager/pull/47) by [@tiangolo](https://github.com/tiangolo).
* 👷 Upgrade actions/checkout from v5 to v6. PR [#44](https://github.com/tiangolo/issue-manager/pull/44) by [@tiangolo](https://github.com/tiangolo).
* 👷 Upgrade `latest-changes` GitHub Action and pin `actions/checkout@v5`. PR [#43](https://github.com/tiangolo/issue-manager/pull/43) by [@tiangolo](https://github.com/tiangolo).
* ⬆ Bump actions/checkout from 4 to 5. PR [#38](https://github.com/tiangolo/issue-manager/pull/38) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump tiangolo/latest-changes from 0.3.2 to 0.4.0. PR [#37](https://github.com/tiangolo/issue-manager/pull/37) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆️ Update Dependabot ecosystem coverage. PR [#51](https://github.com/tiangolo/issue-manager/pull/51) by [@tiangolo](https://github.com/tiangolo).

## 0.6.0

* ✨ Add configurable reminder before closing issue. PR [#39](https://github.com/tiangolo/issue-manager/pull/39) by [@YuriiMotov](https://github.com/YuriiMotov).

### Internal

* 🎨 Format code with Ruff, to make reviews easier. PR [#40](https://github.com/tiangolo/issue-manager/pull/40) by [@tiangolo](https://github.com/tiangolo).
* ⬆ Bump tiangolo/latest-changes from 0.3.1 to 0.3.2. PR [#36](https://github.com/tiangolo/issue-manager/pull/36) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump docker/build-push-action from 5 to 6. PR [#35](https://github.com/tiangolo/issue-manager/pull/35) by [@dependabot[bot]](https://github.com/apps/dependabot).

## 0.5.1

### Features

* ⚡️ Improve speed (from 23 seconds to 3 seconds) by using Docker underneath. PR [#33](https://github.com/tiangolo/issue-manager/pull/33) by [@tiangolo](https://github.com/tiangolo).

### Fixes

* 🐛 Fix Docker deploy on branch `master` (not `main`). PR [#34](https://github.com/tiangolo/issue-manager/pull/34) by [@tiangolo](https://github.com/tiangolo).

### Docs

* 📝 Update docs and include `permissions` for `pull-request: write`. PR [#29](https://github.com/tiangolo/issue-manager/pull/29) by [@tiangolo](https://github.com/tiangolo).
* 📝 Update docs about token permissions. PR [#27](https://github.com/tiangolo/issue-manager/pull/27) by [@tiangolo](https://github.com/tiangolo).

### Internal

* 👷 Update `issue-manager.yml`. PR [#32](https://github.com/tiangolo/issue-manager/pull/32) by [@tiangolo](https://github.com/tiangolo).
* 👷 Update `latest-changes` GitHub Action. PR [#28](https://github.com/tiangolo/issue-manager/pull/28) by [@tiangolo](https://github.com/tiangolo).
* 👷 Update issue-manager.yml GitHub Action permissions. PR [#26](https://github.com/tiangolo/issue-manager/pull/26) by [@tiangolo](https://github.com/tiangolo).
* 🔧 Add GitHub templates for discussions and issues, and security policy. PR [#22](https://github.com/tiangolo/issue-manager/pull/22) by [@alejsdev](https://github.com/alejsdev).

## 0.5.0

### Features

* ✨ Add first-class support for PRs, including reviews, review comments. PR [#20](https://github.com/tiangolo/issue-manager/pull/20) by [@tiangolo](https://github.com/tiangolo).

## 0.4.1

### Fixes

* 🐛 Fix datetime comparison. PR [#19](https://github.com/tiangolo/issue-manager/pull/19) by [@tiangolo](https://github.com/tiangolo).

### Internal

* 🔧 Add funding. PR [#18](https://github.com/tiangolo/issue-manager/pull/18) by [@tiangolo](https://github.com/tiangolo).
* 👷 Update dependabot. PR [#17](https://github.com/tiangolo/issue-manager/pull/17) by [@tiangolo](https://github.com/tiangolo).
* 👷 Add latest-changes GitHub Action. PR [#16](https://github.com/tiangolo/issue-manager/pull/16) by [@tiangolo](https://github.com/tiangolo).

## 0.4.0

* ✨ Add support for managing PRs and remove support for HTML comments to avoid rate limits. PR [#12](https://github.com/tiangolo/issue-manager/pull/12) by [@tiangolo](https://github.com/tiangolo).
* 👷 Add Latest Changes GitHub Action. PR [#13](https://github.com/tiangolo/issue-manager/pull/13) by [@tiangolo](https://github.com/tiangolo).

## 0.3.0

* Add option to remove a label automatically after closing the issue. PR [#10](https://github.com/tiangolo/issue-manager/pull/10).

## 0.2.1

* Avoid crashing when a label has been edited _after_ added to the issue. PR [#9](https://github.com/tiangolo/issue-manager/pull/9).
* Fix using single quote (`'`) in README examples. PR [#6](https://github.com/tiangolo/issue-manager/pull/6) by [@svlandeg](https://github.com/svlandeg).

## 0.2.0

* Add support for running immediately with each specific issue after a new comment or label is added.
* Add support for issue labels, detecting if a new comment was added after the label and removing the label.

## 0.1.1

* Fix incorrect input name. PR [#3](https://github.com/tiangolo/issue-manager/pull/3) by [@browniebroke](https://github.com/browniebroke).

## 0.1.0

* Initial release.
