#!/bin/bash -eu

if test $# -ne 1; then
    echo "Missing version number"
    exit 1
fi

if ! command -v gbp &> /dev/null; then
    echo "Missing gbp command"
    echo "Install git-buildpackage"
    echo "  sudo apt-get install -yq git-buildpackage"
    exit 1
fi

declare -r VERSION_SPEC=$1
declare VERSION=""
declare -rx DEBFULLNAME=$(git config user.name)
declare -rx DEBEMAIL=$(git config user.email)

echo "Running tests"
tox --recreate > /dev/null
poetry version "${VERSION_SPEC}"
VERSION=$(poetry version --short)
echo "Releasing version $VERSION"
gbp dch \
    --new-version "$VERSION" \
    --distribution "$(lsb_release -sc)" \
    --debian-tag="%(version)s"\
    --no-git-author\
    --id-length=8\
    --spawn-editor=always
sed -i "s/^__version__ = .*$/__version__ = '$VERSION'/g" rchat/__init__.py
git commit -am "Version $VERSION"
git tag -a "$VERSION" -m "Version $VERSION"
echo "Created tag $VERSION"
echo "Don't forget to: "
echo " git push origin master $VERSION"
