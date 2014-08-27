"""
* Sync local folders to remote /srv/[salt|pillar]
* 
"""
import os
import sys
import yaml
import pprint


import pkg_resources
pkg_resources.require("cotton>=0.2.0")

from cotton.salt_shaker import Shaker
import cotton.salt
from cotton.ssh_utils import rsync_project, ssh
from fabric.api import task, run, sudo, put, local, hide
from fabric.api import env as fab_env
from fabric.operations import open_shell
from fabric.colors import red

from lib.utils import get_pillar, approve_master_key, requires_latest_git, list_valid_envs

root = os.path.dirname(fab_env.real_fabfile)
sys.path.append(os.path.join(root, 'providers'))

fab_env.environment = "development"
fab_env.pillar_root = os.path.abspath("pillars")
fab_env.git_checking = True

def _set_env(env_name):
    env_names = list_valid_envs()
    if env_name not in env_names:
        raise ValueError(red("%s not a valid env name.\nPlease use of of %s" %
            (env_name, ", ".join(name for name in env_names))))
    fab_env.environment = env_name
    if fab_env.environment != "development":
        with hide('output', 'running'):
            fab_env.pillar = get_pillar()
            fab_env.hosts = [fab_env.pillar['local']['master_ip_public'],]

            if 'master_key_file_name' in fab_env.pillar['local']:
                fab_env.key_filename = fab_env.pillar['local']['master_key_file_name']
            if 'master_user_name' in fab_env.pillar['local']:
                fab_env.user = fab_env.pillar['local']['master_user_name']

            fab_env.domainname = fab_env.pillar['local'].get('domainname', env_name + '.civilclaims')

@task
def no_git_checking():
    """
    DON'T use this normally.  Only designed for automated jobs where we know we
    have the up to date code already.
    """
    fab_env.git_checking = False

@task
def env(env="development"):
    _set_env(env)

@task
@requires_latest_git
def init_master(**kwargs):

    # Stub out the cotton config
    fab_env.vm = True
    fab_env.vm_name = "master"

    kwargs.setdefault('salt_roles', ['master'])
    cotton.salt.bootstrap_master(**kwargs)

    set_salt_environment()
    update_master()

@task
@requires_latest_git
def init_minion(name, ip, **kwargs):
    """
    Example usage. Bit clunky :( ::

        fab env:production no_git_checking \
            -u provisioning -i pillars/provisioning_skyscape.pem \
            init_minion:ac-front,10.5.12.100,salt_roles='accelerated_claim_front;loadbalancer',install_type=-D\ git\ v2014.1.4
    """
    fab_env.vm = True
    fab_env.vm_name = name

    #fab_env.gateway = 'aberlin@' + fab_env.pillar['local']['master_ip_public']
    fab_env.host_string = ip

    kwargs.setdefault('master', fab_env.pillar['local']['master_ip_private'])
    cotton.salt.bootstrap_minion(**kwargs)
    set_salt_environment()

@task
@requires_latest_git
def vendor_formulas():
    shaker = Shaker(root_dir=os.path.dirname(fab_env.real_fabfile))
    shaker.install_requirements()

@task
@requires_latest_git
def update_master():
    vendor_formulas()

    # set_salt_environment()
    # rsync code to master and run local highstate
    dirs = [
        ('salt/', '/srv/salt/'),
        ('vendor/_root/', '/srv/salt-formulas/'),
        ("%s/base/" % fab_env.pillar_root, '/srv/pillar/base/'),
        ("%s/%s/" % (fab_env.pillar_root, fab_env.environment), '/srv/pillar/%s/' %fab_env.environment),
    ]
    for directory in dirs:
        sudo('mkdir -p %s' % directory[1])
        sudo('chown -R %s %s' % (fab_env.user, directory[1]))
        rsync_project(directory[1], directory[0], delete=True, extra_opts='-L')
    put("%s/top.sls" % fab_env.pillar_root, '/srv/pillar/top.sls', use_sudo=True),

def set_salt_environment():
    sudo("salt-call --local grains.setval 'release_stage' %s" % fab_env.environment)

@task
def accept_keys():
    sudo('salt-key -L')
    sudo('salt-key -A')

@task
@requires_latest_git
def master_highstate():
    sudo('service salt-master restart')
    sudo('service salt-minion restart')
    # approve_master_key()
    set_salt_environment()
    sudo('salt-call --local state.sls minions.master')
    sudo('salt-call state.highstate')
    sudo('service salt-master restart')

@task
@requires_latest_git
def highstate(role='*', branch='master'):
    from cotton.salt import salt
    local('nosetests')
    fab_env.saltmaster = True
    if branch != 'master':
        assert fab_env.environment != 'production', "You must deploy master in production"
    salt(role, "state.highstate pillar=\"{{'deploy_branch':'{0}'}}\"".format(branch), parse_highstate=True)

def run_cmd(role=None, command=None):
    sudo("salt '%s' cmd.run '%s'" % (role, command))

@task
def test_ping():
    sudo("salt '*' test.ping")

@task
def network_ips():
    sudo("salt '*' network.ip_addrs")

@task
def pillar_items():
    sudo("salt -C 'G@release_stage:%s' pillar.items" % fab_env.environment)

@task
def local_pillar_items():
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(fab_env.pillar['local'])


@task
def ssh_cmd():
    user = fab_env.user
    ip = fab_env.hosts[0]
    out = user + "@" + ip
    if fab_env.key_filename is not None:
        keyfiles = fab_env.key_filename
        out = out + ' -i ' + keyfiles
    print out

@task
def test_envs():
    """
    This command should print "PROD" when:
        `fab production test_envs`
    is called, and "DEV" when 
        `fab test_envs`
    is called.
    """
    pillar = get_pillar()
    ENV_NAME = pillar['local']['pillar_env']
    if fab_env.environment == "development":
        assert ENV_NAME == "DEV"
    if fab_env.environment == "production":
        assert ENV_NAME == "PROD"


