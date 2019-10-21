# Issue Manager

Automatically close issues that have a **keyword mark** (an HTML comment) in the **last comment** in the issue, by a group of predefined **users**, after a **custom delay**.

## Features

You can set multiple configurations, each with a different:

* Keyword.
* Set of users (multiple per keyword).
* Message.

## How to use

You first need to have access to [GitHub actions](https://github.com/features/actions) (in beta as of 2019-10).

Install this GitHub action by creating a file in your repo at `.github/workflows/main.yml`.

A minimal example could be:

```yml
on:
  schedule:
  - cron: "0 0 * * *"

jobs:
  issue-manager:
    runs-on: ubuntu-latest
    steps:
    - uses: tiangolo/issue-manager@master
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        config: '{"answered": {}}'
```

Then, whenever the repo owner answers an issue with a comment, he/she can add an HTML comment with a mark, e.g.:

```markdown
Ah, you have to use a JSON string in the config.

<!-- issue-manager: answered -->
```

Then the comment will only show:

```markdown
Ah, you have to use a JSON string in the config.
```

But after 10 days, if no one has added a new comment, the GitHub action will write:

```markdown
Assuming the original issue was solved, this issue will be automatically closed now.
```

And then it will close the issue.

## Config

If you check, the `config` in that file `main.yml` has a `string`, and inside of the string there's a whole JSON configuration:

```JSON
{"answered": {}}
```

...but it's all inside a `string`:

```YAML
'{"answered": {}}'
```

This JSON configuration (inside a string) is what allows to add multiple custom keywords, with different users, and different messages.

Imagine this JSON config:

```JSON
{
    "answered": {
        "users": [
            "tiangolo",
            "dmontagu"
        ],
        "delay": "P3DT12H30M5S",
        "message": "It seems the issue was answered, I'll close this now."
    },
    "validated": {
        "users": ["tiangolo", "samuelcolvin"],
        "delay": 300,
        "message": "The issue could not be validated after 5 minutes. Closing now."
    },
    "waiting": {
        "users": ["tomchristie", "dmontagu"],
        "delay": 691200,
        "message": "Closing after 8 days of waiting for the additional info requested."
    }
}
```

In this case, if the last comment in an open issue has a keyword of `answered`, as in:

```markdown
<!-- issue-manager: answered -->
```

...and was written by one of [@tiangolo](http://github.com/tiangolo) or [@dmontagu](https://github.com/dmontagu).

...and it has already passed 3 days, 12 hours, 30 minutes and 5 seconds or more.

...it will close the issue with a message of:

```markdown
It seems the issue was answered, I'll close this now.
```

---

But then, if the issue had a last comment with a keyword of `validated`:

```markdown
<!-- issue-manager: validated -->
```

...was written by [@tiangolo](http://github.com/tiangolo) or [@samuelcolvin](http://github.com/samuelcolvin).

...and was written more than `300` seconds ago (5 minutes).

...it will close it with a message:

```markdown
The issue could not be validated after 5 minutes. Closing now.
```

---

And in the last case, using a keyword of `waiting`:

```markdown
<!-- issue-manager: waiting -->
```

...written by [@tomchristie](http://github.com/tomchristie) or [@dmontagu](http://github.com/dmontagu).

...after `691200` seconds (10 days).

...will close with:

```markdown
Closing after 10 days of waiting for the additional info requested.
```

### Delay

The delay can be configured using [anything supported by Pydantic's `datetime`](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types).

So, it can be an [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) period format (like `P3DT12H30M5S`), or the amount of seconds between the two dates (like `691200`, or 10 days) plus other options.

### Defaults

By default, any config has:

* `users`: No users, only the repository owner.
* `delay`: A delay of 10 days.
* `message`: A message of:

```markdown
Assuming the original issue was solved, this issue will be automatically closed now.
```

### Config in the action

To use that same JSON config from above, you would have to put it on a single `string` inside the GitHub Action config (`main.yml`).

But YAML supports multiline strings using `>`.

Just make sure to indent everything to be part of the same string.

So, you can put all the config with:

```yml
on:
  schedule:
  - cron: "0 0 * * *"

jobs:
  issue-manager:
    runs-on: ubuntu-latest
    steps:
    - uses: tiangolo/issue-manager@master
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        config: >
            {
                "answered": {
                    "users": [
                        "tiangolo",
                        "dmontagu"
                    ],
                    "delay": "P3DT12H30M5S",
                    "message": "It seems the issue was answered, I'll close this now."
                },
                "validated": {
                    "users": ["tiangolo", "samuelcolvin"],
                    "delay": 300,
                    "message": "The issue could not be validated after 5 minutes. Closing now."
                },
                "waiting": {
                    "users": ["tomchristie", "dmontagu"],
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

## Motivation

### Closing early

When I answer an issue, I like to give the original user some time to respond, and give him/her the chance to close the issue before doing it myself.

Or some times, I have to request for additional info.

Some times, my answer didn't respond the real question/problem, and if I closed the issue immediately, it would end up feeling "impolite" to the user.

Moreover, if I closed the issue prematurely, there's a smaller chance that I (or someone else) will revisit it again to answer the real question/problem.

### Not closing

But then, if I leave the issue open after giving an answer, in many cases, the issue will keep open until I come back to close it, after many days.

Then, after that time (10 days, 30 days) and after seeing that there are no new comments, I write "I assume the problem is solved, I'll close this issue now".

But that requires me going through all the open issues again, one by one, check where I (or someone else) have already answered, typing that message, etc.

## Alternatives

One option would be to use a tool that closes stale issues, like [probot/stale](https://github.com/probot/stale), or the [Close Stale Issues Action](https://github.com/marketplace/actions/close-stale-issues).

But if the user came back explaining that my answer didn't respond to his/her problem, or giving the extra info requested, but I couldn't respond on time, the issue would still go stale and be closed.

## What Issue Manager does

This action allows the repo owner (and a configurable set of other users) to add a mark with a keyword to a comment in an issue (it's an HTML comment).

Something like:

```html
<!-- issue-manager: answered -->
```

That won't be visible in the comment, but it will still be there and this action will be able to read it.

Then, this action, by running every night (or however you configured it) will, for each of the open issues:

* Check if the *last comment* has a keyword like that (configurable).
    * It's important that it checks the last comment, that way, if the original issue creator or someone else wrote some extra comments (giving extra data, clarifying information, etc), it won't close it prematurely.
* Check if the keyword mark in that last comment was added by the repo owner or an authorized user (configurable).
* Check if the current date is more than the configured *delay* to wait for the user to reply back or close the issue (configurable).
* Then, if all that matches, it will add a comment with a message (configurable).
* And then it will close the issue.

## License

This project is licensed under the terms of the MIT license.
