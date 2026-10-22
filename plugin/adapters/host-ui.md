# control-ui server writes and login

- Before any action that may write to the server (save, submit, delete, approve, or typing into an existing record), stop and get a yes from the user, or from the coordinator if you are a worker.
- To log in, read credentials from the project's secret file (for example `.env`) without asking. Fill the form with code that never prints, returns or logs them, and never put them in tool arguments. If no secret file exists, ask the user to log in in the browser, then continue.
