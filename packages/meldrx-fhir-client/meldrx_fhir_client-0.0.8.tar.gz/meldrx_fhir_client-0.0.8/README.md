# meldrx-client-py
MeldRx Python Client

## Setup/Installation
- Create `config.py` (use `config.example.py` as an example)

## Unit Tests
`python3 -m unittest`

## Publish (on test registry)
1. Update version in `setup.py`
2. `python3 setup.py sdist bdist_wheel`
3. `twine upload --repository testpypi dist/*`

## Publish (on main registry)
1. Update version in `setup.py`
2. `python3 setup.py sdist bdist_wheel`
3. `twine upload dist/*`