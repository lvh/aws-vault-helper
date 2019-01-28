# The goal is to create an interactive subshell with a modified interactive prompt. This is tricky!
# You can't just set $PS1 unless you also disable rcfiles; they can set $PS1 too.
# So, a few options:
# - reduced shell with no rcfiles and other fancy features
# - shell cooperates by setting some ${WELL_KNOWN_FLAG} in its own $PS1
# - $PROMPT_COMMAND hacks that modify PS1 and then unset $PROMPT_COMMAND (same problem as setting $PS1 but less common)

import sys
import os
import subprocess


if len(sys.argv) != 2:
    print("pass aws-vault profile as an argument")
    sys.exit(1)
else:
    vaultenv = sys.argv[1]


sh = os.getenv("SHELL")
for shtype in ["bash", "zsh", "sh"]:
    if sh.endswith(shtype):
        break

for path in os.environ["PATH"].split(os.pathsep):
    fullpath = os.path.join(path, "aws-vault")
    if os.access(fullpath, os.X_OK):
        awsvault = fullpath
        break
else:
    raise RuntimeError("couldn't find aws-vault in PATH")

if sys.platform.startswith("linux"):
    awsvaultflags = ["--backend=secret-service"]
else:
    awsvaultflags = []

awsvaultcmd = [awsvault] + awsvaultflags + ["exec", vaultenv, "--", "env", "-0"]
envlines = subprocess.check_output(awsvaultcmd)
env = {}
for l in envlines.split(b"\x00"):
    if not l:
        break
    k, v = l.split(b"=", maxsplit=1)
    env[k] = v

ESC = '\033[{0}m'
esc = ESC.format

OFF, BOLD, UNDERSCORE, BLINK = 0, 1, 4, 5
BLACK, BLACKBG = 30, 40
RED, REDBG = 31, 41
GREEN, GREENBG = 32, 42
YELLOW, YELLOWBG = 33, 43
BLUE, BLUEBG = 34, 44
MAGENTA, MAGENTABG = 35, 45
CYAN, CYANBG = 36, 46
WHITE, WHITEBG = 37, 47


newps1 = "{loud}<aws-vault env {env}>{quiet} {ps1}".format(
    loud=esc(MAGENTABG) + esc(BLACK),
    quiet=esc(OFF),
    env=vaultenv,
    ps1=env.get("PS1", "$")
)
args = ()
if shtype == "bash":
    env["PROMPT_COMMAND"] = 'PS1="{newps1}";unset PROMPT_COMMAND' .format(newps1=newps1)
elif shtype == "zsh":
    pass
os.execve(sh, args, env)
