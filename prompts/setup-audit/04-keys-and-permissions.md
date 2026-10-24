# 04 · Keys and permissions (in the session)

**What it's for:** finding keys in the wrong place and permissions that are too wide open.
**Who runs it:** the client. Read-only.

Copy from the line below to the end.

---

Check my keys and permissions. Only read. Don't change anything. Never show a key, token or password: write HIDDEN instead.

1. Search the instruction files, skills, commands and scripts in this folder and in ~/.claude for anything that looks like a pasted API key, token or password. Say which file and line, never the value.
2. List every .env file (variable names only). Is each one in .gitignore? Is there a Read deny rule for .env in my settings?
3. If this folder is a git repo with a remote: has a .env file, or any file holding a key, ever been committed? Check the git history for those file names only. Say yes or no and which file. Don't print what's in them.
4. List my permission rules (allow, ask, deny) and any defaultMode from each settings file. Flag broad ones like Bash(*), and any use of bypassPermissions or --dangerously-skip-permissions in settings or scripts.
5. For each routine that touches client data, email, payments or anything public: does a person check the result before it goes out?

Give me a short list: what's fine, what to fix first, what to tidy up.
