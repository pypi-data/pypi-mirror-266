from setuptools import setup, find_packages

setup(
    name='webtextcrawler',
    version='1.0.2',
    author='Carlo Moro',
    author_email='cnmoro@gmail.com',
    description="Python project for crawling the web and extracting text.",
    packages=find_packages(),
    package_data={
        'webtextcrawler': [
            'resources/language_mapping.pkl',
        ]
    },
    include_package_data=True,
    install_requires=["langdetect", "beautifulsoup4", "requests", "jusText"],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)