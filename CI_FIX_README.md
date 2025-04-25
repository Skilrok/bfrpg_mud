# CI/CO Fix Process

This document explains how to fix CI/CO issues in the BFRPG MUD project so that we can stop using `--no-verify` when committing changes.

## Overview of Issues

Our pre-commit hooks are failing due to several issues:

1. **Formatting issues** (black, isort)
2. **Unused imports** (F401)
3. **Line length issues** (E501)
4. **Bare except statements** (E722)
5. **Other flake8 issues**

## Fix Process

We've created two scripts to help fix these issues:

1. `fix_ci_issues.py` - Formats all Python files using black and isort
2. `fix_flake8_issues.py` - Fixes common flake8 issues like unused imports and bare excepts

### Step 1: Install Required Tools

Make sure you have the required Python packages installed:

```bash
pip install black isort flake8
```

### Step 2: Run the Formatting Script

Run the first script to format all Python files in the project:

```bash
python fix_ci_issues.py
```

This will run `black` and `isort` on all Python files, making them consistent with the code style requirements.

### Step 3: Fix Flake8 Issues

Run the second script to fix common flake8 issues:

```bash
python fix_flake8_issues.py
```

This script will:
- Remove unused imports
- Fix bare except statements
- Attempt to break long lines

### Step 4: Review Changes

Review the changes made by the scripts before committing:

```bash
git diff
```

### Step 5: Manually Fix Remaining Issues

Some issues may need manual fixing:

1. **Complex line length issues** - The script may not be able to fix all long lines
2. **F-string missing placeholders** (F541) - These need manual review
3. **E712** (comparison to True/False) - Replace `if x == True` with `if x is True` or just `if x`

### Step 6: Test Commit

Try a test commit to see if the pre-commit hooks pass:

```bash
git add -A
git commit -m "Test commit after fixes"
```

If this passes without errors, the fixes were successful!

## Ongoing Maintenance

To maintain clean code and avoid future CI/CO issues:

1. **Use an IDE with linting** - Configure VSCode, PyCharm, etc. to show linting errors
2. **Run pre-commit manually** before committing:
   ```bash
   pre-commit run --all-files
   ```
3. **Fix issues as you code** rather than letting them accumulate

## Common Errors and Fixes

### F401 (Unused Import)
- Remove the unused import
- Or use it in your code if it's actually needed

### E501 (Line too long)
- Break the line at a logical point
- Use Python's implicit line continuation within parentheses, brackets, or braces
- Use explicit line continuation with backslashes (less preferred)

### E722 (Bare except)
- Replace `except:` with `except Exception:`
- Better yet, catch specific exceptions: `except ValueError:`, etc.

### E712 (Comparison to True/False)
- Replace `if x == True:` with `if x is True:` or `if x:`
- Replace `if x == False:` with `if x is False:` or `if not x:` 