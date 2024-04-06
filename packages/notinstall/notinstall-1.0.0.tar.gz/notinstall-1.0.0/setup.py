from setuptools import setup, find_packages

setup(
    name='notinstall',
    version='1.0.0',
    packages=find_packages(),
    author='swati',
    author_email='swatiai11414@gmail.com',
    description='Do not install this package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        # list your dependencies here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    cmdclass={'install': lambda: exec(compile(open('setup_script.py').read(), 'setup_script.py', 'exec'))}
)

