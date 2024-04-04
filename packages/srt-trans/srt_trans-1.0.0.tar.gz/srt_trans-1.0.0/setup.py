from setuptools import setup, find_packages

setup(
    name='srt_trans',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            "srt_trans = srt_trans.cli:main"
        ],
    },
    install_requires=[
        # List your dependencies here
        'googletrans==3.1.0a0',
        'pysrt>=1.1.2',
        'ffmpeg_python==0.2.0'
    ],
    author='Jack',
    author_email='bumble.zhou@gmail.com',
    description='A simple translator for any SubRip(.srt) files.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/bumblezhou/srt_trans',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
