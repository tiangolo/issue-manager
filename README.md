# Issue Manager

Automatically close issues or pull requests that have a **label**, after a **custom delay**, if no one replies back.

## How to use

Install this GitHub action by creating a file in your repo at `.github/workflows/issue-manager.yml`.

A minimal example could be:

```yml
name: Issue Manager

on:
  schedule:
    - cron: "0 0 * * *"
  issue_comment:
    types:
      - created
  issues:
    types:
      - labeled
  pull_request_target:
    types:
      - labeled
  workflow_dispatch:

permissions:
  issues: write
  pull-requests: write

jobs:
  issue-manager:
    runs-on: ubuntu-latest
    steps:
      - uses: tiangolo/issue-manager@0.4.0
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config: '{"answered": {}}'
```

Then, you can answer an issue or PR and add the label from the config, in this case, `answered`.

After 10 days, if no one has added a new comment (or in the case of PRs, a new review or commit), the GitHub action will write:

```markdown
Assuming the original need was handled, this will be automatically closed now.
```

And then it will close the issue.

But if someone adds a comment _after_ you added the label, this GitHub Action will remove the label so that you can come back and check it instead of closing it.

## Config

You can use any file name you want, `issue-manager.yml` is just a suggestion. But it has to be inside of `.github/workflows/` and have a `.yml` extension.

If you check, the `config` in that file `issue-manager.yml` above has a `string`, and inside the string there's a whole JSON configuration:

```JSON
{"answered": {}}
```

...but it's all inside a `string`:

```YAML
'{"answered": {}}'
```

This JSON configuration (inside a string) is what allows us to add multiple custom labels, with different delays, and different messages.

Imagine this JSON config:

```JSON
{
    "answered": {
        "delay": "P3DT12H30M5S",
        "message": "It seems the issue was answered, closing this now."
    },
    "validated": {
        "delay": 300,
        "message": "The issue could not be validated after 5 minutes. Closing now."
    },
    "waiting": {
        "delay": 691200,
        "message": "Closing after 8 days of waiting for the additional info requested."
    },
    "needs-tests": {
      "delay": 691200,
      "message": "This PR will be closed after waiting 8 days for tests to be added. Please create a new one with tests."
    }
}
```

In this case, if:

* the issue has a label `answered`
* the label was added _after_ the last comment
* the last comment was written more than 3 days, 12 hours, 30 minutes and 5 seconds ago

...the GitHub action would close the issue with a message of:

```markdown
It seems the issue was answered, closing this now.
```

But if there was a new comment created _after_ the label was added, by default, it would remove the label.

---

But then, if:

* the issue has a label `validated`
* the label was added _after_ the last comment
* the last comment was written more than `300` seconds ago (5 minutes)

...the GitHub action would close the issue with a message:

```markdown
The issue could not be validated after 5 minutes. Closing now.
```

And also, if there was a new comment created _after_ the label was added, by default, it would remove the label.

---

Then, if:

* the issue has a label `waiting`
* the label was added _after_ the last comment
* the last comment was addded more than `691200` seconds (8 days) ago

...the GitHub action would close the issue with:

```markdown
Closing after 10 days of waiting for the additional info requested.
```

And again, by default, removing the label if there was a new comment written after adding the label.

---

And finally, if:

* a PR has a label `needs-tests`
* the label was added _after_ the last comment
* the last comment was added more than `691200` seconds (8 days) ago

...the GitHub action would close the PR with:

```markdown
This PR will be closed after waiting 8 days for tests to be added. Please create a new one with tests.
```

**Note**: in this last example the process is applied to a PR instead of an issue. The same logic applies to both issues and PRs. If you want a label to only apply to issues, you should use that label only with issues, and the same with PRs.

### Delay

