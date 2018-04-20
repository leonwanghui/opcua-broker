from setuptools import setup, find_packages

install_requires = ["opcua", "flask", "openbrokerapi"]

setup(name="opcua-broker",
      version="0.0.1",
      description="Python OPC-UA service broker module",
      author="Leon Wang",
      author_email="wanghui71leon@gmail.com",
      url='https://github.com/leonwanghui/opcua-broker.git',
      packages=find_packages(),
      provides=["opcua"],
      license="Apache-2.0",
      install_requires=install_requires,
      extras_require={
          'encryption': ['cryptography']
      },
      classifiers=["Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "Operating System :: OS Independent",
                   "License :: OSI Approved :: Apache-2.0",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      entry_points={}
      )

