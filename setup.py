from setuptools import setup

setup(
    name='easy_tcp',
    version='1.0',
    py_modules=['easy_tcp'],
    install_requires=[
        'twisted==17.5.0',
        'werkzeug==0.14.1',
        'setuptools==39.2.0'
    ],
    platforms=['any'],
    python_requires='>=3.6',
    description='This is a simple wrapper for Twisted TCP',
    url='https://github.com/pufit/easy-tcp',
    author='pufit',
    author_email='budanov01@bk.ru',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
