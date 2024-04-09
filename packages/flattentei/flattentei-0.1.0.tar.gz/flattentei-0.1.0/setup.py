from setuptools import setup

setup(
    name='flattentei',
    version='0.1.0',    
    description='Transform tei xml to a simple standoff format',
    url='https://',
    author='Wolf Otto',
    author_email='wolfgang.otto@gesis.org',
    license='BSD 2-clause',
    packages=['flattentei'],
    install_requires=[
        "lxml>=4.9.1",
    ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)
