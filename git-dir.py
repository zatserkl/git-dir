# #! /usr/bin/env/python

# Andriy Zatserklyaniy <zatserkl@gmail.com> Dec 9, 2023

import pathlib
import subprocess
from collections import defaultdict

class GitDir:
    """
    Creates a directory with subdirectory for each git branch and fills
    them with the branch content.

    Usage: run in the directory with .git repository e.g.
    GitDir().copy_branches()
    """
    def __init__(self, dir_top='git-dir', branch_noprefix=None):
        """
        dir-top: a directory to envelope branch subdirectories,
                 default is git-dir

        branch_noprefix: a single name or a list of names: branches to exclude
                         from prefixing with index
                         '*' disables prefixing
                         Default is ['main', 'master']
        """
        self.dir_top = pathlib.Path(dir_top)
        self.git_dir = pathlib.Path('.git')
        self.cwd = pathlib.Path.cwd()

        if type(branch_noprefix) == type(''):
            self.branch_noprefix = [branch_noprefix]
        elif type(branch_noprefix) == type([]):
            self.branch_noprefix = branch_noprefix[:]
        else:
            self.branch_noprefix = ['main', 'master']

        if self.git_dir.is_dir():
            self.git_found = True

            command = 'git branch'  # local branches only

            self.branches = subprocess.check_output(command, shell=True)
            self.branches = self.branches.decode('utf-8').strip().split()

            # remove asterisk string '*': a marker for the current branch
            # print(f'branches list with "*": {self.branches}')
            self.branches.remove('*')
            # print(f'branches: {self.branches}')

            self.branch_files = defaultdict(list)
            for branch in self.branches:
                command = f'git ls-tree -r --name-only {branch}'
                file_list = subprocess.check_output(command, shell=True)
                file_list = file_list.decode('utf-8').strip().split()
                self.branch_files[branch] = file_list
                # print(f'{branch} -- {self.branch_files[branch]}')
        else:
            self.git_found = False
            print(f'\nCannot find a git repository in the current dir {self.cwd}')
            print('Stop\n\n')
            return
            # raise Exception(f'Directory .git was not found in the current directory {self.cwd}\nStop.\n\n')

    @staticmethod  # just to namespace mkdir
    def mkdir(dir):
        try:
            pathlib.Path(dir).mkdir(exist_ok=True, parents=True)
        except FileExistsError as e:
            print(f'***Error: name {dir} is in use for the ordinary file\n')
            raise Exception(f'Cannot create/use directory {dir}: this name is in use for ordinary file.\n')

    def copy_branches(self, index_from=1):
        """
        Creates the envelop directory with a directory for each branch
        and copies there the branch content.
        The directory name is prefixed by an index to keep the directories
        sorted in the branch creation order.
        The branches listed in the self.branch_noprefix will not have a prefix.
        Example of the prefixed branch:
        01. my_first_branch

        index_from: start prefix from this number.
        """
        if not self.git_found:
            return

        print(f'Create/update directory: {self.dir_top}')
        self.mkdir(self.dir_top)

        ok = True
        for i, branch in enumerate(self.branches):
            # prefix branch's directory name by index
            branch_index = i + index_from
            branch_dir = self.dir_top / f'{branch_index:0>2d}. {branch}'
            if branch in self.branch_noprefix or self.branch_noprefix == '*':
                branch_dir = self.dir_top / branch

            if branch_dir.is_dir():
                print(f'Update subdirectory: {branch_dir}')
            else:
                print(f'Create subdirectory: {branch_dir}')
                self.mkdir(f'{branch_dir}')

            command = f'git archive {branch} | tar x -C \'{branch_dir}\''
            res = subprocess.call(command, shell=True)
            if res:
                ok = False
                print(f'  *** problem with copy files from branch {branch} -- res: {res}')

        if ok:
            print(f'Done: Copied content of git branches into subdirectories of ./{self.dir_top}/')
        else:
            print(f'There was a problem with copy of content of git branches into subdirectories of ./{self.dir_top}/')


if __name__ == '__main__':
    GitDir().copy_branches()
