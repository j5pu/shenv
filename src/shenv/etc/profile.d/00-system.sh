# shellcheck shell=sh
# shellcheck disable=SC2034

[ ! "${DIST_ID-}" ] || return 0

# '1' if 'DIST_ID' is 'alpine' and not: nix or busybox
#
export ALPINE

# '1' if 'DIST_ID' is 'alpine'
#
export ALPINE_LIKE

# '1' if 'DIST_ID' is 'arch' for archlinux
#
export ARCH

# Bash Deprecation
#
export BASH_SILENCE_DEPRECATION_WARNING

# '1' if not '/etc/os-release' and not '/sbin'.
#
export BUSYBOX

# '1' if 'DIST_ID' is 'centos'.
#
export CENTOS

# Command Line Tools Usr Directory (xcode-select -p).
#
export CLT

# '1' if running in docker container.
#
export CONTAINER

# '1' if 'DIST_ID' is 'debian'.
#
export DEBIAN

# 'noninteractive' if 'IS_CONTAINER' and 'DEBIAN_LIKE' are set.
    #
export DEBIAN_FRONTEND

# '1' if 'DIST_ID_LIKE is 'debian'.
#
export DEBIAN_LIKE

# <html><h2>Distribution Codename</h2>
# <p><strong><code>$DIST_CODENAME</code></strong> (always exported).</p>
# <ul>
# <li><code>Catalina</code></li>
# <li><code>Big Sur</code></li>
# <li><code>kali-rolling</code></li>
# <li><code>focal</code></li>
# <li><code>etc.</code></li>
# </ul>
# </html>
export DIST_CODENAME

# <html><h2>Distribution ID</h2>
# <p><strong><code>$DIST_ID</code></strong> (always exported).</p>
# <ul>
# <li><code>alpine</code></li>
# <li><code>centos</code></li>
# <li><code>debian</code></li>
# <li><code>kali</code></li>
# <li><code>macOS</code></li>
# <li><code>ubuntu</code></li>
# </ul>
# </html>
export DIST_ID

# <alpine|debian|rhel fedora>.
#
export DIST_ID_LIKE

# '1' if 'DIST_ID' is unknown.
#
export DIST_UNKNOWN

# <html><h2>Distribution Version</h2>
# <p><strong><code>$DIST_ID</code></strong> (always exported).</p>
# <ul>
# <li><code>macOS</code>: 10.15.1, 10.16 ...</li>
# <li><code>kali</code>: 2021.2, ...</li>
# <li><code>ubuntu</code> 20.04, ...</li>
# </ul>
# </html>
export DIST_VERSION

# '1' if 'DIST_ID' is 'fedora'.
#
export FEDORA

# '1' if 'DIST_ID' is 'fedora' or 'fedora' in 'DIST_ID_LIKE'.
#
export FEDORA_LIKE

# GIT System Config
#
export GIT_CONFIG_SYSTEM

# GIT Init Template Directory
#
export GIT_TEMPLATE_DIR

# https://github.com/Homebrew/homebrew-command-not-found
#
export HB_CNF_HANDLER

# Cask Versions (similar to opt)
#
export HOMEBREW_CASK

# Version of formula, $HOMEBREW_PREFIX/opt is a symlink to $HOMEBREW_CELLAR (brew shellenv).
#
export HOMEBREW_CELLAR

# HOMEBREW_COMPLETIONS_D
#
export HOMEBREW_COMPLETIONS_D

# Homebrew etc
#
export HOMEBREW_ETC

# Homebrew unlinked Kegs (in $HOMEBREW_OPT) to add to PATH
#
export HOMEBREW_KEGS

# Homebrew ./lib
#
export HOMEBREW_LIB

# Symlink for the latest version of formula to $HOMEBREW_CELLAR.
#
export HOMEBREW_OPT

# Homebrew prefix (brew shellenv)
#
export HOMEBREW_PREFIX

# Profile compat dir (profile.d), under etc.
#
export HOMEBREW_PROFILE_D

