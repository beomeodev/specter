# Universal Dev Container Template

## Overview
A portable Docker-based development environment with:
- Python 3.12 + common dev tools
- AI agent CLIs (Claude Code, Codex)
- Auto-sync workflow with Git
- CI/CD pipeline (GitHub Actions)
- Cross-platform support (Windows WSL2, macOS, Linux)

---

## Initial Setup (One-time per machine)

### 1. Prerequisites
```bash
# Required
- Docker Desktop (with WSL2 on Windows)
- Git
- Make (usually pre-installed on Linux/macOS)

# Optional
- GitHub CLI (gh) for PR management
```

### 2. Project Manager Setup
```bash
# Run setup script once to enable 'pm' command
cd /path/to/project
bash setup-pm.sh
source ~/.zshrc  # or source ~/.bashrc

# Test
pm sab cc  # Works from any directory!
```

**What `pm` does:**
- `pm sab cc` = Start project + Claude Code (from anywhere)
- `pm sab cx` = Start project + Codex
- `pm sab cr` = Resume last Codex session

### 3. Agent CLI Login (Optional)
```bash
# For Codex (if using)
pipx install @openai/codex
codex login

# Claude Code uses API key from .env
```

---

## Daily Workflow

### Start Working
```bash
# From ANY directory
pm sab cc  # or pm sab cx

# What happens:
# 1. Auto-commit local changes
# 2. Push to remote
# 3. Pull latest from remote
# 4. Start container (rebuild if needed)
# 5. Launch Claude Code
```

### Finish Working
```bash
# Inside project directory
make finish

# What happens:
# 1. Run CI checks (lint, type, test)
# 2. Commit changes
# 3. Push to remote
```

---

## Commands Reference

### Project Launcher (from anywhere)
```bash
pm sab cc    # Start with Claude Code
pm sab cx    # Start with Codex
pm sab cr    # Resume Codex session
```

### Container Management
```bash
make start        # Start or resume container without rebuild
make stop         # Stop container
make down         # Remove container completely
make rebuild      # Force rebuild (no cache)
make sh           # Shell into container
```

### Development
```bash
make test         # Run tests
make fmt          # Format code (black, isort)
make lint         # Lint code (ruff, flake8)
make precommit    # Run pre-commit hooks
```

### CI/CD
```bash
make ci           # Run all CI checks
make finish       # CI + commit + push (recommended)
```

### Agent CLIs (inside container)
```bash
make cc           # Claude Code
make cx           # Codex
make cr           # Codex resume
```

### Optional Services
```bash
make dbup         # Start Postgres
make cacheup      # Start Redis
make nbup         # Start Jupyter Lab
```

---

## New Project Setup

### 1. Copy Template Files
```
docker-compose.yml
Dockerfile
Makefile
.github/workflows/ci.yml
setup-pm.sh
DOCKER_README.md (this file)
```

### 2. Customize Makefile
```makefile
# Line 101-103: Change project shortcode (3 letters)
.PHONY: abc  # Change from 'sab' to your code
abc:
	@$(MAKE) -s sync repo=git@github.com:user/repo.git

# Line 117-124: Update shorthand commands
abccc:  # Change from 'sabcc'
	@$(MAKE) -s go proj=abc agent=cc
```

### 3. Create Symbolic Link (optional)
```bash
cd /mnt/d/underway_project
ln -s your-long-project-name abc
```

### 4. Done!
```bash
pm abc cc  # Start working!
```

---

## Rebuild Triggers

**Container rebuilds when:**
- You run `make up` or `make rebuild` explicitly
- `Dockerfile` changed (detected by Docker)
- `requirements.txt` changed (detected by Docker)
- `docker-compose.yml` changed

**Container does NOT rebuild when:**
- You use `make start` or `pm <ticker> cc/cx/cr/gm`
- Already running (for speed)
- Use `make down && make up` to force rebuild

---

## GitHub Actions CI

**Auto-runs on:**
- Push to any branch
- Pull request to main/master

**What it checks:**
- Lint (black, isort, ruff)
- Type (mypy)
- Tests (pytest with coverage)

**Same checks as `make ci` locally!**

---

## Troubleshooting

### `pm: command not found`
```bash
# Re-run setup
bash setup-pm.sh
source ~/.zshrc
```

### Container won't rebuild
```bash
make stop
make rebuild  # Force rebuild with no cache
```

If you want to discard the container entirely:
```bash
make down
```

### Git conflicts
```bash
# Resolve manually, then:
git add .
git rebase --continue
```

### Port conflicts
```bash
# Check docker-compose.yml and change ports
# Or stop conflicting services
```

---

## Architecture

### Directory Structure
```
/workspace/${PROJECT_NAME}/     # Auto-detected from directory name
├── src/                        # Your code
├── tests/                      # Tests
├── .github/workflows/ci.yml    # CI pipeline
├── docker-compose.yml          # Container config
├── Dockerfile                  # Image definition
├── Makefile                    # Commands
├── requirements.txt            # Python deps
├── requirements-dev.txt        # Dev deps
└── setup-pm.sh                 # Setup script
```

### Container Features
- Non-root user (dev)
- Volume mount for live code updates
- Shared `~/.codex` for token persistence
- Pre-installed: git, openssh-client, Node.js, uv, pipx
- Python dev tools: black, isort, ruff, mypy, pytest

---

## Tips

1. **Use `pm` from anywhere** - No need to cd to project
2. **Use `make finish`** - Ensures CI passes before push
3. **Keep containers running** - Faster subsequent `pm` calls
4. **One PC at a time** - Workflow optimized for single-user
5. **Symbolic links** - Shorter project names for `pm` command

---

## Support

For issues or questions:
- Check [GitHub Issues](https://github.com/your-org/template/issues)
- Review [Makefile](Makefile) for all available commands
- Check [.github/workflows/ci.yml](.github/workflows/ci.yml) for CI config
