# CI/CO Fix Process

This document explains how to fix CI/CO issues in the BFRPG MUD project so that we can stop using `--no-verify` when committing changes.

## Overview of Issues

Our pre-commit hooks are failing due to several issues:

1. **Formatting issues** (black, isort)
2. **Unused imports** (F401)
3. **Line length issues** (E501)
4. **Bare except statements** (E722)
5. **String formatting issues** that cause parsing errors in black

## Fix Process

We've created scripts to help fix these issues:

1. `fix_selected_files.py` - Formats files one by one using black and isort
2. `fix_flake8_issues.py` - Fixes common flake8 issues like unused imports and bare excepts

### Step 1: Install Required Tools

Make sure you have the required Python packages installed:

```bash
pip install black isort flake8
```

### Step 2: Manually Fix Parsing Issues

Before running the formatters, check for and fix string concatenation issues:

1. Look for lines containing `" +` followed by strings on the next line
2. Replace these with proper multiline strings or single strings
3. Example fix:
   ```python
   # Before:
   logger.info(
       " +
       "This is a broken string"with concatenation issues"
   )
   
   # After:
   logger.info(
       "This is a fixed string with concatenation issues"
   )
   ```

### Step 3: Run the File-by-File Formatting Script

Run the script to format files one at a time:

```bash
python fix_selected_files.py
```

This approach is better than trying to format all files at once, as it allows us to:
- Process files individually
- See which specific files are failing
- Fix issues incrementally

### Step 4: Fix Flake8 Issues

For files that pass basic formatting, run the flake8 fix script:

```bash
python fix_flake8_issues.py
```

### Step 5: Review and Test

1. Review the changes with `git diff`
2. Run a test commit to see if pre-commit hooks pass:
   ```bash
   git add -A
   git commit -m "Test commit after fixes"
   ```

## Long-Term Solutions

To maintain clean code moving forward:

1. **Use an IDE with linting** - Configure VSCode, PyCharm, etc. to show formatting issues in real time
2. **Run pre-commit manually** during development:
   ```bash
   pre-commit run --all-files
   ```
3. **Add CI checks** to enforce code standards in pull requests

## Common Errors and Fixes

### String Concatenation Issues
- Replace `" + "string"` patterns with properly formatted strings
- For long strings, use parentheses to get implicit line continuation:
  ```python
  long_string = (
      "This is a very long string that will be "
      "automatically concatenated by Python"
  )
  ```

### F401 (Unused Import)
- Remove the unused import
- Or use it in your code if it's actually needed

### E501 (Line too long)
- Break the line at a logical point
- Use Python's implicit line continuation within parentheses, brackets, or braces

### E722 (Bare except)
- Replace `except:` with `except Exception:`
- Better yet, catch specific exceptions: `except ValueError:`, etc.

### E712 (Comparison to True/False)
- Replace `if x == True:` with `if x is True:` or `if x:`
- Replace `if x == False:` with `if x is False:` or `if not x:` 