# Repository and Library with homebrew gems and Taps (brew shellenv).
#
export HOMEBREW_REPOSITORY

# Taps path under '$HOMEBREW_REPOSITORY/Library'.
#
export HOMEBREW_TAPS

# <html><h2>First part of hostname</h2>
# <p><strong><code>$HOST</code></strong> (always exported).</p>
# <ul>
# <li><code>foo.com</code>: foo</li>
# <li><code>example.foo.com</code>: example</li>
# </ul>
# </html>
export HOST

# Symbol and 'HOST' if 'CONTAINER' or 'SSH'.
#
export HOST_PROMPT

# '1' if 'DIST_ID' is 'kali'.
#
export KALI

# <html><h2>Is MACOS?</h2>
# <p><strong><code>$MACOS</code></strong> (always exported).</p>
# <p><strong><code>Boolean</code></strong></p>
# <ul>
# <li><code>1</code>: $UNAME is darwin</li>
# <li><code>0</code>: $UNAME is linux</li>
# </ul>
# </html>
export MACOS

# '1' if 'DIST_ID' is 'alpine' and '/etc/nix'.
#
export NIXOS

# <html><h2>Default Package Manager</h2>
# <p><strong><code>$PM</code></strong> (always exported).</p>
# <ul>
# <li><code>apk</code></li>
# <li><code>apt</code></li>
# <li><code>brew</code></li>
# <li><code>nix</code></li>
# <li><code>yum</code></li>
# </ul>
# </html>
export PM

# <html><h2>Default Package Manager Command with Install Options</h2>
# <p><strong><code>$PM_INSTALL</code></strong> (always exported).</p>
# <p><strong><code>Quiet and no cache (for containers)</code></strong>.</p>
# <ul>
# <li><code>apk</code></li>
# <li><code>apt</code></li>
# <li><code>brew</code></li>
# <li><code>nix</code></li>
# <li><code>yum</code></li>
# </ul>
# </html>
export PM_INSTALL

# <html><h2>Default Package Manager Command with Upgrade and Cleanup</h2>
# <p><strong><code>$PM_UPGRADE</code></strong> (always exported).</p>
# <p><strong><code>Quiet and no cache (for containers)</code></strong>.</p>
# <ul>
# <li><code>apk</code></li>
# <li><code>apt</code></li>
# <li><code>brew</code></li>
# <li><code>nix</code></li>
# <li><code>yum</code></li>
# </ul>
# </html>
export PM_UPGRADE

# Python Interactive Startup File
#
PYTHONSTARTUP="$(command -v pythonstartup || true)"; export PYTHONSTARTUP

# '1' if 'DIST_ID' is 'rhel'.
#
export RHEL

# '1' if 'DIST_ID' is 'rhel' or 'rhel' in 'DIST_ID_LIKE'.
#
export RHEL_LIKE

# SHARE_COMPLETIONS_D contains the default /usr/share completions compat dir for Linux
#
export SHARE_COMPLETIONS_D

# '1' if 'SSH_CLIENT' or 'SSH_TTY' or 'SSH_CONNECTION'.
#
export SSH

# Path with sudo command
# https://linuxhandbook.com/run-alias-as-sudo/
#
export SUDOC='/usr/bin/sudo'

# '1' if 'DIST_ID' is 'ubuntu'.
#
export UBUNTU

# <html><h2>Operating System Name</h2>
# <p><strong><code>$UNAME</code></strong> (always exported).</p>
# <ul>
# <li><code>Darwin</code></li>
# <li><code>Linux</code></li>
# </ul>
# </html>
export UNAME

# <html><h2>Have an VGA card</h2>
# <p><strong><code>$VGA</code></strong> '1' if has an VGA card.</p>
# </html>
export VGA

