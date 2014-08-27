import os
import json
import time
import tempfile
from functools import wraps

import git

from fabric.api import local
from fabric.api import env as fab_env
from fabric.contrib.files import exists
from fabric.colors import red


def approve_master_key():
    """
    approves master key
    """
    while True:
        if exists('/etc/salt/pki/master/minions/master', use_sudo=True):
            # master key already approved
            break
        if exists('/etc/salt/pki/master/minions_pre/master', use_sudo=True):
            # approving master key
            sudo('salt-key -y -a master')
            break
        print '.',
        time.sleep(1)

def get_pillar():
    """
    Makes some temp files and folders that makes salt work enough to render a 
    pillar we give it.
    """

    user = local('whoami', capture=True)
    temp_dir = tempfile.gettempdir()
    try:
        temp_folder = open("%s/local_minion_path" % temp_dir, 'r').read()
    except IOError:
        temp_folder = tempfile.mkdtemp(prefix='salt-minion-')
        with open("%s/local_minion_path" % temp_dir, 'w') as f:
            f.write(temp_folder)


    minion_file_content = """
    user: %(user)s
    grains_cache: True
    root_dir: %(temp_folder)s/
    grains:
        release_stage: %(environment)s
    pillar_opts: False
    pillar_roots:
      base:
        - %(pillar_root)s
    """ % ({
        'user': user,
        'temp_folder': temp_folder,
        'pillar_root': fab_env.pillar_root,
        'environment': fab_env.environment,
        })

    with open(os.path.join(temp_folder, 'minion'), 'w') as minion_file:
        minion_file.write(minion_file_content)
    cmd = ["salt-call",
        "-c",
        "%s/" % temp_folder,
        "pillar.items",
        "--local",
        "--out=json",]

    return json.loads(local(" ".join(cmd), capture=True))


def requires_latest_git(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if fab_env.environment in list_valid_envs() and fab_env.git_checking:
            check_git_status()
        return func(*args, **kwargs)
    return inner


def check_git_status():
    
    paths = [
        ('.', 'Deploy Repo'),
        (fab_env.pillar_root, 'Config Repo'),
    ]
    error_message = []
    check_remotes = True
    for path, name in paths:
        repo = git.Repo(path)
        if repo.is_dirty():
            check_remotes = False
            error_message.append("%s is dirty" % name)
        # Eugh, this is broken in GitPython, do it manually
        untracked = repo.git.execute(['git', 'status', '--porcelain'])
        if "??" in untracked:
            names = untracked.split('\n')
            error_message.append("The following files are untracked: \n\t%s" %
            "\n\t".join([name.strip('? ') for name in names if name.startswith('??')]))
    if check_remotes:
        for path, name in paths:
            repo = git.Repo(path)
            repo.remote('origin').fetch()
            local_sha = repo.head.object.hexsha
            remote_sha = repo.remote('origin').refs['master'].object.hexsha
            if local_sha != remote_sha:
                error_message.append(
                    "%s local commit doesn't match remote master" % name)
    
    
    if error_message:
        for message in error_message:
            print red(message)
        import sys
        sys.exit(1)


def list_valid_envs():
    return [name for name in os.listdir(fab_env.pillar_root) if os.path.isdir(os.path.join(fab_env.pillar_root, name))]

