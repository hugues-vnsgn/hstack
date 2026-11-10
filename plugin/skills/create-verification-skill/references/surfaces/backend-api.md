# Backend API surface

Authored guidance, not an observed run. This page says what each section of the generated skill pins for a service a client reaches over HTTP. The .NET lines are an example; use the repository's own commands.

- **Launch:** the repository's run command with an explicit port and environment. For ASP.NET Core that is `dotnet run --project <path> --urls http://127.0.0.1:<port>` with `ASPNETCORE_ENVIRONMENT` set. Start the database and queues from the repository's own compose file or scripts, then apply migrations and seed data. Ready means a real route returns the expected body. A listening port or a health check can pass before migrations finish.
- **Doctor:** the port belongs to the process this run started, the build that answers is the one under test, the connection string names the verification database, and the test user's credential is valid.
- **Drive:** the repository's own API path first: its integration test project, its `.http` files or its request collection. Otherwise plain HTTP against the routes a client calls, through the real sign-in flow. Internal and test-only endpoints are not the user path.
- **Evidence:** for each call the method, path, request body, status and response body, with secrets redacted. Then read the side effect back yourself: the row, the queued message, the written file or the mail in the local catcher. Keep the service log for the run.
- **Cleanup:** stop the processes and containers this run started, by PID or container ID, and drop the verification database or schema.
- **Isolate:** each instance takes its own port, database name and data directory from the environment. If the service cannot take one of them that way, say so in the generated skill.
