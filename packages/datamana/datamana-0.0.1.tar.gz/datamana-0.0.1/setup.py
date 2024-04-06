from setuptools import setup, find_packages

setup(
    name = 'datamana',
    packages = find_packages(exclude=['examples']),
    version = '0.0.1',
    license='MIT',
    description = 'Dataset Manager',
    author = 'JiauZhang',
    author_email = 'jiauzhang@163.com',
    url = 'https://github.com/JiauZhang/datamana',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type = 'text/markdown',
    keywords = [
        'Deep Learning',
        'Dataset Manager',
        'Artificial Intelligence',
    ],
    install_requires=[
        'numpy',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
)