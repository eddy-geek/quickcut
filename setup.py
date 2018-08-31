# from distutils.dist import Distribution
import sys
import os
from setuptools import setup, find_packages

"""Quickcut's setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
http://blog.codekills.net/2011/07/15/lies,-more-lies-and-python-packaging-documentation-on--package_data-/
"""

__author__ = 'eoubrayrie'

# dist = Distribution(dict(script_args=sys.argv[1:]))
# dist.parse_command_line()
# dist.dump_option_dicts()
# print(distutils.command.install.install.user_options)

if 'install' in sys.argv and '--user' in sys.argv:
    prefix = os.path.join(os.getenv('HOME'), '.local')
else:
    prefix = '/usr/local'


with open("README.md", "r") as fp:
    long_description = fp.read()

REQUIRES = ['pysrt']

try:
    # noinspection PyUnresolvedReferences
    import pathlib
except ImportError:
    REQUIRES.append('pathlib')

try:
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    import PyQt5
except ImportError:
    if os.name == "nt":
        # On windows we can use this special repo with binaries:
        REQUIRES.append('python-qt5')
    else:
        print('''Warning: no PyQt5 is available on pypi for your platform.
                 Install it through your package manager or from
                 https://riverbankcomputing.com/software/pyqt/download5
                 or else quickcut will not start''')

s = setup(
    name='QuickCut',
    version='0.0.1',
    url='http://github.com/eddy-geek/quickcut/',
    license='GPL',
    author='Edward Oubrayrie',
    author_email='edoubrayrie@gmail.com',
    description='Video & subtitle cut on given time-range. ffmpeg/pysrt based.',
    long_description=long_description,
    keywords='video, subtitle, editor, avi, mp4, srt, ffmpeg, pysrt, pyqt',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,
    python_requires='>=3.3',
    install_requires=REQUIRES,
    setup_requires=['install_freedesktop'],  # creates desktop files if installed with pip
    entry_points={
        'gui_scripts': [
            'quickcut=quickcut:main',
        ],
    },
    desktop_entries={
        'quickcut': {
            'Name': 'QuickCut',
            'GenericName': 'Video & Subtitle Cut',
            'Categories': 'Utility;Application;Multimedia;QT;KDE;GNOME',
            'Icon': os.path.join(prefix, 'share/icons/hicolor/128x128/apps/quickcut.png'),
            'Exec': os.path.join(prefix, 'bin/quickcut')  # override buggy-for-wheels behaviour
        },
    },
    package_data={
        '': ['*.png'],
    },
    data_files=[  # Paths are relative to '<sys.prefix>'
        # ('share/applications', ['quickcut.desktop']),  # superseded by install_freedesktop
        ('share/icons/hicolor/128x128/apps', ['quickcut/quickcut.png']),
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities',
    ],
)


if 'install_data' in s.command_obj:
    print('Installed to', s.command_obj['install_data'].install_dir)
    # icon path could be cutsomized here too
