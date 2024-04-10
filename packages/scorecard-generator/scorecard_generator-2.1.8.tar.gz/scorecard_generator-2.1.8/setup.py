from setuptools import setup, find_packages

setup(
    name='scorecard_generator',
    version='2.1.8',
    packages=find_packages(),
    description='A Python Library for Creating Scorecards From Classification Models.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Kwadwo Daddy Nyame Owusu - Boakye',
    author_email='kwadwo.owusuboakye@outlook.com',
    url='https://github.com/knowusuboaky/scorecard_generator',
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=['scorecard', 'classification', 'woe', 'linear', 'machine learning']
)
