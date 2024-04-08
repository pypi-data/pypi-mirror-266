from setuptools import setup, find_packages

setup(
    name='auto_artifacts',
    version='2024.03.11',
    author='Veda Sadhak',
    author_email='vedasadhak@gmail.com',
    description='Simple service to manage your artifacts',
    long_description=open('readme.md').read(),
    include_package_data=True,
    long_description_content_type='text/markdown',
    url='https://github.com/veda-s4dhak/auto-artifacts.git',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'requests',
        'backports.pbkdf2',
        'python-multipart'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
)