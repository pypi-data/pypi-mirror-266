from setuptools import setup


setup(name='vvm_lib',
      version='0.4',
      description='my frequently used functions',
      packages=[
          'vvm_lib'
          ],
      author_email='v.vazhinskiy@yandex.ru',
      author="vvazhinskiy",
      url="https://github.com/VazhikVM/vvm_lib",
      zip_safe=False,
      install_requires=[
          "pandas",
          "numpy",
          "psycopg2-binary",
          "hvac",
          "openpyxl",
          "requests-ntlm",
          "oauth2client",
          "gspread",
          "pymssql",
          ],
      
      )
