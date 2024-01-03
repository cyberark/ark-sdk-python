#!/usr/bin/env bash
set -e

ORIGINAL_PACKAGE=$1
START_DIR=$(pwd)
TEMP_DIR=$(mktemp -d)
WORKING_WHEEL=$TEMP_DIR/package.whl
FINAL_PACKAGE=$(echo $ORIGINAL_PACKAGE | rev | cut -d"-" -f4- | rev)-py3-none-any.whl

if [[ ! -f "$ORIGINAL_PACKAGE" ]]; then
  echo "File not found at path $1"
  exit 1
fi

cp $ORIGINAL_PACKAGE $WORKING_WHEEL

cd $TEMP_DIR

mkdir unzipped
unzip $WORKING_WHEEL -d unzipped

WHEEL_FILE=$(find unzipped -name "WHEEL")

grep -v '^Root-Is-Purelib' $WHEEL_FILE > $WHEEL_FILE.tmp
grep -v '^Tag' $WHEEL_FILE.tmp > $WHEEL_FILE
rm $WHEEL_FILE.tmp

echo "Root-Is-Purelib: true" >> $WHEEL_FILE
echo "Tag: py3-none-any" >> $WHEEL_FILE

cat $WHEEL_FILE

cd unzipped
zip -r ../universal_package.whl *
cd ..

cd $START_DIR

cp $TEMP_DIR/universal_package.whl $FINAL_PACKAGE
rm $ORIGINAL_PACKAGE