#######################################
# distribution ID
#######################################
dist_id() {
  case "${DIST_ID}" in
    alpine)
      # TODO: check if nix is really alpine !!!
      ALPINE_LIKE=1; DIST_ID_LIKE="${DIST_ID}"
      if [ -r '/etc/nix' ]; then NIXOS=1; PM='nix-env'; else ALPINE=1; PM='apk'; fi
      ;;
    arch) ARCH=1; PM='pacman' ;;
    centos) CENTOS=1; PM='yum' ;;
    debian) DEBIAN=1; DEBIAN_LIKE=1; DIST_ID_LIKE="${DIST_ID}" ;;
    fedora) FEDORA=1; FEDORA_LIKE=1; PM='dnf' ;;
    kali) KALI=1 ;;
    rhel) RHEL=1; RHEL_LIKE=1; PM='yum' ;;
    ubuntu) UBUNTU=1 ;;
    *) DIST_UNKNOWN=1 ;;
  esac
}

#######################################
# distribution ID like
#######################################
dist_id_like() {
  case "${DIST_ID_LIKE}" in
    debian) DEBIAN_LIKE=1; PM='apt' ;;
    *fedora*) FEDORA_LIKE=1;;
    *rhel*) RHEL_LIKE=1 ;;
  esac
}

#######################################
# sets git config variables
# Examples:
#   git ls-remote --get-url
#   git config credential.credentialStore
#   git config credential.helper
#   git config credential."https://dev.azure.com".useHttpPath
#######################################
git_config() {
  set -a
  GIT_CONFIG_SYSTEM="$(command -v .gitconfig)"
  GIT_TEMPLATE_DIR="${GIT_CONFIG_SYSTEM:+$(command dirname "${GIT_CONFIG_SYSTEM}")/template}"

  [ ! "${GITHUB_ACTION-}" ] || { set +a; return; }

  GIT_CONFIG_COUNT=4
  GIT_CONFIG_KEY_0='url.ssh://git@github.com/.insteadOf';
  GIT_CONFIG_VALUE_0="$(! command ssh -T git@github.com 2>&1 \
  | command grep -q "successfully authenticated" || echo https://github.com/ )"
  GIT_CONFIG_KEY_1="credential.credentialStore"
  GIT_CONFIG_VALUE_1="$(if [ "$(command uname -s)" = 'Darwin' ];
  then echo keychain; elif command -v secret-tool >/dev/null; then echo secretservice; else echo plaintext; fi)"
  GIT_CONFIG_KEY_2="credential.helper"
  GIT_CONFIG_VALUE_2="$(command -v git-credential-manager-core)"
  GIT_CONFIG_KEY_3='credential."https://dev.azure.com".useHttpPath'
  GIT_CONFIG_VALUE_3="${GIT_CONFIG_VALUE_2:+true}"
  set +a
}

#######################################
# homebrew variables
#######################################
homebrew() {
  HOMEBREW_CASK="${HOMEBREW_PREFIX}/Caskroom"
  HOMEBREW_CELLAR="${HOMEBREW_PREFIX}/Cellar"
  HOMEBREW_ETC="${HOMEBREW_PREFIX}/etc"
  HOMEBREW_COMPLETIONS_D="${HOMEBREW_ETC}/bash_completion.d"
  HOMEBREW_LIB="${HOMEBREW_PREFIX}/lib"
  HOMEBREW_OPT="${HOMEBREW_PREFIX}/opt"
  HOMEBREW_PROFILE_D="${HOMEBREW_ETC}/profile.d"
  HOMEBREW_REPOSITORY="${HOMEBREW_PREFIX}/Homebrew"
  HOMEBREW_TAPS="${HOMEBREW_REPOSITORY}/Library/Taps"
  HB_CNF_HANDLER="${HOMEBREW_TAPS}/homebrew/homebrew-command-not-found/handler.sh"
}

