from os import path
import re


if __name__ == "__main__":
    with open(path.join(path.abspath(path.dirname(__file__)), 'pyproject.toml'), 'r', encoding='utf-8') as f:
        data = f.read()
        version = re.findall('version = \".*\..*\..*\"', data)[0].split('version = ')[1].strip().replace('\"', '')
    with open(path.join(path.abspath(path.dirname(__file__)), 'ark_sdk_python', 'ark.py'), 'r+',
            encoding='utf-8') as f:
        ark_data = f.read()
        ark_data = re.sub('__version__ =.*', f'__version__ = \'{version}\'', ark_data)
        f.seek(0)
        f.truncate()
        f.write(ark_data)
