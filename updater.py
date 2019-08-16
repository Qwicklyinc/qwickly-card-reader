#!/usr/bin/env python3

import os
import shutil
from pkg_resources import parse_version


def _local_tags(parse=False):
    """
    Get version tags that are available on current machine
    
    Parameters:
    parse (bool): False to get tag strings, True to get pgk_resources.Version objects
    
    Returns:
    list: a list of tags
    """
    
    pipe = os.popen('git tag')
    local_str = pipe.read()
    pipe.close()
    
    local_tags = local_str.strip().split('\n')
    
    return list(map(parse_version, local_tags)) if parse else local_tags


def _remote_tags(parse=False):
    """
    Get version tags that are available in remote repository
    
    Parameters:
    parse (bool): False to get tag strings, True to get pgk_resources.Version objects
    
    Returns:
    list: a list of tags
    """
    
    pipe = os.popen('git ls-remote --tags')
    remote_str = pipe.read()
    pipe.close()
    
    remote_tags = map(lambda s: s.split('/')[-1], remote_str.strip().split('\n'))
    
    return list(map(parse_version, remote_tags)) if parse else list(remote_tags)


def _store_temp():
    """ Store CONFIG.json and custom images in a temporary directory """
    
    os.mkdir('temp')

    shutil.copytree(
            'images', 'temp/images/',
            ignore=shutil.ignore_patterns(
                    'config.png', 'fail.png',
                    'logo.png', 'pending.png',
                    'success.png', 'idle.png',
                    'active.png'
            )
    )

    shutil.copy('CONFIG.json', 'temp')
    

def _recover_temp():
    """ Return temporary directory contents to their original location """
    
    shutil.move('temp/CONFIG.json', 'CONFIG.json')

    for item in os.listdir('temp/images'):
        s = os.path.join('temp/images', item)
        d = os.path.join('images', item)
        shutil.move(s, d)

    shutil.rmtree('temp')


def current_version(parse=False):
    """ 
    Get version tag of currently active version
    
    Parameters:
    parse (bool): False to get a tag string, True to get a pkg_resources.Version object
    """
    
    os.chdir('/home/pi/qwickly')
    
    pipe = os.popen('git describe --tags')
    version = pipe.read()
    pipe.close()
    
    return parse_version(version.strip()) if parse else version.strip()


def update_available():
    """ Check for new version """
    
    os.chdir('/home/pi/qwickly')
    
    return max(_remote_tags(parse=True)) > current_version(parse=True)


def get_version(version):
    """
    Check out a different version
    
    Parameters:
    version (str): a version tag string
    """
    
    os.chdir('/home/pi/qwickly')
    
    if version == current_version():
        return
    elif version in _local_tags():
        _store_temp()
        os.system(f'git checkout {version}')
        _recover_temp()
        os.system('sudo reboot')
    elif version in _remote_tags():
        _store_temp()
        os.system('git fetch --all')
        os.system(f'git checkout {version}')
        _recover_temp()
        os.system('sudo reboot')
    else:
        print(f'could not find version {version}')
        return


def update():
    """ Check out newst version """
    
    newest_version = max(_remote_tags(parse=True))
    
    get_version('v' + str(newest_version))
