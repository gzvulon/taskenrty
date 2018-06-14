Taskfile: Make-like Entrypoints
===============================

The entrypoints are placed into [Taskfile](Taskfile.yml)
wich are processed by [task](https://github.com/go-task/task).

Entrypoints are still defined by make colon notaion:
```yaml
  pack-clean:
    desc: clean package files
    cmds:
      - rm -rf dist
      - rm -rf refstore.egg-info

  deps-install:
    desc: install dependancies
    cmds:
      - pipenv install --skip-lock
```
However the baseline syntax is yaml with some
simple ansible-like dsl.

Usage
-----
try: `task --list` to see available tasks


Advantages
----------
- **cross platform**
    - run on windows linux and osx
    - have easy os specific customization
- **one file depoy**
    - just put binary into path and it working
- **bash specia** charachter escaping
    - copy paste or even type-first
    - using rich YAML multiline and interpolation syntax.


Links
-----
* [Download Release](https://github.com/go-task/task/releases)
* [Documentation](https://github.com/go-task/task#task---a-task-runner--simpler-make-alternative-written-in-go)