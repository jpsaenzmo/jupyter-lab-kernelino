from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='arduino_kernel',
    version='1.0',
    packages=['arduino_kernel'],
    description='Arduino kernel for Jupyter',
    long_description=readme,
    author='',
    author_email='',
    url='',
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel', 'pexpect'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
    include_package_data=True,
)
