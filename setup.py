from setuptools import setup, find_packages
from os import path, name

"""Quickcut's setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

__author__ = 'eoubrayrie'

here = path.abspath(path.dirname(__file__))

REQUIRES = ['pysrt']

try:
    # noinspection PyUnresolvedReferences
    import PyQt
except ImportError:
    if name == "nt":
        # We can use this special repo with binaries
        REQUIRES.append('python-qt5')
    else:
        print('''Warning: no PyQt5 is available on pypi for your platform.
                 Install it through your package manager or from
                 https://riverbankcomputing.com/software/pyqt/download5
                 or else quickcut will not start''')

setup(
    name='QuickCut',
    version='0.0.1',
    url='http://github.com/eddy-geek/quickcut/',
    license='GPL',
    author='Edward Oubrayrie',
    description='Video/Subtitle Cut on given time-range. ffmpeg/pysrt based.',
    keywords='video, subtitle, editor, avi, mp4, srt, ffmpeg, pysrt',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=REQUIRES,
    setup_requires=['install_freedesktop'],  # creates desktop files if installed with pip
    entry_points={
        'gui_scripts': [
            'quickcut=quickcut:main',
        ],
    },
    # scripts,
    # If there are data files included in your packages that need to be installed
    # package_data={
    #     'sample': ['package_data.dat'],
    # },
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    data_files=[  # Paths are relative to '<sys.prefix>/my_data'
        # ('$HOME/.local/share/', ['quickcut.desktop'])
        # ('share/icons/hicolor/16x16/apps', ['icons/16x16/myapp.png']),
        # ('share/icons/hicolor/48x48/apps', ['icons/48x48/myapp.png']),
        # ('share/icons/hicolor/scalable/apps', ['icons/scalable/myapp.svg']),
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities',
    ],
    include_package_data=True,
)
