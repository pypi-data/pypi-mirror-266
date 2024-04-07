from setuptools import setup, find_packages

setup(
    name='tasks_loader',
    version='0.1.0',
    author='GlizzyKingDreko',
    author_email='glizzykingdreko@protonmail.com',
    description='A module for dynamically creating tasks from CSV files with extensive validation features.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/glizzykingdreko/tasks-loader',
    packages=find_packages(),
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
)
