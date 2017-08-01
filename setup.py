from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(
    name='jvc_proxy',
    version='0.0.1',
    license='Apache Software License',
    url='https://github.com/dermotduffy/jvc_proxy',
    author='Dermot Duffy',
    author_email='dermot.duffy@gmail.com',
    description='Simple Python server to proxy commands to a JVC projector.',
    long_description=long_description,
    packages=find_packages(),
    keywords='jvc proxy projector',
    zip_safe=True,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'future',
		],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Home Automation',
    ],
    entry_points = {
        'console_scripts': [
            'jvc_proxy=jvc_proxy.jvc_proxy:main',
        ],
    },
)
