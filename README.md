# Issue Manager

Automatically close issues that have a **label**, after a **custom delay**, if no one replies back.

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
      - edited
  issues:
    types:
      - labeled

jobs:
  issue-manager:
    runs-on: ubuntu-latest
    steps:
        - uses: tiangolo/issue-manager@0.2.0
        with:
            token: ${{ secrets.GITHUB_TOKEN }}
            config: '{"answered": {}}'
```

Then, you can answer an issue and add the label from the config, in this case, `answered`.

After 10 days, if no one has added a new comment, the GitHub action will write:

```markdown
Assuming the original issue was solved, it will be automatically closed now.
```

And then it will close the issue.

But if someone adds a comment _after_ you added the label, it will remove the label.

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
        "message": "It seems the issue was answered, I'll close this now."
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

In this case, if:

* the issue has a label `answered`
* the label was added _after_ the last comment
* the last comment was written more than 3 days, 12 hours, 30 minutes and 5 seconds ago

...the GitHub action would close the issue with a message of:

```markdown
It seems the issue was answered, I'll close this now.
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

And in the last case, if:

* the issue has a label `waiting`
* the label was added _after_ the last comment
* the last comment was addded more than `691200` seconds (10 days) ago

...the GitHub action would close the issue with:

```markdown
Closing after 10 days of waiting for the additional info requested.
```

And again, by default, removing the label if there was a new comment written after adding the label.

### Delay

