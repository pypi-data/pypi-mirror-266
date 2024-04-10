import shutil
from os import path

script = """
#!/usr/bin/env bash
function gimme_func {
  arg=$1
  case $arg in
    ("")
      gimmetool -h
      ;;
    (-h | config | list | ls | l | updates | update | pull | changes | repo)
      gimmetool "$@"
      ;;

    (*)
      p="$(gimmetool repo "$@")"
      if [ -z "$p" ]
      then
        echo "Could not find repository \"$arg\""
      else
        if [ "${p:0:1}" = "/" ];
        then
          cd "${p}" || return
        else
          echo "Could not find repository \"$arg\""
        fi
      fi

      unset p
    ;;
  esac

  unset arg
}

gimme_func "$@"
"""

def main():
    install_path = shutil.which('gimmetool')
    # while path.islink(install_path):
    #     install_path = os.readlink(install_path)

    install_dir = path.dirname(install_path)
    print(install_dir)
    with open('gimme', 'w') as gimme:
        gimme.write(script)

