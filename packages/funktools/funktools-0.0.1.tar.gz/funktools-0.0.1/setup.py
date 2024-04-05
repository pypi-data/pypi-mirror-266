from setuptools import find_packages, setup

setup(
    name='funktools',
    version='0.0.1',
    packages=find_packages(),
    python_requires='>=3.12',
    url='https://github.com/cevans87/funktools',
    license='mit',
    author='cevans87',
    author_email='c.d.evans87@gmail.com',
    description='Python 3.12+ async/sync memoize and rate decorators',
    extras_require={
        'base': (base := []),
        'test': (test := base + ['pytest', 'pytest-asyncio', 'pytest-cov']),
    },
    install_requires=base,
)
