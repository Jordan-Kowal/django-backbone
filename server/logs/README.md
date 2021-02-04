# Logs

We currently have 4 loggers that write their output into files.
They are all **RotatingFileHandler** meaning that:
- Once the file reaches a certain size, it will create a new one
- The previous file will be kept based on the maximum number of files set
- The newest files replace the oldest

Logs are split into different log files to make it easier to find what you are looking for.
The available log files are:
- **console.log**: Default file for everything
- **debug.log**: File to be used for debug messages and any possible helpers
- **healthchecks.log**: File dedicated to healthchecks information, from the api/healthchecks services
- **security.log**: For anything related to security, like user logins, IP white/blacklisting, etc
