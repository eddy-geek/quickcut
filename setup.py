__author__ = 'eoubrayrie'

""" https://packaging.python.org/en/latest/distributing.html """

from setuptools import setup

try:
    import quickcut.__version__ as version
except ImportError as e:
    version = None

REQUIRES = ['pysrt']

try:
    import PyQt5
except ImportError:
    REQUIRES.append('PyQt5')

if __name__ == '__main__':
    setup(
        name='QuickCut',
        version=version,
        url='http://github.com/eddy-geek/quickcut/',
        license='GPL',
        author='Edward Oubrayrie',
        description='Video/Subtitle Cut',
        install_requires=REQUIRES,
        setup_requires=['install_freedesktop'],  # creates desktop files if installed with pip
        entry_points={
            'gui_scripts': [
                'quickcut=quickcut:main',
            ],
        },
        # scripts,
        data_files=[
            # ('$HOME/.local/share/', ['quickcut.desktop'])
            # ('share/icons/hicolor/16x16/apps', ['icons/16x16/myapp.png']),
            # ('share/icons/hicolor/48x48/apps', ['icons/48x48/myapp.png']),
            # ('share/icons/hicolor/scalable/apps', ['icons/scalable/myapp.svg']),
        ]
    )
