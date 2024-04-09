from setuptools import setup, find_packages

setup(
    name='newswacafi',
    version='0.2',
    packages=find_packages(),
    install_requires=['requests'],
    author='DRC WANALA',
    author_email='contact@newswacafi.online',
    description='Une bibliothèque Python pour interagir avec l\'API de Newswacafi.',
    url='https://github.com/votre_utilisateur/mon_projet',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11.7',
    readme = "README.md"
)