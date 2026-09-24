The project included the following components:

- Provisioned and configured a Linux-based server on DigitalOcean.
- Installed Docker and deployed the target application in a Docker container.
- Developed a Python monitoring script that periodically sends HTTP requests to the application using the requests library.
- Used the Python schedule library to run application and server health checks every five minutes.
- Validated the returned HTTP status code to determine whether the application was available.
- Sent an email notification when the application became unavailable or returned an unexpected HTTP response.
- Implemented automated recovery actions to restart the Docker container when the application failed.
- Tested the monitoring and recovery process by manually stopping and starting the Docker container.
- If the application fails to respond, the server is rebooted.

During testing, the monitored Jenkins server returned an HTTP 403 Forbidden response because unauthenticated requests were not authorized to access the requested resource. Therefore, the monitoring logic was configured to recognize http 403 response as normal operation.
