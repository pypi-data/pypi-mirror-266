# Keystone API

[![](https://app.codacy.com/project/badge/Grade/9ee06ecdddef4f75a8deeb42fa4a9651)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

The backend REST API for the Keystone allocation management dashboard.

## Installation

To install the Keystone API, choose from one of the following options.

### Using Docker

Using Docker is the recommended method for building and deploying application instances.
The most recent image can be pulled from the GitHub container registry:

```bash
docker pull ghcr.io/pitt-crc/keystone-api
docker run -p 8000:8000 ghcr.io/pitt-crc/keystone-api
```

Alternatively, the latest development version can be built directly from source:

```bash
git clone https://github.com/pitt-crc/keystone-api
docker build -t keystone-api:develop keystone-api
docker run -p 8000:8000 keystone-api:develop
```

The container will automatically launch a fully functioning API server.
If the container is being launched for the first time, you will need to manually create the first user account.
To do so, execute the following command with the appropriate container name and follow the onscreen prompts.

```bash
docker exec -it [CONTAINER NAME] keystone-api createsuperuser
```

The default container instance is *not* suitable for full production out of the box.
See the [Settings](#settings) section for a complete overview of configurable options and recommended settings.

### Installing from PyPI

Installing the Keystone-API Python package is only recommended as a fallback for situations where using Docker is not feasible.
Before proceeding with the installation, the following dependencies must be met:

- A running Celery instance
- A running Celery Beat instance
- A running Redis database

The following dependencies are optional:

- A running PostgreSQL database (if using PostgreSQL instead of SQLite)
- LDAP development binaries (if using LDAP authentication)

In keeping with best practice, it is recommended to install packages into a dedicated virtual environment:

```bash
conda create -n keystone-api python=3.11
conda activate keystone-api
```

The package and its dependencies are pip installable.

```bash
pip install keystone-api
```

If the installation was successful, the packaged CLI tool will be available in your working environment.
Use the `--help` option to view the available commands.

```bash
keystone-api --help
```

The following example will set up the project database, create an admin user account, and launch the
API server in debug mode. As a general rule, debug mode should **never** be enabled in production.

```bash
keystone-api migrate
keystone-api createsuperuser
DEBUG=true keystone-api runserver
```

#### Enabling Autocomplete

The `keystone-api` utility does not support tab autocompletion by default.
To enable this feature, use the `enable_autocomplete` command:

```bash
keystone-api enable_autocomplete
```

## Settings

Application settings are configurable as environmental variables.
Individual settings are listed below by category and use case.

### Security

Improperly configuring these settings can introduce dangerous vulnerabilities and may damage your production deployment.
Administrators should adhere to the following general guidelines:

- Ensure your deployment is isolated behind a web proxy with proper HTTPS handling
- Always define the `SECURE_ALLOWED_HOSTS` list using a restrictive collection of domain patterns
- Avoid issuing session/CSRF tokens over unsecured connections by enabling `SECURE_SESSION_TOKENS`
- Always use a secure `SECURE_SECRET_KEY` value to ensure proper request signing across application instances/restarts
- Consider using HTTP Strict Transport Security (HSTS) to enforce the use of HTTPS

The `SECURE_SECRET_KEY` value may be changed at any given time. However, doing so may invalidate any active user
sessions and require users to reauthenticate.

| Setting Name              | Default Value            | Description                                                   |
|---------------------------|--------------------------|---------------------------------------------------------------|
| `SECURE_SECRET_KEY`       | Randomly generated       | Secret key used to enforce cryptographic signing.             |
| `SECURE_ALLOWED_HOSTS`    | `localhost,127.0.0.1`    | Comma-separated list of accepted host/domain names.           |
| `SECURE_SSL_REDIRECT`     | `False`                  | Automatically redirect all HTTP traffic to HTTPS.             |
| `SECURE_SESSION_TOKENS`   | `False`                  | Only issue session/CSRF tokens over secure connections.       |
| `SECURE_CSRF_ORIGINS`     | `[]`                     | Domains (with protocol) to accept CSRF headers from.          |
| `SECURE_HSTS_SECONDS`     | `0` (Disabled)           | HSTS cache duration in seconds.                               |
| `SECURE_HSTS_SUBDOMAINS`  | `False`                  | Enable HSTS for subdomains.                                   |
| `SECURE_HSTS_PRELOAD`     | `False`                  | Enable HSTS preload functionality.                            |

### General Configuration

The following settings configure varius aspects of Keystone's backend behavior.

Keystone uses various static files to facilitate operation and support user requests.
By default, these files are stored in subdirectories of the installed application directory (`<app>`).

| Setting Name              | Default Value             | Description                                                                                       |
|---------------------------|---------------------------|---------------------------------------------------------------------------------------------------|
| `CONFIG_TIMEZONE`         | `UTC`                     | The application timezone.                                                                         |
| `CONFIG_STATIC_DIR`       | `<app>/static_files`      | Where to store internal static files required by the application.                                 |
| `CONFIG_UPLOAD_DIR`       | `<app>/upload_files`      | Where to store file data uploaded by users.                                                       |
| `CONFIG_LOG_RETENTION`    | 30 days                   | How long to store log records in seconds. Set to 0 to keep all records.                           |
| `CONFIG_LOG_LEVEL`        | `WARNING`                 | Only record logs above this level (`CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, or `NOTSET`). |

### API Throttling

API settings are used to throttle incoming API requests against a maximum limit.
Limits are specified as the maximum number of requests per `day`, `minute`, `hour`, or `second`.

| Setting Name              | Default Value            | Description                                                   |
|---------------------------|--------------------------|---------------------------------------------------------------|
| `API_THROTTLE_ANON`       | `1000/day`               | Rate limiting for anonymous (unauthenticated) users.          |
| `API_THROTTLE_USER`       | `10000/day`              | Rate limiting for authenticated users.                        |

### LDAP Authentication

Enabling LDAP authentication is optional and disabled by default.
To enable LDAP, set the `AUTH_LDAP_SERVER_URI` value to the desired LDAP endpoint.

Application user fields can be mapped to LDAP attributes by specifying the `AUTH_LDAP_ATTR_MAP` setting.
The following example maps the `first_name` and `last_name` fields used by Keystone to the LDAP attributes `givenName` and `sn`:

```bash
AUTH_LDAP_ATTR_MAP="first_name=givenName,last_name=sn"
```

See the `apps.users.models.User` class for a full list of available Keystone fields.

| Setting Name              | Default Value            | Description                                                   |
|---------------------------|--------------------------|---------------------------------------------------------------|
| `AUTH_LDAP_SERVER_URI`    |                          | The URI of the LDAP server.                                   |
| `AUTH_LDAP_START_TLS`     | `True`                   | Whether to use TLS when connecting to the LDAP server.        |
| `AUTH_LDAP_BIND_DN`       |                          | Optionally bind LDAP queries to the given DN.                 |
| `AUTH_LDAP_BIND_PASSWORD` |                          | The password to use when binding to the LDAP server.          |
| `AUTH_LDAP_USER_SEARCH`   | `(uid=%(user)s)`         | The search query for finding a user in the LDAP server.       |
| `AUTH_LDAP_REQUIRE_CERT`  | `False`                  | Whether to require certificate verification.                  |
| `AUTH_LDAP_ATTR_MAP`      |                          | A mapping of user fields to LDAP attribute names.             |

### Database Connection

Official support is included for both SQLite and PostgreSQL database backends.
However, SQLite is intended for development and demonstrative use-cases only.
The PostgreSQL backend should always be used in production settings.

| Setting Name              | Default Value            | Description                                                   |
|---------------------------|--------------------------|---------------------------------------------------------------|
| `DB_POSTGRES_ENABLE`      | `False`                  | Use PostgreSQL instead of the default Sqlite driver.          |
| `DB_NAME`                 | `keystone`               | The name of the application database.                         |
| `DB_USER`                 |                          | Username for database authentication (PostgreSQL only).       |
| `DB_PASSWORD`             |                          | Password for database authentication (PostgreSQL only).       |
| `DB_HOST`                 | `localhost`              | Database host address (PostgreSQL only).                      |
| `DB_PORT`                 | `5432`                   | Database host port (PostgreSQL only).                         |

### Redis Connection

Redis settings define the network location and connection information for the Redis backend.
Enabling password authentication is suggested when deploying Redis in a production environment.

| Setting Name              | Default Value            | Description                                                   |
|---------------------------|--------------------------|---------------------------------------------------------------|
| `REDIS_HOST`              | `127.0.0.1`              | URL for the Redis message cache.                              |
| `REDIS_PORT`              | `6379`                   | Port number for the Redis message cache.                      |
| `REDIS_DB`                | `0`                      | The Redis database number to use.                             |
| `REDIS_PASSWORD`          |                          | Optionally connect using the given password.                  |

### Developer Settings

The following settings are intended exclusively for use in development.
The `DEBUG` option is inherently insecure and should **never** be enabled in production settings.

| Setting Name              | Default Value            | Description                                                   |
|---------------------------|--------------------------|---------------------------------------------------------------|
| `DEBUG`                   | `False`                  | Enable or disable debug mode.                                 |

## Developer Notes

The following section details useful information for application contributors.

### Debug Mode

Running the application in debug mode enables/disables various features to aid in the development process.
In addition to enabling the standard debugging behavior provided by Django:

- A `/docs` page is enabled with full API documentation for the parent application
- Tracebacks are provided in the browser when an exception occurs (a Django standard)

### Admin Utilities

The `keystone-api` utility includes a series of admin utilities.
These utilities are useful for automating various development tasks.
A brief summary is provided below.
Use the `keystone-api <command> --help` option for specific usage information.

| Command                   | Description                                                                              |
|---------------------------|------------------------------------------------------------------------------------------|
| `clean`                   | Clean up files generated when launching a new application instance.                      |
| `quickstart`              | A helper utility for quickly migrating/deploying an application instance.                |

### Tests and System Checks

Application tests are run using the `test` command:

```bash
keystone-api test
```

Specific subsets of tests are run by specifying an app label.
For example, tests for the `users` application are executed as:

```bash
keystone-api test apps.users
```

The default django system checks can also be executed as standard:

```bash
keystone-api check                   # Check for system configuration errors
keystone-api makemigrations --check  # Check for missing database migrations
keystone-api health_check            # Check the status of running backend services
```

### API Schema Generation

Use the `spectacular` command to dynamically generate an OpenAPI schema:

```bash
keystone-api spectacular >> api.yml
```
