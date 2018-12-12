# -*- coding: utf-8 -*-
from __future__ import print_function

__email__ = 'antsyoung@qq.com'
__version__ = '0.1.0'
__date__ = '2018-12-11'

import argparse
import yaml
import os


def is_exclude(path, file_suffixes):
    for item in file_suffixes:
        if path.endswith(item):
            return True
    return False


def is_include(path, file_suffixes):
    for item in file_suffixes:
        if path.endswith(item):
            return True
    return False


def _generate_type_config(configs, old_copyright_heads, new_copyright, update_template_file):
    """Generate complete configuration for easy use.

    Args:
        configs: `list of dict`, original type config
        old_copyright_heads: `list of str`, old copyright first line
        new_copyright: `str`, new copyright
        update_template_file: whether update .template file

    Returns:
        `list of dict`, complete configuration
    """
    for config in configs:
        config['old_heads'] = [config['prefix'] + head for head in old_copyright_heads]
        config['copyright'] = [config['copyright_start_line'] + '\n'] if config['copyright_start_line'] else []
        _new_copyright = [config['prefix'] + line + '\n' for line in new_copyright.split('\n')]
        config['copyright'].extend(_new_copyright)
        if config['copyright_end_line']:
            config['copyright'].append(config['copyright_end_line'] + '\n')
    if update_template_file:
        template_config = []
        for config in configs:
            config = config.copy()
            config['file_suffix'] = config['file_suffix'] + '.template'
            template_config.append(config)
        configs.extend(template_config)
    return configs


def _is_first_line_of_copyright(first, second, conf):
    first, second = first.strip(), second.strip()
    if conf['copyright_start_line']:
        if first.startswith(conf['copyright_start_line']):
            for head in conf['old_heads']:
                if head.strip() in second:
                    return True
    else:
        for head in conf['old_heads']:
            if head.strip() in first:
                return True
    return False


def _is_end_line_of_copyright(first, second, conf):
    first, second = first.strip(), second.strip()
    if conf['copyright_end_line']:
        if first.endswith(conf['copyright_end_line'].strip()):
            return True
    else:
        if not second.startswith(conf['prefix'].strip()):
            return True
    return False


def _get_file_type_conf(file_, conf):
    for con in conf:
        if file_.endswith(con['file_suffix']):
            return con


def update_copyright(file_, conf):
    """Update or add copyright of file_ with conf.

    Args:
        file_: path
        conf: `dict` contains copyright format, old copyright head lines and new copyright.

    Returns:
    """
    start_num, end_num = 0, 0  # previous copyright start/end line number
    with open(file_, 'r') as f:
        lines = f.readlines()
        len_lines = len(lines)

    # skip line which starts with #!/, consider shell,python,etc.
    for i in range(len_lines):
        if lines[i].startswith('#!/'):
            end_num = start_num = i + 1

    # find first line of previous copyright
    has_copyright = False
    for num in range(start_num, len_lines):
        if num + 1 >= len_lines:
            break
        if _is_first_line_of_copyright(lines[num], lines[num + 1], conf):
            end_num = start_num = num
            has_copyright = True
            break

    # find last line of previous copyright
    if has_copyright:
        end_num = len_lines
        for num in range(start_num + 1, len_lines):
            if num + 1 >= len_lines:
                end_num = len_lines
                break
            if _is_end_line_of_copyright(lines[num], lines[num + 1], conf):
                end_num = num + 1
                break
    print('=====Replaced [%s, %s) lines %s' % (start_num, end_num, file_))
    # append blank line to copyright if there is not
    if end_num < len_lines and lines[end_num].strip():
        new_lines = lines[0: start_num] + conf['copyright'] + ['\n'] + lines[end_num:]
    else:
        new_lines = lines[0: start_num] + conf['copyright'] + lines[end_num:]
    with open(file_, 'w') as f:
        f.write(''.join(new_lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='rule.yaml', help="yaml file configuration")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.load(f.read())
    # print(config)

    # append / to directory because file matched with directory suffix
    exclude_suffixes = ['/' + item if not item.startswith('/') else item for item in config['source_exclude']]
    # generate complete configuration
    type_config = _generate_type_config(config['type'], config['old_copyright_heads'], config['new_copyright'],
                                        config['update_template_file'])
    include_suffixes = [item['file_suffix'] for item in type_config]
    print('EXCLUDE suffixes: %s' % exclude_suffixes)
    print('INCLUDE suffixes: %s' % include_suffixes)
    print('TYPE_CONFIG: %s' % type_config)

    # handle general case
    source_queue = list(reversed(config['source_include']))
    while len(source_queue) > 0:
        parent = source_queue.pop()
        if os.path.isdir(parent):
            for dirname in os.listdir(parent):
                dirname = os.path.join(parent, dirname)
                if is_exclude(dirname, exclude_suffixes):
                    continue
                if os.path.isdir(dirname):
                    source_queue.append(dirname)
                    continue
                else:
                    if not is_include(dirname, include_suffixes):
                        continue
                    update_copyright(dirname, _get_file_type_conf(dirname, type_config))
        else:
            if not is_include(parent, include_suffixes):
                continue
            update_copyright(parent, _get_file_type_conf(parent, type_config))

    # handle specific cases
    specific_configs = config['specific_include']
    type_config = _generate_type_config(
        specific_configs, config['old_copyright_heads'], config['new_copyright'], False)
    for spec in type_config:
        if os.path.isdir(spec['path']):
            for dirpath, dirnames, filenames in os.walk(spec['path']):
                for filename in filenames:
                    dirname = os.path.join(dirpath, filename)
                    update_copyright(dirname, spec)
        else:
            update_copyright(spec['path'], spec)


if __name__ == '__main__':
    print("Current dir:", os.getcwd())
    main()
