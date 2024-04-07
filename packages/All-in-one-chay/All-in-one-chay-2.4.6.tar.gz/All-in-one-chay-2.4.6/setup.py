# coding:UTF-8
import setuptools

setuptools.setup(
    name="All-in-one-chay",
    version="2.4.6",
    author="Chay",
    author_email="lichenyi_2020@qq.com",
    url="https://github.com/lichenyichay/All-in-one/releases/tag/v2.4.6",
    description="All-in-one",
    long_description="多功能一体机",
    python_requires=">=3.5",
    # packages=setuptools.find_packages("src"),
    packages_dir={"": "src"},
    packages_data={"": ["*.txt", "*.info", "*.properties"], "": ["data/*.*"]},
    exclude=["*.test", "*.test.*", "test.*", "test"],
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2",
                 "Programming Language :: Python :: 3"
                 ]
)
