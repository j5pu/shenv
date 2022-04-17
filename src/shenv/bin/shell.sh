#!/bin/sh
# shellcheck disable=SC3054,SC3028,SC3040

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

[ "${__SHELL_SH_SOURCED-0}" -eq 0 ] || return 0
__SHELL_SH_SOURCED=1

# <html><h2>Running Shell</h2>
# <p><strong><code>$SH</code></strong> posix-<ash|busybox|dash|ksh|sh>, zsh, sh for bash sh, bash or bash4.</p>
# </html>
SH="${ZSH_ARGZERO:-${0##*/}}"

__bash () {
  SH="${BASH##*/}"
  [ "${BASH_VERSINFO[0]}" -lt 4 ] || { SH="bash-4"; shopt -s inherit_errexit; }
  set -o errtrace
}

__real () {
  SH="$("$(command -v realpath || command -v readlink)" "$(command -v "$1")")"
  [ "${SH-}" ] || SH="$1"
  SH="posix-${SH##*/}"
}

case "${SH}" in
  ash|bash|busybox|dash|ksh|sh)
    if [ "${BASH_SOURCE-}" ]; then
      __bash
    else
      __real "${ZSH_ARGZERO:-$0}"
    fi
    ;;
  -zsh|zsh) SH="zsh" ;;
  *)
    if [ "${BASH-}" ]; then
      __bash
    elif [ "${ZSH_EVAL_CONTEXT-}" ]; then
      SH="zsh"
    elif [ "${KSH_VERSION-}" ]; then
      SH="posix-ksh"
    else
      if test -f /proc/$$/comm; then
        SH="$(cat /proc/$$/comm)"
        __exe="$(command awk -F '[()]' '{ print $2 }' /proc/$$/stat)"
        __cmd="$(tr "\000" "\n" < /proc/$$/cmdline | head -1)"
        [ "${__exe##*/}" = "${__cmd##*/}" ] || SH="${__cmd}"
      elif __ps="$(command -v ps)"; then
        SH="$("${__ps}" -o pid= -o comm= | command sed -n "s/^ \{0,\}$$ //p")"
      fi
      case "${SH##*/}" in
        ash|busybox|dash|sh) __real "${SH}" ;;
      esac
    fi
    ;;
esac

unset -f __bash __real
unset __ps