#######################################
# package manager install
#######################################
pm_install() {
  if [ "${PM-}" ]; then
    case "${PM}" in
      # pacman -Sy (like apt update)
      apk) PM_INSTALL="sudo ${PM} ${PM} add -q --no-progress"; NO_CACHE='--no-cache' ;;
      apt)
        PM_INSTALL="sudo ${PM} -qq update -y && ${PM} -qq install -y"
        PM_UPGRADE="${PM} -qq full-upgrade -y && ${PM} -qq auto-remove -y && ${PM} -qq clean"
        ;;
      brew) PM_INSTALL="${PM} install --quiet" ;;
      dnf) PM_INSTALL="sudo ${PM} install -y -q" ;;
      nix) PM_INSTALL="sudo ${PM} --install -A" ;; # nixos -> nixos.curl, no nixos --> nixpkgs.curl
      pacman) PM_INSTALL="sudo ${PM} -Sy && ${PM} -S --noconfirm" ;;
      yum) PM_INSTALL="sudo ${PM} install -y -q" ;;
      *) PM_INSTALL=''
    esac
  fi
}

#######################################
# system main
#######################################
system() {
  _strip() { echo "${value}" | sed 's/^"//;s/"$//'; }
  HOST="$(command -p hostname -s 2>/dev/null || command cut -d '.' -f 1 /etc/hostname)"
  UNAME="$(command uname)"
  if [ "${UNAME}" = 'Darwin' ]; then
    BASH_SILENCE_DEPRECATION_WARNING=1
    CLT='/Library/Developer/CommandLineTools'
    DIST_ID="$(command -p sw_vers -ProductName)"
    DIST_VERSION="$(command -p sw_vers -ProductVersion)"
      # shellcheck disable=SC2016
      case "$(echo "${DIST_VERSION}" | command awk -F. '{ print $1 $2 }')" in
      1013) DIST_CODENAME='High Sierra' ;;
      1014) DIST_CODENAME='Mojave' ;;
      1015) DIST_CODENAME='Catalina' ;;
      11*) DIST_CODENAME='Big Sur' ;;
      12*) DIST_CODENAME='Monterey' ;;
      *) DIST_CODENAME='Other' ;;
    esac
    HOMEBREW_KEGS='ruby'
    HOMEBREW_PREFIX='/usr/local'
    MACOS=1
    PM='brew'
    PM_INSTALL="${PM} install"
    [ "${GITHUB_RUN_ID-}" ] || VGA=1
  else
    if [ -f '/etc/os-release' ]; then
      while IFS='=' read -r name value; do
        case "${name}" in
          ID) DIST_ID="$(_strip)"; dist_id; unset -f dist_id ;;
          ID_LIKE) DIST_ID_LIKE="$(_strip)"; dist_id_like; unset -f dist_id_like ;;
          VERSION_ID) DIST_VERSION="$(_strip)" ;;
          VERSION_CODENAME) DIST_CODENAME="$(_strip)" ;;
        esac
      done < '/etc/os-release'
    else
      BUSYBOX=1; PM=''
      DIST_ID='busybox'
    fi
    unset _strip name value
    SHARE_COMPLETIONS_D='/usr/share/bash-completion/completions'
    LINUXBREW='/home/linuxbrew/.linuxbrew'
    HOMEBREW_PREFIX="${LINUXBREW}"
    MACOS=0
    [ -x /usr/bin/sudo ] || export SUDOC=
    VGA="$(command lspci 2>/dev/null | command awk '/VGA/ { print 1 }')"
  fi

  homebrew; unset -f homebrew
  pm_install; unset -f pm_install

  if [ "${SSH_CLIENT-}" ] || [ "${SSH_CONNECTION-}" ] || [ "${SSH_TTY-}" ]; then
    SSH=1
  elif [ -f '/.dockerenv' ]; then
    CONTAINER=1
    [ ! "${DEBIAN_LIKE-}" ] || DEBIAN_FRONTEND='noninteractive'
    if [ "${NO_CACHE-}" ]; then
      PM_INSTALL="${PM_INSTALL} ${NO_CACHE}"
    fi
  fi
  git_config; unset -f git_config
}

system; unset -f system
