from setuptools import setup, find_packages

setup(
    name="aether-engine",
    version="0.1.0",
    description="Zero-Latency Adaptive Edge-Cloud Compute Fabric for Low-Spec Hardware",
    author="Aether Engine Core Team",
    author_email="dev@aether-engine.org",
    url="https://github.com/your-username/aether-engine",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "websockets>=11.0",
        "pydantic>=2.0.0",
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "rich>=13.0.0",
        "cryptography>=41.0.0",
    ],
    entry_points={
        "console_scripts": [
            "aether=aether.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Distributed Computing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
)
