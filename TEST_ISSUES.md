# Test Issues to Resolve

The following issues need to be addressed to fix the skipped tests:

## Authentication Tests
- The authentication fixtures in `tests/test_authentication.py` need to be updated.
- Password verification during login needs to work properly in test fixtures.
- The `verify_password` function needs a fix for the test environment.

## User Registration Tests
- Duplicate user/email checking needs to be fixed in the test environment.
- Tests need to use a completely separate database transaction for each test.
- The `test_register_duplicate_username` and `test_register_duplicate_email` tests need to be updated.

## Hireling Tests
- The hire_hireling endpoint needs to be fixed to work in test environment.
- The reward_hireling endpoint is returning 404, needs to be fixed.
- The loyalty_decrease_unpaid endpoint needs to be fixed.

## User Flow Tests
- The complete user flow test needs to be updated to work with test database.
- Verification of user creation in separate database transactions.

## General Issues
- SQLAlchemy deprecation warning about declarative_base() needs to be fixed.
- Tests are currently using different databases and endpoints leading to conflicts.
- Authentication override needs to be properly managed between tests.

## Next Steps
1. Update the auth.py router to be consistent with the users.py router or vice versa.
2. Implement proper transaction isolation in tests.
3. Fix the hireling endpoints to work with the test database.
4. Standardize the authentication approach across the app.
5. Fix the bcrypt version warning by upgrading/downgrading as needed. 