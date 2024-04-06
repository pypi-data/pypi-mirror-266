import setuptools

_requires = [
    'six',
    'setuptools-scm',
    'SQLAlchemy',
    'kivy_garden.ebs.gallery>=1.0',
    'kivy_garden.ebs.pdfplayer>=1.0',
    'ebs-linuxnode-core>=2.0',
    'ebs-linuxnode-gui-kivy-core>=2.0',
]

setuptools.setup(
    name='ebs-linuxnode-gui-kivy-gallery',
    url='https://github.com/ebs-universe/ebs-linuxnode-kivy-gallery',

    author='Chintalagiri Shashank',
    author_email='shashank.chintalagiri@gmail.com',

    description='Image Gallery infrastructure linuxnode applications',
    long_description='',

    packages=setuptools.find_packages(),
    install_requires=_requires,

    setup_requires=['setuptools_scm'],
    use_scm_version=True,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
    ],
)
