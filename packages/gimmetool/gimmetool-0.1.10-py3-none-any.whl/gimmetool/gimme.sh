function gimme {
  if ! command -v gimmetool &> /dev/null
  then
    return
  fi

  arg=$1
  case $arg in
    ("")
      gimmetool -h
      ;;
    (-h | --help | -v | --version | config | list | ls | l | updates | update | pull | changes | repo | init)
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
