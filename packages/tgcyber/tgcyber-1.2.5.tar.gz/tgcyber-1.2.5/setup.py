#  cybergram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2024-present rizaldevs <https://github.com/rizaldevs/>
#
#  This file is part of cybergram.
#
#  cybergram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  cybergram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with cybergram.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, Extension, find_packages

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="tgcyber",
    version="1.2.5",
    description="Fast and Portable Cryptography Extension Library for cybergram",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/cybergram",
    download_url="https://github.com/rizaldevs/tgcyber/releases/latest",
    author="rizaldevs",
    author_email="rizaldaitona@gmail.com",
    license="LGPLv3+",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords="cybergram telegram crypto cryptography encryption mtproto extension library aes",
    project_urls={
        "Tracker": "https://github.com/rizaldevs/tgcyber/issues",
        "Community": "https://t.me/cybergram",
        "Source": "https://github.com/rizaldevs/tgcyber",
        "Documentation": "https://docs.cybergram.org",
    },
    python_requires="~=3.7",
    packages=find_packages(),
    test_suite="tests",
    zip_safe=False,
    ext_modules=[
        Extension(
            "tgcyber",
            sources=[
                "tgcyber/tgcyber.c",
                "tgcyber/aes256.c",
                "tgcyber/ige256.c",
                "tgcyber/ctr256.c",
                "tgcyber/cbc256.c"
            ]
        )
    ]
)
