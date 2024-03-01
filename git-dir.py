# #! /usr/bin/env/python

# Andriy Zatserklyaniy <zatserkl@gmail.com> Dec 9, 2023

import pathlib
import subprocess
from collections import defaultdict

class GitDir:
    """
    Creates a directory with subdirectory for each git branch and fills it with the branch content.
    If the subdirectory already exists, just update the traking content.

    Usage: run in the directory with .git repository e.g.
    GitDir().copy_branches()
    """
    def __init__(self, dir_top='git-dir'):
        """
        dir-top: a directory to envelope branch subdirectories,
                 default is git-dir
        """
        self.dir_top = pathlib.Path(dir_top)
        self.git_dir = pathlib.Path('.git')
        self.cwd = pathlib.Path.cwd()

        if self.git_dir.is_dir():
            self.git_found = True
            command = 'git for-each-ref --sort=committerdate refs/heads/ --format="%(refname:short)"'
            # print(f'command: {command}')
            self.branches = subprocess.check_output(command, shell=True).decode('utf-8').strip().split()
            # print(f'branches list: {self.branches}')
        else:
            self.git_found = False
            print(f'\nCannot find a git repository in the current dir {self.cwd}\nStop\n\n')
            return
            # raise Exception(f'Directory .git was not found in the current directory {self.cwd}\nStop.\n\n')

    @staticmethod  # to include stand-along function mkdir into class namespace
    def mkdir(dir):
        try:
            pathlib.Path(dir).mkdir(exist_ok=True, parents=True)
        except FileExistsError as e:
            print(f'***Error: name {dir} could be in use for the ordinary file\n')
            raise Exception(f'Cannot create/use directory {dir}: this name could be in use for ordinary file.\n')

    def copy_branches(self, noprefix=None, index_from=1):
        """
        Creates an envelop folder with a directory for each git branch and copies there the branch content.
        The directory name could be prefixed by an index to keep the directories sorted in the branch creation order.
        Example of the prefixed branch:
        01. my_first_branch

        noprefix:   single name or list of names: branches to exclude from prefixing with index
                    Asterisk * can be used as a wildcard for branch end, like rel*
                    prefix='*' disables prefixing
                    Default value (None) is equivalent to a list ['main', 'master']

        index_from: start prefix from this number.
        """
        if not self.git_found:
            return
        
        # branch names to be exluded from prefixing
        exclude_exact = []  # exact branch names
        exclude_start = []  # branch names startswith

        if type(noprefix) == type(''):
            # noprefix is a str
            iasterisk = noprefix.find('*')
            if iasterisk < 0:
                exclude_exact.append(noprefix)
            else:
                exclude_start.append(noprefix[:iasterisk])
        elif type(noprefix) == type([]):
            # noprefix is a list
            for b in noprefix:
                iasterix = b.find('*')
                if iasterisk < 0:
                    exclude_exact.append(b)
                else:
                    exclude_start.append(b[:iasterisk])
        else:
            # default None (and any other type)
            exclude_exact.extend(['main', 'master'])

        print(f'Create/update directory: {self.dir_top}')
        self.mkdir(self.dir_top)

        ok = True
        iprefix = index_from
        for branch in self.branches:
            # prefix for the directory name
            prefix = f'{iprefix:0>2d}. '  # prefix like "01. my_first_branch"
            if branch in exclude_exact:
                prefix = ''
            else:
                for b in exclude_start:
                    if branch.startswith(b):
                        prefix = ''
                        break
        
            branch_dir = self.dir_top / (prefix + branch)  # "git-dir/01. my_first_branch"

            if prefix:
                iprefix += 1

            if branch_dir.is_dir():
                print(f'Update subdirectory: {branch_dir}')
            else:
                print(f'Create subdirectory: {branch_dir}')
                self.mkdir(branch_dir)
            
            command = f'git archive {branch} | tar x -C "{branch_dir}"'
            # print(f'-- command: {command}')
            res = subprocess.call(command, shell=True)
            if res:
                ok = False
                print(f'  *** problem with copy files from branch {branch} -- res: {res}')

        if ok:
            print(f'Done: Copied content of git branches into subdirectories of ./{self.dir_top}/')
        else:
            print(f'There was a problem with copy of content of git branches into subdirectories of ./{self.dir_top}/')


if __name__ == '__main__':
    # GitDir().copy_branches()
    GitDir().copy_branches(noprefix='*')
