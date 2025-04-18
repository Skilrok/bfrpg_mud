# Test Issues to Resolve

The following issues have been addressed:

## Authentication Tests
- ✅ The authentication fixtures in `tests/test_authentication.py` have been updated.
- ✅ Password verification during login now works properly in test fixtures.
- ✅ The `verify_password` function has been fixed for the test environment.
- ✅ The skipped tests `test_token_route` and `test_protected_route_with_token` have been fixed and now work properly.
- ✅ Fixed client parameter missing from `test_protected_route_without_token` and `test_protected_route_with_invalid_token` tests.
- ✅ Fixed duplicate test functions in the test file that were causing conflicts.

## User Registration Tests
- ✅ Duplicate user/email checking has been fixed in the test environment.
- ✅ Tests now use a completely separate database transaction for each test.
- ✅ The `test_register_duplicate_username` and `test_register_duplicate_email` tests have been fixed.

## Hireling Tests
- ✅ The hire_hireling endpoint has been fixed to work in the test environment.
- ✅ The reward_hireling endpoint is now working correctly.
- ✅ The loyalty_decrease_unpaid endpoint now works properly.
- ✅ We've resolved the "no such table: hirelings" errors with a file-based SQLite database.

## User Flow Tests
- ✅ The complete user flow test now works with the test database.
- ✅ Verification of user creation in separate database transactions now works correctly.

## General Issues
- ✅ SQLAlchemy deprecation warning about declarative_base() has been fixed.
- ✅ Tests now use a centralized test database configuration to avoid conflicts.
- ✅ Authentication override is now properly managed between tests.
- ✅ The bcrypt version warning has been fixed by upgrading/downgrading as needed.

## Summary of Changes Made
1. ✅ Updated the `auth.py` router to be consistent with the `users.py` implementation.
2. ✅ Implemented proper transaction isolation in tests using a file-based SQLite database.
3. ✅ Fixed the hireling endpoints to ensure they return Pydantic models correctly.
4. ✅ Standardized the authentication approach across the app.
5. ✅ Fixed the bcrypt version warning.
6. ✅ Centralized test fixtures in conftest.py for better reuse.
7. ✅ Made test database setup and teardown more robust.
8. ✅ Fixed Pydantic model conversions in all endpoints.

## Future Improvements
1. Consider using a dedicated test configuration for handling database access.
2. Add more comprehensive test coverage for character creation and management.
3. Implement database migrations with Alembic to keep schema in sync.
4. Consider using async SQLAlchemy for better performance in non-test environments.
5. Implement proper error reporting and logging framework.

## Next Steps
1. ✅ Update the auth.py router to be consistent with the users.py router or vice versa.
2. ✅ Implement proper transaction isolation in tests - resolved by using file-based SQLite database with proper setup.
3. ✅ Fix the hireling endpoints to work with the test database.
4. ✅ Standardize the authentication approach across the app.
5. ✅ Fix the bcrypt version warning.

## Remaining Issues
1. ✅ In-memory SQLite database issue has been resolved by using file-based SQLite databases with proper initialization.
2. ✅ Hireling tests are now passing with the file-based SQLite database approach.
3. ✅ Database transaction isolation has been improved in the conftest.py fixture.
4. ✅ All skipped tests are now enabled and passing.
5. ✅ Fixed the auth router to correctly use `from_orm` for Pydantic model conversion.
6. ✅ Fixed test_basic_hirelings.py to create the test user when needed.
7. ✅ Fixed test_user_flow.py to use the proper user registration approach.

All tests are now passing! The system is ready for the next phase of development.

All planned tasks have been completed, and the application is ready for the next phase of development.
