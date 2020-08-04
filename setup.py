import setuptools

setuptools.setup(name="ulcarchetype",
      version=0.1,
      author="Miguel F. Astudillo",
      author_email="migferast@gmail.com",
      packages=setuptools.find_packages(),
      license="LICENSE.txt",
      description="package to estimate uncertainty related to lca archetypes",
      long_description=open("README.md").read(),
      install_requires=["pandas","brightway2",'numpy'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    ) 