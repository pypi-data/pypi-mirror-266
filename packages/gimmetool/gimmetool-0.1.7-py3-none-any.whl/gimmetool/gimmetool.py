#!/usr/bin/env python3
import os
import stat
import io
import git
import argparse
import json
import sys
import shutil
from os import path
import stat
from termcolor import colored
import pkg_resources

def colored(*args):
    return args[0]

CONFIG_FILE_NAME = '.gimmeconfig.json'

gcmd = git.Git(path.expanduser("~/git/GitPython"))

SCRIPT = """
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
    (-h | --help | -v | --version | config | list | ls | l | updates | update | pull | changes | repo)
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
"""


def main():
    """main

    Main entrypoint.
    """

    parser = argparse.ArgumentParser(prog='gimme', description='Gimme: The multi-repo manager!')
    parser.add_argument('-v', '--version', action='store_true', help='display version number')

    subparsers = parser.add_subparsers(dest='command')
    add_init_parser(subparsers)
    add_list_parser(subparsers)
    add_updates_parser(subparsers)
    add_repo_switcher(subparsers)
    add_config_options(subparsers)
    parser.set_defaults(func=lambda _: parser.print_help())

    args = parser.parse_args()

    if not path.exists(path.join(Utils.get_install_dir(), 'gimmetool')) and args.command is None:
        print('gimme needs initialization:')
        print(colored('~$ sudo gimme init', 'yellow'))
        return

    if args.version:
        print(pkg_resources.get_distribution('my-package-name').version)
        return

    args.func(args)

