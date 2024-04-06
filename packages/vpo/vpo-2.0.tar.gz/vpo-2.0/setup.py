from setuptools import setup, find_packages

setup(
    name="vpo",
    version="2.0",
    author="VP_Services",
    author_email="discordyashing@gmail.com",
    url="https://github.com/hackiyui/vpimport",
    description="Un package qui vous facilitera la vie: un système de keyauth automatique par exemple",
    packages=['vpo'],
    install_requires=["win32security", "uuid", "wmi", "datetime", "uuid", "pystyle"],
    python_requires=">=3.11",
    classifiers=[
        "Environment :: Win32 (MS Windows)",
        "Natural Language :: French",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: System",
        "Topic :: System :: Logging",
    ],

)