# ClangTidyReporter
Run clang-tidy and generate a nice looking report of the results.

## Presentation

Python script running clang-tidy on several directories (tested on Windows only).
Results are analyzed, categorized, and displayed in html pages.
A diff is done wih previous run, only if the previous run has been done yesterday.

This script does in this order:

1. Run clang-tidy on the specified files
2. Generate the report in html format

## Prerequisite

1. Clang-tidy
2. Python 3.5 or above

## Usage

`python main.py [-h] [-c|--checks CLANG_CHECKS] [-p|--compilation_db PATH_COMPILATION_DB] [-o|--output_dir OUTPUT_DIR] [-f|--files FILES,FILES...] [-d|--directories DIR,DIR,DIR,...]`

**Example:** 

`python main.py --checks " -*,misc-*,modernize-*,bugprone-*" -p "./source" --ouput_dir "output" -f "./source/file1.c,./source/file2.cpp" -d "./source/dir1/,./source/dir2/"`

Run clang-tidy on the directories ./source/dir1 and ./source/dir2 + the files ./source/file1.c and ./source/file2.cpp with the clang checks "misc-*,modernize-*,bugprone-*".
Output will be logged in the directory "output".

## Screenshots

Index page

![screen1](https://github.com/bourdibay/ClangTidyReporter/blob/master/screenshots/index.png)

Categorisation by files

![screen2](https://github.com/bourdibay/ClangTidyReporter/blob/master/screenshots/files.png)

Categorisation by type of warning

![screen3](https://github.com/bourdibay/ClangTidyReporter/blob/master/screenshots/categories.png)
