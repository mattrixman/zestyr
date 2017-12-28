from setuptools import setup

setup(name='zestyr',
      version='0.1.0.dev1',
      description='Zephyr Emits Test Steps Then You Run\'em.  The goal of zestyr is to automate the creation of Zephyr test executions',
      url='https://github.com/mattrixman/zestyr',
      author='M@ Rixman',
      author_email ='zestyr@matt.rixman.org',
      license='MPL-2.0',
      keywords='zephyr test runner',
      packages=['zestyr'],
      python_requires = '>=3.6',
      entry_points={'console_scripts':['zcase = zestyr.case:main',
                                       'zexec = zestyr.exec:main',
                                        ]}
      )

