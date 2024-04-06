from setuptools import setup, find_packages


setup(
    name="AlgoGrade",
    version="1.0.10",
    author="artandfi (Artem Fisunenko)",
    author_email="artyom.fisunenko@gmail.com",
    description="A library for automated grading of algorithmic tasks with grading of their intermediate stages. "
    "The grading of some computational geometry tasks are provided out of the box.",
    packages=find_packages(),
    install_requires=[line.strip() for line in open("requirements.txt", "r").readlines()],
    keywords=[
        "Python3",
        "automated grading",
        "computational geometry",
        "convex hull",
        "region search",
        "geometric search",
        "point location",
        "proximity",
        "closest pair",
        "closest points"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