The delay can be configured using [anything supported by Pydantic's `datetime`](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types).

So, it can be an [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) period format (like `P3DT12H30M5S`), or the number of seconds between the two dates (like `691200`, or 10 days) plus other options.

### Remove label on comment

You can also pass a config `remove_label_on_comment` per keyword. By default, it's `true`.

When someone adds a comment _after_ the label was added, then this GitHub action won't close the issue.

On top of not closing the issue, by default, it will remove the label. You can disable removing the label by setting `remove_label_on_comment` to `false`.

### Remove label on close

After this GitHub action closes an issue it can also automatically remove the label from the issue when you pass the config `remove_label_on_close` set to `true`.

By default it is false, and doesn't remove the label from the issue.

### Defaults

By default, any config has:

* `delay`: A delay of 10 days.
* `message`: A message of:

```markdown
Assuming the original issue was solved, it will be automatically closed now.
```

* `remove_label_on_comment`: True. If someone adds a comment after you added the label, it will remove the label from the issue.
* `remove_label_on_close`: False. After this GitHub action closes the issue it would also remove the label from the issue.

### Config in the action

To use that same JSON config from above, you would have to put it on a single `string` inside the GitHub Action config (`issue-manager.yml`).

But YAML supports multiline strings using `>`.

Just make sure to indent everything to be part of the same string.

So, you can put all the config with:

```yml
name: Issue Manager

on:
  schedule:
    - cron: "0 0 * * *"
  issue_comment:
    types:
      - created
      - edited
  issues:
    types:
      - labeled
  pull_request_target:
    types:
      - labeled
  workflow_dispatch:

permissions:
  issues: write
  pull-requests: write

jobs:
  issue-manager:
    runs-on: ubuntu-latest
    steps:
      - uses: tiangolo/issue-manager@0.4.0
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config: >
            {
                "answered": {
                    "delay": "P3DT12H30M5S",
                    "message": "It seems the issue was answered, closing this now."
                },
                "validated": {
                    "delay": 300,
                    "message": "The issue could not be validated after 5 minutes. Closing now."
                },
                "waiting": {
                    "delay": 691200,
                    "message": "Closing after 8 days of waiting for the additional info requested."
                }
            }
```

### Edit your own config

If you have [Visual Studio Code](https://code.visualstudio.com) or another modern editor, you can create your JSON config by creating a JSON file, e.g. `config.json`.

Then writing the contents of your config in that file, and then copying the results.

But you can do it all with autocomplete :rocket:.

You can start your JSON config file with:

```JSON
{
    "$schema": "https://raw.githubusercontent.com/tiangolo/issue-manager/master/schema.json"
}
```

And then after you write a keyword and start its config, like `"answered": {}`, it will autocomplete the internal config keys, like `delay`, `message`. And will validate its contents.

It's fine to leave the `$schema` in the `config` on the `.yml` file, it will be discarded and won't be used as a label.

### A complete example

**Note**: you probably don't need all the configs, the examples above should suffice for most cases. But if you want to make the GitHub action _not_ remove the labels if someone adds a new comment, this can help as an example:

```yml
name: Issue Manager

on:
  schedule:
    - cron: "0 0 * * *"
  issue_comment:
    types:
      - created
      - edited
  issues:
    types:
      - labeled
  pull_request_target:
    types:
      - labeled
  workflow_dispatch:

permissions:
  issues: write
  pull-requests: write

jobs:
  issue-manager:
    runs-on: ubuntu-latest
    steps:
      - uses: tiangolo/issue-manager@0.4.0
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config: >
            {
                "$schema": "https://raw.githubusercontent.com/tiangolo/issue-manager/master/schema.json",
                "answered": {
                    "delay": "P3DT12H30M5S",
                    "message": "It seems the issue was answered, closing this now.",
                    "remove_label_on_comment": false,
                    "remove_label_on_close": false
                },
                "validated": {
                    "delay": 300,
                    "message": "The issue could not be validated after 5 minutes. Closing now.",
                    "remove_label_on_comment": true,
                    "remove_label_on_close": false
                },
                "waiting": {
                    "delay": 691200,
                    "message": "Closing after 8 days of waiting for the additional info requested.",
                    "remove_label_on_comment": true,
                    "remove_label_on_close": true
                }
            }
```

## GitHub Action triggers

If you check the examples above, they have a section that says when to run the GitHub action:

```yml
on:
  schedule:
    - cron: "0 0 * * *"
  issue_comment:
    types:
      - created
      - edited
  issues:
    types:
      - labeled
  pull_request_target:
    types:
      - labeled
  workflow_dispatch:
```

* The `cron` option means that the GitHub action will be run every day at 00:00 UTC.
* The `issue_comment` option means that it will be run with a specific issue when a comment is added.
    * This way, if there's a new comment, it can immediately remove any label that was added before the new comment.
* The `issues` option with a type of `label` will run it with each specific issue when you add a label.
    * This way you can add a label to an issue that was answered long ago, and if the configured delay since the last comment is enough the GitHub action will close the issue right away.
* The `pull_request_target` option with a type of `label` will run it with each specific Pull Request made to your repo when you add a label.
    * This way you can add a label to a PR that was answered long ago, or that was waiting for more comments from the author, reviews, commits, etc. And if the configured delay since the last comment is enough the GitHub action will close the issue right away.
* The `workflow_dispatch` option allows you to run the action manually from the GitHub Actions tab for your repo.

## GitHub Action Permissions

From the examples above you can see a section:

```yml
permissions:
  issues: write
  pull-requests: write
```

This is to give the GitHub Action the necessary permissions to write to the issues and pull requests (including removing the label).

When you add this GitHub Action to a personal repo, you might not need this specific permission.

But when you add it to a repo that belongs to a GitHub organization, depending on the organization default configurations, you might need to explicitly set this permission.

## Motivation

### Closing early

When I answer an issue, I like to give the original user some time to respond and give them the chance to close the issue before doing it myself.

Or sometimes, I have to request additional info.

Sometimes, my answer didn't respond the real question/problem, and if I closed the issue immediately, it would end up feeling "impolite" to the user.

Moreover, if I closed the issue prematurely, there's a smaller chance that I (or someone else) will revisit it again to answer the real question/problem.

### Not closing

But then, if I leave the issue open after giving an answer, in many cases, the issue will keep open until I come back to close it, after many days.

Then, after that time (10 days, 30 days) and after seeing that there are no new comments, I write "I assume the problem is solved, closing this issue now".

But that requires me going through all the open issues again, one by one, check where I (or someone else) have already answered, typing that message, etc.

## Alternatives

One option would be to use a tool that closes stale issues, like [probot/stale](https://github.com/probot/stale), or the [Close Stale Issues Action](https://github.com/marketplace/actions/close-stale-issues).

But if the user came back explaining that my answer didn't respond to his/her problem or giving the extra info requested, but I couldn't respond on time, the issue would still go "stale" and be closed.

## What Issue Manager does

This action allows the repo owner to add a label (e.g. `answered`) to an issue after answering. Or multiple labels with multiple configurations (multiple messages, delays, etc).

Then, this action, by running every night (or however you configure it) will, for each open issue:

* Check if the issue has one of the configured labels.
* Check if the label was added _after_ the last comment.
* If not, remove the label (configurable).
* Check if the current date-time is more than the configured *delay* to wait for the user to reply back (configurable).
* Then, if all that matches, it will add a comment with a message (configurable).
* And then it will close the issue.

It will also run after each comment or label added, with the specific issue that has the new comment or label (if you used the example configurations from above).

## Release Notes

### Latest Changes

#### Features

* ⚡️ Improve speed by using Docker underneath. PR [#33](https://github.com/tiangolo/issue-manager/pull/33) by [@tiangolo](https://github.com/tiangolo).

#### Fixes

* 🐛 Fix Docker deploy on branch `master` (not `main`). PR [#34](https://github.com/tiangolo/issue-manager/pull/34) by [@tiangolo](https://github.com/tiangolo).

#### Docs

* 📝 Update docs and include `permissions` for `pull-request: write`. PR [#29](https://github.com/tiangolo/issue-manager/pull/29) by [@tiangolo](https://github.com/tiangolo).
* 📝 Update docs about token permissions. PR [#27](https://github.com/tiangolo/issue-manager/pull/27) by [@tiangolo](https://github.com/tiangolo).

#### Internal

* 👷 Update `issue-manager.yml`. PR [#32](https://github.com/tiangolo/issue-manager/pull/32) by [@tiangolo](https://github.com/tiangolo).
* 👷 Update `latest-changes` GitHub Action. PR [#28](https://github.com/tiangolo/issue-manager/pull/28) by [@tiangolo](https://github.com/tiangolo).
* 👷 Update issue-manager.yml GitHub Action permissions. PR [#26](https://github.com/tiangolo/issue-manager/pull/26) by [@tiangolo](https://github.com/tiangolo).
* 🔧 Add GitHub templates for discussions and issues, and security policy. PR [#22](https://github.com/tiangolo/issue-manager/pull/22) by [@alejsdev](https://github.com/alejsdev).

### 0.5.0

#### Features

* ✨ Add first-class support for PRs, including reviews, review comments. PR [#20](https://github.com/tiangolo/issue-manager/pull/20) by [@tiangolo](https://github.com/tiangolo).

### 0.4.1

#### Fixes

* 🐛 Fix datetime comparison. PR [#19](https://github.com/tiangolo/issue-manager/pull/19) by [@tiangolo](https://github.com/tiangolo).

#### Internal

* 🔧 Add funding. PR [#18](https://github.com/tiangolo/issue-manager/pull/18) by [@tiangolo](https://github.com/tiangolo).
* 👷 Update dependabot. PR [#17](https://github.com/tiangolo/issue-manager/pull/17) by [@tiangolo](https://github.com/tiangolo).
* 👷 Add latest-changes GitHub Action. PR [#16](https://github.com/tiangolo/issue-manager/pull/16) by [@tiangolo](https://github.com/tiangolo).

### 0.4.0

* ✨ Add support for managing PRs and remove support for HTML comments to avoid rate limits. PR [#12](https://github.com/tiangolo/issue-manager/pull/12) by [@tiangolo](https://github.com/tiangolo).
* 👷 Add Latest Changes GitHub Action. PR [#13](https://github.com/tiangolo/issue-manager/pull/13) by [@tiangolo](https://github.com/tiangolo).

### 0.3.0

* Add option to remove a label automatically after closing the issue. PR [#10](https://github.com/tiangolo/issue-manager/pull/10).

### 0.2.1

* Avoid crashing when a label has been edited _after_ added to the issue. PR [#9](https://github.com/tiangolo/issue-manager/pull/9).
* Fix using single quote (`'`) in README examples. PR [#6](https://github.com/tiangolo/issue-manager/pull/6) by [@svlandeg](https://github.com/svlandeg).

### 0.2.0

* Add support for running immediately with each specific issue after a new comment or label is added.
* Add support for issue labels, detecting if a new comment was added after the label and removing the label.

### 0.1.1

* Fix incorrect input name. PR [#3](https://github.com/tiangolo/issue-manager/pull/3) by [@browniebroke](https://github.com/browniebroke).

### 0.1.0

* Initial release.

## License

This project is licensed under the terms of the MIT license.
