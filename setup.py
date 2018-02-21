from setuptools import setup

setup(
    name='lambda-packager',
    version='0.1.0',
    description='Package up Lambda code like SAM, with some extras',
    packages=["lambda_packager"],
    package_data={
        "lambda_packager": ["Makefile"]
    },
    entry_points={
        'console_scripts': [
            'lambda-packager = lambda_packager.__main__:main'
        ],
    },
    install_requires=[
    ],
    author='Ben Kehoe',
    author_email='bkehoe@irobot.com',
    project_urls={
        "Source code": "https://github.com/benkehoe/lambda-packager",
    },
    license='Apache Software License 2.0',
    classifiers=(
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
    ),
    keywords='aws lambda cloudformation',
)