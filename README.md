# repro\_clipper

> Clips down a test case ("repro")

This small webapp enables near-automatic minification of testcases that behave differently across browsers.

repro\_clipper uses a divide-and-conquer-ish approach: delete large sections, let the human decide whether the
bug still occurs, and iterate. This enables users to rapidly minify testcases from megabytes down to a handful
of lines, which then can be minified by hand.

repro\_clipper does not support automatic reloading, because that would change the page content, and potentially
interfere with the bug itself.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [TODOs](#todos)
- [NOTDOs](#notdos)
- [Contribute](#contribute)

## Install

`python3 -m venv .venv && source .venv/bin/activate && pip install -U pip && pip install -r requirements.txt`

(i.e. just install `requirements.txt`, no further config required.)

You might also want to install the plugin "Save Page WE" for Firefox, which is
able to export most websites as a single HTML file, including all images,
scripts, styles, CSS state. However, JS state is lost, but this is often not
relevant.

## Usage

1. Start repro\_clipper: `./manage.py runserver`
2. Open it in any observer browser: http://127.0.0.1:8000/
3. Upload (TODO) the HTML file you'd like to minify/clip
4. Open (TODO) the project-and-state-specific URL (given by repro\_clipper) in various test browsers (e.g. Firefox and [ladybird](https://github.com/LadybirdBrowser/ladybird/))
5. Click (TODO) "Bug present" or "Bug absent" in repro\_clipper
6. Refresh the new page in your test browsers
7. Repeat steps 5 and 6 until the filesize is very small, and manual minification is easier again

## TODOs

- Everything, lol

## NOTDOs

Here are some things this project will definitely not support:
* Automatic bug detection
* Anything AI

Things I *probably* won't do, because this is just about bulk clipping as a first pass:
* Syntax checking, parsing, etc.

## Contribute

Feel free to dive in! [Open an issue](https://github.com/BenWiederhake/repro_clipper/issues/new) or submit PRs.