def add_init_parser(subparsers: argparse._SubParsersAction):
    init_parser = subparsers.add_parser('init', help='Perform first time initialization')

    def init(_args):
        """Performs gimme one-time initialization.

        In order to make jumping from repo to repo possible, gimme needs to change directories from the main shell
        context. In order to do this, we generate a shell function which proxies the CLI.
        """
        if not os.environ.get("SUDO_UID") and os.geteuid() != 0:
            print('gimme init must be run with sudo.')
            return

        install_dir = Utils.get_install_dir()
        gimmetoolpath = path.join(install_dir, 'gimmetool')
        gimmepath = path.join(install_dir, 'gimme')

        try:
            repos_path = input('where do all of your repositories live [~/]?')
            if repos_path == '':
                repos_path = '~/'

            config = Config()
            config.add_group(path.expanduser(repos_path))

            config_path = input('shell config file [~/.zshrc]: ')
            if config_path == '':
                config_path = '~/.zshrc'

            if not path.exists(path.expanduser(config_path)):
                confirm_force = input(f'Could not find {config_path}. Proceed anyway? [n]: ')
                if confirm_force.lower() != 'y' or confirm_force.lower() != 'yes':
                    return

            if path.islink(gimmepath):
                # just generate symlinks instead of copying actual file contents over.
                actual_path = os.readlink(gimmepath)
                os.symlink(actual_path, gimmetoolpath)
                os.remove(gimmepath)
            else:
                os.rename(gimmepath, gimmetoolpath)

            gimmefuncpath = path.join(install_dir, 'gimme.sh')
            with open(gimmefuncpath, 'w') as gimme:
                gimme.write(SCRIPT)
                gimme.close()

            # mark as executable
            st = os.stat(gimmefuncpath)
            os.chmod(gimmefuncpath, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            expanded_config_path = path.expanduser(config_path)
            with open(expanded_config_path, 'r+') as config_file:
                source_line = f'. {gimmefuncpath}'
                if source_line not in config_file.read():
                    config_file.seek(0, io.SEEK_END);
                    config_file.write(f'\n. {gimmefuncpath}')
                    config_file.close()

            print('Initialization successful.')

        except PermissionError:
            print('gimme init must be run with sudo.')

    init_parser.set_defaults(func=init)


def add_config_options(subparsers: argparse._SubParsersAction):
    config_parser = subparsers.add_parser('config', help='Configure gimme behavior.')
    config_parser.set_defaults(func=lambda _: config_parser.print_help())
    config_subparsers = config_parser.add_subparsers()

    # -------------------------
    # ---------- Add ----------
    # -------------------------
    add_config_parser = config_subparsers.add_parser('add', help='add a new configuration')
    add_config_subparsers = add_config_parser.add_subparsers()

    # Group Add
    add_group_parser = add_config_subparsers.add_parser('group', help='Add a group of repositories')
    add_group_parser.add_argument('path', help='The path to the repo group. Should be a single folder')
    add_group_parser.set_defaults(func=lambda args: Config().add_group(args.path))

    # Favorite Add
    add_favorite_parser = add_config_subparsers.add_parser(
        'favorite',
        help='Add a favorite repository. Favorites are searched first.'
    )

    add_favorite_parser.add_argument('path', help='The path to the repo.')
    add_favorite_parser.set_defaults(func=lambda args: Config().add_favorite(args.path))

    # Alias Add
    add_alias_parser = add_config_subparsers.add_parser('alias', help='Add an alias for a specific search.')
    add_alias_parser.add_argument('alias', help='The alias.')
    add_alias_parser.add_argument('actual', help='What the alias substitutes.')
    add_alias_parser.set_defaults(func=lambda args: Config().add_alias(args.alias, args.actual))

    # ----------------------------
    # ---------- Remove ----------
    # ----------------------------
    remove_config_parser = config_subparsers.add_parser('remove', help='Remove a configuration')
    remove_config_subparsers = remove_config_parser.add_subparsers()

    # Remove Group
    remove_group_parser = remove_config_subparsers.add_parser('group', help='Remove a group of repositories')
    remove_group_parser.add_argument('path', help='the path to the repo group you\'d like to remove')
    remove_group_parser.set_defaults(func=lambda args: Config().remove_group(args.path))

    # Remove Favorite
    remove_favorite_parser = remove_config_subparsers.add_parser('favorite', help='Remove a favorite repositories')
    remove_favorite_parser.add_argument('path', help='the path to the repo group you\'d like to remove')
    remove_favorite_parser.set_defaults(func=lambda args: Config().remove_favorite(args.path))

    # Remove Alias
    remove_alias_parser = remove_config_subparsers.add_parser('alias', help='Add an alias for a specific search.')
    remove_alias_parser.add_argument('alias', help='The alias.')
    remove_alias_parser.set_defaults(func=lambda args: Config().remove_alias(args.alias))

    # --------------------------
    # ---------- List ----------
    # --------------------------
    list_config_parser = config_subparsers.add_parser('list', help='list settings for a configuration')
    list_config_subparsers = list_config_parser.add_subparsers()
    list_config_parser.set_defaults(func=lambda _: list_config_parser.print_help)

    # Group List
    list_groups_parser = list_config_subparsers.add_parser('groups', help='show repository groups')
    list_groups_parser.set_defaults(func=lambda _: Config().list_groups())

    # Favorites List
    list_favorites_parser = list_config_subparsers.add_parser('favorites', help='show favorited repositories')
    list_favorites_parser.set_defaults(func=lambda _: Config().list_favorites())

    # Aliases List
    list_alias_parser = list_config_subparsers.add_parser('aliases', help='show aliases')
    list_alias_parser.set_defaults(func=lambda _: Config().list_aliases())


def add_list_parser(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser(
        'list',
        aliases=['ls'],
        help='Lists all local repositories. The search is recursive under each configured directory.'
    )
    parser.add_argument('--dirs', '-d', nargs='*', default=[], help='Override directories.')

    def list_repos(_args):
        config = Config()
        lister = Lister()

        lister.list_repositories(config.groups)

    parser.set_defaults(func=list_repos)


def add_updates_parser(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser(
        'updates',
        aliases=['pull', 'changes'],
        help='Pulls updates from the main branch associated with each of your local repositories.'
    )
    parser.add_argument('--dirs', '-d', nargs='*', default=[], help='Override directories.')
    parser.add_argument(
        '--verbose', '-v',
        dest='verbosity',
        action='store_const',
        const=1,
        default=0,
        help='Show a more verbose output.'
    )
    parser.add_argument(
        '--clean', '-c',
        action='store_true',
        help='If updating repositories, switches all repositories back to their dev/main/master branch after update.'
    )

    def update_repos(args):
        config = Config()
        dirs = config.groups

        if len(dirs) > 0:
            updater = Updater(args.verbosity)
            updater.update(dirs, args.clean)
        else:
            print("No directories configured!")
            print(f"\nSet up default directories using 'gimme --config-dirs [dir_list]' "
                  f"or modify ~/{CONFIG_FILE_NAME}.")

    parser.set_defaults(func=update_repos)


def add_repo_switcher(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser(
        'repo',
        help='Search for a repository and change your working directory to it. '
             'Supports partial searches. You may also use this command by simply typing `gimme <repo name>`.')
    parser.add_argument('repo', help='The name of the repo to jump to. Supports partial searches.')

    parser.set_defaults(func=lambda args: Finder().find_repo(args.repo))


class Config:
    def __init__(self):
        super().__init__()

        self.__config_path = path.join(path.expanduser('~'), CONFIG_FILE_NAME)
        self.__load()

    def __load(self):
        try:
            with open(self.__config_path) as config:
                self.__config = json.load(config)
        except json.decoder.JSONDecodeError as e:
            msg = f'Error loading gimme configuration. ' \
                  f'Your .gimmeconfig.json should be a valid json file.\nJSON Error: \n - {e}'
            print(colored(msg, 'red'))
            sys.exit(1)
        except FileNotFoundError:
            print(colored(f'creating {self.__config_path}', 'green'))
            os.chmod(path.dirname(self.__config_path), 0o777)
            self.__config = {}
            self.__save()

    def __save(self):
        with open(self.__config_path, 'w', encoding='utf-8') as file:
            try:
                json.dump(self.__config, file, ensure_ascii=False, indent=2)
            except PermissionError:
                json.dump(self.__config, file, ensure_ascii=False, indent=2)

    @property
    def groups(self):
        if 'groups' not in self.__config:
            self.__config['groups'] = []

        return self.__config["groups"]

    @property
    def favorites(self):
        if 'favorites' not in self.__config:
            self.__config['favorites'] = []

        return self.__config["favorites"]

    @property
    def aliases(self):
        if 'aliases' not in self.__config:
            self.__config['aliases'] = {}

        return self.__config["aliases"]

    def list_groups(self):
        if len(self.groups) == 0:
            print('No groups configured.')
            return

        print('Groups:')
        for group in self.groups:
            print(f' - {group}')

    def add_group(self, group_path):
        if group_path in self.groups:
            print(f'"{group_path}" already exists in groups.')
            self.list_groups()
            return

        self.groups.append(group_path)
        self.__save()

    def remove_group(self, group_path):
        if group_path not in self.groups:
            print(f'"{group_path}" not found in groups.')
            self.list_groups()
            return

        self.groups.remove(group_path)
        self.__save()

    def list_favorites(self):
        if len(self.favorites) == 0:
            print('No favorites configured.')
            return

        print('Favorites:')
        for fav in self.favorites:
            print(f' - {fav}')

    def add_favorite(self, fpath):
        if fpath in self.favorites:
            print(f'"{fpath}" already exists in favorites.')
            self.list_favorites()
            return

        self.favorites.append(fpath)
        self.__save()

    def remove_favorite(self, fpath):
        if fpath not in self.favorites:
            print(f'"{fpath}" not found in favorites.')
            self.list_favorites()
            return

        self.favorites.remove(fpath)
        self.__save()

    def list_aliases(self):
        if len(self.aliases) == 0:
            print('No aliases configured.')
            return

        print('Aliases:')
        for key, value in self.aliases.items():
            print(f" - '{key}' → '{value}'")

    def add_alias(self, alias, actual):
        if alias in self.aliases:
            print(f'"{alias}" already exists in aliases.')
            self.list_aliases()
            return

        self.aliases[alias] = actual
        self.__save()

    def remove_alias(self, alias):
        if alias not in self.aliases:
            print(f'"{alias}" not found in aliases.')
            self.list_aliases()
            return

        del self.aliases[alias]
        self.__save()


class Lister:
    def __init__(self):
        super().__init__()
        self.log = Logger()

    def list_repositories(self, directories):
        """Lists all repositories in the given directories.

        dirs: List - the list of paths to search for repositories under. The search is not recursive.
        """
        for directory in directories:
            self.__list_branches_in_directory(directory)

    def __list_branches_in_directory(self, directory):
        """Lists the branches of all repos directly under the given directory.

        dir: str - The directory to search under.
        """
        found_at_least_one = False
        try:
            full_path = path.expanduser(directory)
            os.chdir(full_path)
        except Exception as _:
            self.log(f"No such directory '{directory}'...")
            return

        code_path = os.getcwd()

        sub_dirs = []

        for repo in os.listdir(code_path):
            dir_path = path.join(code_path, repo)

            if Utils.is_repo(dir_path):
                if not found_at_least_one:
                    found_at_least_one = True
                    self.log(f"{full_path}:")
                self.__list_branches(dir_path, repo)

            elif Utils.is_directory(dir_path):
                sub_dirs.append(dir_path)

        for sub_dir in sub_dirs:
            self.__list_branches_in_directory(sub_dir)

    def __list_branches(self, path: str, repo_name):
        """List the branches of a specific repository.

        path: str - the path to the repository.
        repo_name: str - the name of the repository.
        """
        self.log(f"    {repo_name}")
        os.chdir(path)
        repo = git.Repo(path)
        for branch in repo.branches:
            if branch.name == repo.active_branch.name:
                self.log(f'      * {branch.name}')
            else:
                self.log(f'      - {branch.name}')


class Updater:
    NO_CHANGES_STASHED = "No local changes to save"

    def __init__(self, verbosity=0):
        super().__init__()
        self.log = Logger(verbosity)

    def update(self, dirs, switch_to_main=False):
        """Walks through each repo in each of the directories listed above, updating the trunk with its configured remote branch.

        dirs: List - The list of directories. This function will search directly under these directories for repos to update.
        switch_to_main: Boolean (default: False) -
            Whether to switch all repositories back to their trunk after updating.
            If True, each repo will be set back to whatever its main branch is.
            Otherwise, it will remain on its current branch after update.
        """
        for code_dir in dirs:
            self.__update_repos_in_directory(code_dir, switch_to_main)

    def __update_repos_in_directory(self, directory: str, switch_to_main=False):
        """Update each repo in the given directory.

        dir: str - The directory to search for repositories under.
        switch_to_main: Boolean (default: False) -
            Whether to switch all repositories back to their trunk after updating.
            If True, each repo will be set back to whatever its main branch is.
            Otherwise, it will remain on its current branch after update.
        """
        try:
            os.chdir(path.expanduser(directory))
        except Exception as _:
            self.log(f"No such directory '{directory}'...")
            return
        code_path = os.getcwd()

        sub_dirs = []
        for repo in os.listdir(code_path):
            dir_path = path.join(code_path, repo)

            is_repo = Utils.is_repo(dir_path)
            if is_repo:
                self.__clean_update(dir_path, repo, switch_to_main)
            elif not is_repo and Utils.is_directory(dir_path):
                sub_dirs.append(dir_path)

        for sub_dir in sub_dirs:
            self.__update_repos_in_directory(sub_dir, switch_to_main)

    def __clean_update(self, update_path: str, repo_name, switch_to_main):
        """
        Stashes changes on the current branch,
        and then pulls the latest changes from the main branch of the repo.

        path: str - the path to a repository.
        repo_name: str - the name of the repository.
        switch_to_main: Boolean - whether the repository should stay on the main trunk after updating.
          If true, the repo will stay on its main trunk.
          Otherwise, the repo will switch back to the branch it started on.
        """
        self.log.minimal(f"- Updating '{repo_name}'...", end='')
        self.log.print_banner(f"Pulling Latest Changes from '{repo_name}'", 80)

        os.chdir(update_path)
        repo = git.Repo(update_path)

        stashed_changes = False
        self.log.verbose(" * Stashing changes on current branch...", end="")
        try:
            stashed_changes = repo.git.stash("save") != self.NO_CHANGES_STASHED
            self.log.verbose("done")
        except Exception as e:
            self.log.minimal(colored(f'error\n{e}', 'red'))
            return

        current_branch = repo.active_branch.name

        repo.git.rev_parse()
        result = gcmd.execute(["git", "rev-parse", "--abbrev-ref", "origin/HEAD"])
        branch = result.split("/")[-1]

        try:
            self.log.verbose(f" * Switching to {branch}...", end="")
            repo.git.checkout(branch)
            self.log.verbose("done")
        except:
            self.log.minimal(colored("error", 'red'))
            self.log.minimal(f"-> Are you sure branch \"{branch}\" exists in {repo_name}?")

        self.log.verbose(f" * Stashing changes on {branch}...", end="")
        try:
            repo.git.stash("save")
            self.log.verbose("done")
        except Exception as e:
            self.log.minimal(colored(f'error: \n{e}', 'red'))

        try:
            self.log.verbose(" * Pulling changes...", end="")
            repo.config_writer().set_value("pull", "rebase", "false").release()
            repo.remotes.origin.pull()
            self.log.verbose("done")
        except:
            self.log.minimal(colored('error', 'orange'))
            self.log.minimal(colored('-> Are you connected to the internet and your VPN?', 'orange'))
            exit(1)

        if not switch_to_main:
            self.log.verbose(f" * Switching back to {current_branch}...", end="", )
            repo.git.checkout(current_branch)
            self.log.verbose('done')
            if stashed_changes:
                self.log.verbose(' * Unstashing changes...', end='')
                repo.git.stash('pop')
                self.log.verbose('done')

        self.log.print_banner("Finished", 80)
        self.log.verbose()
        self.log.minimal('done')


class Finder:
    def __init__(self, config=None):
        super().__init__()
        self.config = config if config is not None else Config()


    def find_repo(self, repo):
        """Search for a given repo through the list of configured directories.

        repo: str - the name (or partial name) of the repo to search for.
        config: Config - the gimme util's config object
        """
        repo = self.__alias(repo)

        for fav in self.config.favorites:
            if Utils.is_repo(fav) and repo.lower() in fav.lower():
                print(fav)
                return

        for group in self.config.groups:
            gpath = self.__find_repo_in_directory(repo, group)
            if gpath is not None:
                print(gpath)
                return

    def __alias(self, repo):
        return repo if repo not in self.config.aliases else self.config.aliases[repo]

    def __find_repo_in_directory(self, repo, directory):
        """Search for a repo under one directory.

        repo: str - the name (or partial name) of the repo to search for.
        dirs: str - the directory to search through.
        """
        try:
            os.chdir(path.expanduser(directory))
        except:
            return

        code_path = os.getcwd()

        for sub_dir in os.listdir(code_path):
            dir_path = path.join(code_path, sub_dir)

            is_repo = Utils.is_repo(dir_path)
            if is_repo and repo.lower() in sub_dir.lower():
                return dir_path
            elif not is_repo and Utils.is_directory(dir_path):
                rpath = self.__find_repo_in_directory(repo, dir_path)
                if rpath is not None:
                    return rpath


class Utils:
    @staticmethod
    def is_repo(dir_path):
        """Checks whether a given directory appears to be a repository.

        dir_path: str - the path to check.
        """
        return path.isdir(dir_path) \
            and dir_path != '.' \
            and '.git' in os.listdir(dir_path)

    @staticmethod
    def is_directory(dir_path, allow_hidden=False):
        return path.isdir(dir_path) \
            and 'node_modules' not in dir_path \
            and (allow_hidden or path.basename(dir_path)[0] != '.')

    @staticmethod
    def get_install_dir():
        install_path = shutil.which('gimme')
        if install_path is None:
            install_path = shutil.which('gimmetool')
        return path.dirname(install_path)


class Logger:
    """Logger

    This class is responsible for logging outputs to the console at various verbosity levels.
    """

    def __init__(self, verbosity=0):
        self.verbosity = verbosity

    def print_banner(self, message: str, maxlen: int):
        """Prints a single line banner containing the given message.
        """
        start = f" ---- {message} "
        banner = start + ("-" * (maxlen - len(start)))
        self.print(banner, verbosity=1)

    def verbose(self, message="", end='\n', flush=True):
        """Prints a message only if the user has asked for verbose output.
        """
        self.print(message, verbosity=1, end=end, flush=flush)

    def __call__(self, message="", end='\n', flush=True):
        """Prints a message.
        """
        print(message, end=end, flush=flush)

    def minimal(self, message="", end='\n', flush=True):
        """Prints a message only if the user has not asked for verbose output.
        """
        self.print(message, end=end, flush=flush)

    def print(self, message="", verbosity=0, end='\n', flush=True):
        """Prints a message only if the user's verbosity matches what it's passed in.
        """
        if self.verbosity == verbosity:
            print(message, end=end, flush=flush)


if __name__ == "__main__":
    main()
