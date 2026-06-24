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
      - uses: tiangolo/issue-manager@0.7.1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
```

Then, you can answer an issue or PR and add one of the default labels:

* `answered`
* `waiting`
* `invalid`
* `maybe-ai`

For example, after adding `answered`, if no one has added a new comment after 10 days (or in the case of PRs, a new review or commit), the GitHub action will write:

```markdown
Assuming the original need was handled, this will be automatically closed now. But feel free to add more comments or start a new conversation if needed.
```

And then it will close the issue.

But if someone adds a comment _after_ you added the label, this GitHub Action will remove the label so that you can come back and check it instead of closing it.

## Config

You can use any file name you want, `issue-manager.yml` is just a suggestion. But it has to be inside of `.github/workflows/` and have a `.yml` extension.

By default, the action manages the labels `answered`, `waiting`, `invalid`, and `maybe-ai`.

You can override those defaults with a custom `config` input. The `config` has a `string`, and inside the string there's a whole JSON configuration:

```JSON
{"answered": {}}
```

...but it's all inside a `string`:

```YAML
'{"answered": {}}'
```

This JSON configuration (inside a string) is what allows you to add custom labels, with different delays, and different messages.

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
        "message": "Closing after 8 days of waiting for the additional info requested.",
        "reminder": {
            "before": "P3D",
            "message": "Heads-up: this will be closed in ~3 days unless there’s new activity."
        }
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

...the GitHub action would send a reminder on day 5 (because the delay is 8 days and the reminder is set to 3 days before closing):

```markdown
Heads-up: this will be closed in ~3 days unless there’s new activity.
```

...and if there is still no activity, it would finally close the issue with:

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

### Reminder

Each label can also define an optional reminder with:

* `before`: How long before the issue/PR would be closed to send the reminder.
  Must be shorter than the main `delay`.
  Supports ISO 8601 durations (e.g. `P3D`) or seconds.
* `message`: The text to post as a comment.

The reminder is just a comment, it does not close the issue or PR.

Example:

```json
"waiting": {
    "delay": 691200,
    "message": "Closing after 8 days of waiting for the additional info requested.",
    "reminder": {
        "before": "P3D",
        "message": "Heads-up: this will be closed in ~3 days unless there’s new activity."
    }
}
```

### Defaults

By default, if no `config` is provided, Issue Manager uses:

```json
{
    "answered": {
        "delay": 864000,
        "message": "Assuming the original need was handled, this will be automatically closed now. But feel free to add more comments or start a new conversation if needed."
    },
    "waiting": {
        "delay": 2628000,
        "message": "This has been waiting for the original user for a while and seems to be inactive, so it will be closed now. If there's still interest, feel free to start a new conversation.",
        "reminder": {
            "before": "P3D",
            "message": "Heads-up: this will be closed in 3 days unless there's new activity."
        }
    },
    "invalid": {
        "delay": 0,
        "message": "This was marked as invalid and will be closed now. If this is an error, please provide additional details."
    },
    "maybe-ai": {
        "delay": 0,
        "message": "This was marked as potentially AI generated and will be closed now. If this is an error, please provide additional details, make sure to read the docs about contributing and AI."
    }
}
```

By default, any label config has:

* `delay`: A delay of 10 days.
* `message`: A message of:

```markdown
Assuming the original need was handled, this will be automatically closed now. But feel free to add more comments or start a new conversation if needed.
```

* `remove_label_on_comment`: True. If someone adds a comment after you added the label, it will remove the label from the issue.
* `remove_label_on_close`: False. After this GitHub action closes the issue it would also remove the label from the issue.
* `reminder`: None. No reminder will be sent unless explicitly configured.

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
      - uses: tiangolo/issue-manager@0.7.1
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
                    "message": "Closing after 8 days of waiting for the additional info requested.",
                    "reminder": {
                        "before": "P3D",
                        "message": "Heads-up: this will be closed in ~3 days unless there’s new activity."
                    }
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
      - uses: tiangolo/issue-manager@0.7.1
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
                    "remove_label_on_close": true,
                    "reminder": {
                        "before": "P3D",
                        "message": "Heads-up: this will be closed in ~3 days unless there’s new activity."
                    }
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
* If a reminder is configured and its time has arrived, post the reminder comment.
* Check if the current date-time is more than the configured *delay* to wait for the user to reply back (configurable).
* Then, if all that matches, it will add a comment with a message (configurable).
* And then it will close the issue.

It will also run after each comment or label added, with the specific issue that has the new comment or label (if you used the example configurations from above).

## License

This project is licensed under the terms of the MIT license.
