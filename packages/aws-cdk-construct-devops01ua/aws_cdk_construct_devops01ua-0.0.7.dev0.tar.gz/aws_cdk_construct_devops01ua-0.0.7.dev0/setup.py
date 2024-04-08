from setuptools import setup, find_packages

setup(
    name='aws_cdk_construct_devops01ua',  # Replace with your package name
    version='0.0.7-dev',  # Replace with your package version
    author='Artem Hrechanychenko',
    author_email='devops01ua@gmail.com',
    description='Sample of custom AWS CDK construct for demo purposes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        "aws-cdk-lib >= 2.0.0",
        "constructs >= 10.0.0"
    ],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
