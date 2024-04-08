from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="OpenGLRenderer",
    version="0.1",
    packages=find_packages(),
    install_requires=["PyQt5", "numpy"],
    setup_requires=[],
    test_requires=[],
    description="An OpenGL Rendering Package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hmralavi/OpenGLRenderer",
    author="Hamid Alavi",
    author_email="hmralavi@gmail.com",
    python_requires=">=3.8",
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    keywords="OpenGL, Render, 3D",
)