The delay can be configured using [anything supported by Pydantic's `datetime`](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types).

So, it can be an [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) period format (like `P3DT12H30M5S`), or the amount of seconds between the two dates (like `691200`, or 10 days) plus other options.

### Users and HTML comments

Before supporting labels, this GitHub action used HTML comments, so, you would write a comment like:

```markdown
Ah, you have to use a JSON string in the config.

<!-- issue-manager: answered -->
```

Then the comment would only show:

```markdown
Ah, you have to use a JSON string in the config.
```

And the GitHub action would read the label/keyword from that HTML comment.

To support external users adding these comments (even if they can't add labels to your repo), you can add a config `users` with a list of usernames allowed to add these HTML keyword comments.

In this case, the GitHub action will only close the issue if:

* the _last_ comment has the keyword/label
* it was written by a user in the `users` list in the `config` (or the owner of the repo)
* the time delay since the last comment is enough

### Remove label

You can also pass a config `remove_label` per keyword. By default it's `true`.

When someone adds a comment _after_ the label was added, then this GitHub action won't close the issue.

On top of not closing the issue, by default, it will remove the label. You can disable removing the label by setting `remove_label` to `false`.

### Defaults

By default, any config has:

* `users`: No users, only the repository owner (only applies to HTML comments).
* `delay`: A delay of 10 days.
* `message`: A message of:

```markdown
Assuming the original issue was solved, it will be automatically closed now.
```

* `remove_label`: True. If someone adds a comment after you added the label, it will remove the label from the issue.

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

jobs:
  issue-manager:
    runs-on: ubuntu-latest
    steps:
        - uses: tiangolo/issue-manager@0.2.0
        with:
            token: ${{ secrets.GITHUB_TOKEN }}
            config: >
                {
                    "answered": {
                        "delay": "P3DT12H30M5S",
                        "message": "It seems the issue was answered, I'll close this now."
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

If you have [Visual Studio Code](https://code.visualstudio.com) or other modern editor, you can create your JSON config by creating a JSON file, e.g. `config.json`.

Then writing the contents of your config in that file, and then copying the results.

But you can do it all with autocomplete :rocket:.

You can start your JSON config file with:

```JSON
{
    "$schema": "https://raw.githubusercontent.com/tiangolo/issue-manager/master/schema.json"
}
```

And then after you write a keyword and start its config, like `"answered": {}`, it will autocomplete the internal config keys, like `delay`, `users`, `message`. And will validate its contents.

It's fine to leave the `$schema` in the `config` on the `.yml` file, it will be discarded and won't be used as a label.

### A complete example

**Note**: you probably don't need all the configs, the examples above should suffice for most cases. But if you want to allow other users to use keywords/labels in HTML comments, or want to make the GitHub action _not_ remove the labels if someone adds a new comment, this can help as an example:

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

jobs:
  issue-manager:
    runs-on: ubuntu-latest
    steps:
        - uses: tiangolo/issue-manager@0.2.0
        with:
            token: ${{ secrets.GITHUB_TOKEN }}
            config: >
                {
                    "$schema": "https://raw.githubusercontent.com/tiangolo/issue-manager/master/schema.json",
                    "answered": {
                        "users": [
                            "tiangolo",
                            "dmontagu"
                        ],
                        "delay": "P3DT12H30M5S",
                        "message": "It seems the issue was answered, I'll close this now.",
                        "remove_label": false
                    },
                    "validated": {
                        "users": [
                            "tiangolo",
                            "samuelcolvin"
                        ],
                        "delay": 300,
                        "message": "The issue could not be validated after 5 minutes. Closing now.",
                        "remove_label": true
                    },
                    "waiting": {
                        "users": [
                            "tomchristie",
                            "dmontagu"
                        ],
                        "delay": 691200,
                        "message": "Closing after 8 days of waiting for the additional info requested.",
                        "remove_label": true
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
```

* The `cron` option means that the GitHub action will be run every day at 00:00 UTC.
* The `issue_comment` option means that it will be run with a specific issue when a comment is added.
    * This way, if there's a new comment, it can immediately remove any label that was added before the new comment.
* The `issues` option with a type of `label` will run it with each specific issue when you add a label.
    * This way you can add a label to an issue that was answered long ago, and if the configured delay since the last comment is enough the GitHub action will close the issue right away.

## Motivation

### Closing early

When I answer an issue, I like to give the original user some time to respond, and give them the chance to close the issue before doing it myself.

Or some times, I have to request additional info.

Sometimes, my answer didn't respond the real question/problem, and if I closed the issue immediately, it would end up feeling "impolite" to the user.

Moreover, if I closed the issue prematurely, there's a smaller chance that I (or someone else) will revisit it again to answer the real question/problem.

### Not closing

But then, if I leave the issue open after giving an answer, in many cases, the issue will keep open until I come back to close it, after many days.

Then, after that time (10 days, 30 days) and after seeing that there are no new comments, I write "I assume the problem is solved, I'll close this issue now".

But that requires me going through all the open issues again, one by one, check where I (or someone else) have already answered, typing that message, etc.

## Alternatives

One option would be to use a tool that closes stale issues, like [probot/stale](https://github.com/probot/stale), or the [Close Stale Issues Action](https://github.com/marketplace/actions/close-stale-issues).

But if the user came back explaining that my answer didn't respond to his/her problem, or giving the extra info requested, but I couldn't respond on time, the issue would still go "stale" and be closed.

## What Issue Manager does

This action allows the repo owner to add a label (e.g. `answered`) to an issue after answering. Or multiple labels with multiple configurations (multiple messages, delays, etc).

Then, this action, by running every night (or however you configure it) will, for each open issue:

* Check if the issue has one of the configured labels.
* Check if the label was added _after_ the last comment.
* If not, remove the label (configurable).
* Check if the current date-time is more than the configured *delay* to wait for the user to reply back (configurable).
* Then, if all that matches, it will add a comment with a message (configurable).
* And then it will close the issue.

Also, all that with the optional alternative using HTML comments.

It will also run after each comment or label added, with the specific issue that has the new comment or label (if you used the example configurations from above).

## Release Notes

### Latest Changes

* Add support for running immediately with each specific issue after a new comment or label is added.
* Add support for issue labels, detecting if a new comment was added after the label and removing the label.

### 0.1.1

* Fix incorrect input name. PR [#3](https://github.com/tiangolo/issue-manager/pull/3) by [@browniebroke](https://github.com/browniebroke).

### 0.1.0

* Initial release.

## License

This project is licensed under the terms of the MIT license.
