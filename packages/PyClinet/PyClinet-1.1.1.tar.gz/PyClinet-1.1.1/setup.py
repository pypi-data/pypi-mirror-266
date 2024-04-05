from setuptools import setup,find_packages

setup(
    name='PyClinet',
    version='1.1.1',
    packages= find_packages(),
    url='https://guides.github.com/features/mastering-markdown/',
    license='MIT',
    author='Luis',
    author_email='mm12mok18@gmail.com',
    description='Luis Rubika libry',
    long_description= open("README.md",'r').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
)