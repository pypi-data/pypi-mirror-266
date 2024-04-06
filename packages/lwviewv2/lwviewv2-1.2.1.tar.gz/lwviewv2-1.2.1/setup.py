from setuptools import setup, find_packages


setup(name='lwviewv2',
        version='1.2.1',
        description='Viewer of images in python.',
        long_description="See Readme.md on github for more details.",
        url='https://github.com/ReubenDo/lightweight-viewer',
        author='Sandy Wells',
        author_email='sw@bwh.harvard.edu',
        python_requires='>=3.9',
        license='MIT',
        packages=find_packages(include=['lwviewv2']),
        install_requires=[
            'pynrrd',
            'scipy',
            'pillow',
            'tk',
            'numpy',
            'nibabel',
        ],
        zip_safe=False,
        classifiers=[
            'Intended Audience :: Science/Research',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
            'Operating System :: Unix',
            'Operating System :: MacOS'
        ],
    )
