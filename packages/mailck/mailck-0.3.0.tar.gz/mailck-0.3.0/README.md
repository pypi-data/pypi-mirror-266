# README

mailck is a simple mail check utility, currently supporting IMAP, designed with the following in mind:

- light: small size and resource usage
- low dependencies: low or no external dependencies
- terminal-focused: terminal usage focused (input and output) - primarily focused on usage through conky


## Latest Changes

- changed --version to use importlib.metadata


### Notices

- it does not make much sense to run this more frequently than every 10s as connecting takes ~1-2s


### Features

- no configuration: install and run
- supports password or password-cmd (getting a password from an external command such as spw)
- scriptable: designed to be ran from conky, cron, or the command line
- minimal: around 250 lines of code, no dependencies
- safe: the code is clean and easy to review with no dependencies so you can easily review to see exactly what it does


### Requirements

- python


### Overview

mailck is a utility to check mail. The default usage simply returns a count of new (unseen) messages but you can have it return a summary (showing From, Date, and Subject) of the messages if needed. See `--help` and the Examples section below for more details.

We use mailck daily via conky to check several mail accounts. mailck was designed for this purpose and built because we could not find a simple, trustworthy application for this that is currently maintained. mailck has no dependencies so keeping it up-to-date is simple but we strive to keep the application functioning as designed and to address any issues quickly.


### Comments / Issues / Feedback

If you find an issue, have a question, or would like a feature added please create an issue as we would be happy to hear from you.

- [issues](https://gitlab.com/drad/mailck/-/issues)


### Install

We recommend using [pipx](https://github.com/pypa/pipx). To install:

- with pipx: `pipx install mailck`
- with pip: `pip install --user mailck`


### Usage

Using mailck is straightforward, see `--help` for details or the Examples section below for example usage.

By default, mailck uses LOG_LEVEL=WARNING which shows minimal extra info. If you are having issues you may want to increase application verbosity by setting the LOG_LEVEL to 'DEBUG'. You can do this by setting a LOG_LEVEL envvar (e.g. `LOG_LEVEL='DEBUG' mailck --server mail.example.com --port 993 --username me@example.com --password='my-password'`). Valid values for LOG_LEVEL are as follow: [CRITICAL|ERROR|WARNING|INFO|DEBUG] (suggest WARNING).


### Examples

- Terminal Usage:
    - basic: `mailck --server mail.example.com --port 993 --username me@example.com --password='my-password'`
        + output: `0`  # indicating no new email
    - basic with password-cmd: `mailck --server mail.example.com --port 993 --username me@example.com --password-cmd='spw -g mail/example@x -u'`
        + output: `0`  # indicating no new email
    - add prefix and suffix with password-cmd: `mailck --server mail.example.com --port 993 --username me@example.com --password-cmd='spw -g mail/example@x -u' --prefix='example@x: ' --suffix=" (new)"`
        + output: `example@x: 0 (new)`   # indicating no new email
    - basic with password-cmd returning message summary: `mailck --server mail.example.com --port 993 --username me@example.com --password-cmd='spw -g mail/example@x -u' -m true --prefix='Total: ' --suffix=' (new)'`
        + output:
            ```
            SA <sa@adercon.com>, 2023-12-20 20:58, Example Email 1
            SA <sa@adercon.com>, 2023-12-20 20:59, Example Email 2
            Total: 2 (new)
            ```
- conky usage:
    ```
    conky.text = [[
    ...
    Mail:
    - devops@ac: ${texeci 60 mailck --server mail.example.com --username me@example.com --password-cmd='spw -g mail/me@ac -u' --suffix=' (new)'}
    - dr@ac:     ${texeci 60 mailck --server mail.example.com --username dr@example.com --password-cmd='spw -g mail/dr@ac -u' --suffix=' (new)'}
    ...
    ]]
    ```
    will produce something like the following in conky:
    ```
    ...
    Mail:
    - devops@ac: 2 (new)
    - dr@ac      0 (new)
    ...
    ```


### Links

- [source code](https://gitlab.com/drad/mailck)
- [issues](https://gitlab.com/drad/mailck/-/issues)
