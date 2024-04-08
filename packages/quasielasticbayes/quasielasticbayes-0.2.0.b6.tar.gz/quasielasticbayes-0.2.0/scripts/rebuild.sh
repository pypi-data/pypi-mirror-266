./scripts/clean.sh

# Build the project wheel
python setup.py bdist_wheel

# Build the source tarball
python setup.py sdist
