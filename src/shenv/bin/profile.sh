# shellcheck shell=sh disable=SC3040,SC3054,SC2296,SC2034,SC3028,SC2046,SC2139

#
# System and users profile for bash, busybox, dash, ksh, sh and zsh (/etc/profile and /etc/zprofile).
#
# https://www.gnu.org/software/bash/manual/html_node/Bash-POSIX-Mode.html
# https://www.gnu.org/software/bash/manual/html_node/The-Shopt-Builtin.html
# https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html
# https://man7.org/linux/man-pages/man1/sh.1p.html
# https://man7.org/linux/man-pages/man1/dash.1.html
# https://linux.die.net/man/1/ksh
# https://www.mkssoftware.com/docs/man1/sh.1.asp
# https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18
# https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_06_02
# BASH:
# /bin/bash or bash does not look at $ENV
# /bin/sh uses $ENV
# sudo su (with SHELL /bin/sh) uses $ENV
# Ideally .bashrc, although if I log in and no vars depending on the user...

unset BASH_ENV
export ENV="${RC?Must be set with RC repository path or sourced by /etc/profile or /etc/zprofile}/profile"

# <html><h2>RC Path</h2>
# <p><strong><code>$RC</code></strong> RC Repository (Development or Installed) Physical Path.</p>
# </html>
export RC

. shell.sh
. profile.sh
. rc.sh

export BASH_ENV="${ENV}"
