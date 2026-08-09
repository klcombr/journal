# Examples

Real usage patterns for `journal`. Copy, paste, adapt.

## 1. Minimal daily habit

```bash
# ~/.zshrc
alias j="journal add"
alias streak="journal count --days"

# usage
j "reviewed the daily notes"
streak
```

## 2. Point it at a different folder

```bash
export JOURNAL_FILE="$HOME/Documents/notes/journal.md"
journal add "first entry in Documents"
```

## 3. Read the last week programmatically

```python
import subprocess

out = subprocess.check_output(["journal", "list", "-n", "50"], text=True)
for line in out.splitlines():
    print(line)
```

## 4. Stats in a cron email (just an idea)

```bash
# crontab
0 18 * * * echo "$(journal count --days) days logged" | mail -s "journal" you@example.com
```
