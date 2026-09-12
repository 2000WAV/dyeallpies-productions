#!/usr/bin/env bash
# Make `import studio` work inside a venv without a build step: a .pth file pointing at tools/.
#   bash tools/install_studio.sh .venv-hand      (repeat for every venv that runs a format's scripts)
set -euo pipefail
venv=${1:?usage: install_studio.sh <venv dir>}
tools=$(cd "$(dirname "$0")" && pwd -W 2>/dev/null || cd "$(dirname "$0")" && pwd)
site=$(ls -d "$venv"/Lib/site-packages 2>/dev/null || ls -d "$venv"/lib/python*/site-packages)
printf '%s\n' "$tools" > "$site/studio.pth"
"$venv"/Scripts/python.exe -c "import studio, sys; print('studio', studio.__version__, 'from', studio.__file__)" 2>/dev/null \
  || "$venv"/bin/python -c "import studio; print('studio', studio.__version__, 'from', studio.__file__)"
