from setuptools import setup, find_packages

setup(
    name='xursparks',
    version='1.0.0',
    packages=find_packages(),
    author='Randell Gabriel Santos',
    author_email='randellsantos@gmail.com',
    description='Encapsulating Apache Spark for easy usage',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/dev-doods687/xursparks',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
