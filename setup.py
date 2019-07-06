from setuptools import setup # type: ignore

if __name__ == '__main__':
    setup(name='kython',
          version='0.1',
          description='My collection of Python utilities',
          url='http://github.com/karlicoss/kython',
          author='Dmitrii Gerasimov',
          author_email='karlicoss@gmail.com',
          license='MIT',
          packages=['kython'],
          zip_safe=False)
