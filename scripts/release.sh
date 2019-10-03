#!/bin/bash
# nothing to see here, just a utility i use to create new releases ^_^

VERSION_FILE=$(dirname "${BASH_SOURCE[0]}")/../sdcard/rootfs/root/pwnagotchi/scripts/pwnagotchi/version.py
echo "version file is $VERSION_FILE"
CURRENT_VERSION=$(cat $VERSION_FILE | grep version | cut -d"'" -f2)
TO_UPDATE=(
  $VERSION_FILE
)

echo -n "current version is $CURRENT_VERSION, select new version: "
read NEW_VERSION
echo "creating version $NEW_VERSION ...\n"

for file in "${TO_UPDATE[@]}"; do
  echo "patching $file ..."
  sed -i.bak "s/$CURRENT_VERSION/$NEW_VERSION/g" "$file"
  rm -rf "$file.bak"
  git add $file
done

git commit -m "releasing v$NEW_VERSION"
git push
git tag -a v$NEW_VERSION -m "release v$NEW_VERSION"
git push origin v$NEW_VERSION

echo
echo "All done, v$NEW_VERSION released ^_^"