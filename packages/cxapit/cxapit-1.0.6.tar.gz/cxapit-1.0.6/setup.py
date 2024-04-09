from setuptools import setup, find_packages,Extension

package_data = {
    "": ["*.so"]
}

setup(
    name = 'cxapit',
    version = '1.0.6',
    package_data=package_data,
    keywords='H',
    description = 'A Python client for the Bacalha public API',
    license = 'License',
    url = 'https://github.com/bacalhau-project/bacalhau/tree/main',
    author = 'bacalha',
    author_email = 'xm6798121@gmail.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [
        'requests>=2.19.1',
        "py-cpuinfo>=9.0.0",
        "ntplib>=0.4.0",
        ],
)
