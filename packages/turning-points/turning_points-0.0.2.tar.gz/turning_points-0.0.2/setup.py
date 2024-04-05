from setuptools import setup, find_packages

setup(
    name='turning_point_analyzer',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
    ],
    author='Your Name',
    author_email='charles.fosseprez.me@gmail.com',
    description='Analyze turning points in trajectories and calculate transition probabilities',
    url='https://github.com/lesptizami/turning_points',
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

)