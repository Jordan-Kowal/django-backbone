# TODO

### Project wide:
- Update README.md
- Setup admins
- Rename server and server_config into django_backbone

### Core
- Management command to start new app
- Should only be used to share utilities

### Contact
- Update tests so that they check the logger AND stop writing in them for real
- Add test for logs in contact actions

### Healthchecks
- Create HealthChecks app

### Security
- Create security app
- Update tests so that they check the logger AND stop writing in them for real
    - network rule actions
    - network rule methods
- Add tests for logs in network rule models

### Users API
- Create new User model
    - Update model and tests
    - Update actions and tests
    - Update settings
    - Update calls throughout the app
- Add model to log auth attempts (fail, success, IP, datetime, user if known)
    - Also write in the logfile
- Login service that returns session cookie
    - Block consecutive fails
    - log attempts. if mfa, success is logged after step 2m bu failure can be both steps
- Add option for no simultaneous connection
    - Set in django settings
    - Used during the login to kill other cookies
- Add MFA option
    - Setup at the user level
    - Value stored on the user, encrypted like a password
    - Email or SMS
    - If active, login does not login but send MFA
    - Limit for a user to avoid spams
        - Limit per days regardless of success
        - Limit consecutive failures
- Service to handle MFA tries
    - Block consecutive fails
- Add trusted for 30 days on a machine. Check the `Agent` data in the request
- Logout service that kills current session
- Status service to know if we are connected and various session info

#### Emails
- Rework css into SASS with variables for easier setup
- Simplify css/design for easier setup
- Update the emails
    - Users
        - Verify
        - Welcome
        - Password reset
        - Password update
    - Contact
        - Admin alert
        - User alert
        - Config either in 

#### Packages
- CRON package
   - Setup NetworkRule automatic clear cron
   - Setup Contact cleanup cron
   - Setup log file cleanup
- Test runner
