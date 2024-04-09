from setuptools import setup, find_packages

setup(
    name='andriatina-authenticator',
    version='0.1.1',
    packages=['andriatina_auth'],
    install_requires=[
        'pyotp',  # Exemple de dépendance
    ],
    author='andriatina',
    author_email='andriatina@aims.ac.za',
    description='authentificator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    #url='https://lien_vers_votre_bibliotheque',
    classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ],
    license='Universite of Antananarivo',
)