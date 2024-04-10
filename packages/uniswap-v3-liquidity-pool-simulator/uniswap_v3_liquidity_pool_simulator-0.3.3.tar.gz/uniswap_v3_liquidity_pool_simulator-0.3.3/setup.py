from setuptools import setup, find_packages


setup(
    name="uniswap_v3_liquidity_pool_simulator",
    version="0.3.3",
    author="the_orthanc_tower",
    author_email="andrbaue@gmail.com",
    description="A simple simulator for Uniswap V3 liquidity pools.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/baueraj/uniswap-v3-liquidity-pool-simulator",
    project_urls={
        "Source": "https://github.com/baueraj/uniswap-v3-liquidity-pool-simulator"
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.6',
    install_requires=open('requirements.txt').read().splitlines(),
)
