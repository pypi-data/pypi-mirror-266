from setuptools import find_packages, setup

setup(
    name='firestore_wrapper',
    version='0.3.1',
    packages=find_packages(),
    description='A custom wrapper for Google Firestore.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Antonio Ventilii',
    author_email='antonioventilii@gmail.com',
    license='MIT',
    install_requires=[
        'google-cloud-firestore>=2.5.0',
        'schema',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    url='https://github.com/AntonioVentilii/firestore-wrapper',
    project_urls={
        'Source Code': 'https://github.com/AntonioVentilii/firestore-wrapper',
        'Issue Tracker': 'https://github.com/AntonioVentilii/firestore-wrapper/issues',
    },
    keywords='firestore api wrapper database',
)
