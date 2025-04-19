# Changelog

## 2025-04-19
### Added
- Enhanced movement command implementation to use the new Exit model
- Added support for hidden and locked exits in the movement system
- Updated the "look" command to display exits from both legacy and new Exit models
- Created database migration scripts to add missing columns
- Added admin user functionality
- Created debugging scripts to check database schema and fix issues

### Fixed
- Fixed authentication for admin login
- Fixed issues with command registry causing server startup errors
- Added missing is_admin column to users table

### Pending
- See TODO.md for remaining tasks 