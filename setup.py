import bootleg
from setuptools import setup, find_packages


install_requires = [
    'automodinit >= 0.16',
    'colorama >= 0.4.3',
    'django >= 3.1',
    'django_compressor >= 2.4',
    'django-crispy-forms >= 1.9.2',
    'django-debug-toolbar >= =3.1.1',
    'django-extensions >= 3.0.9',
    'django-ipware >= 3.0.1',
    'django-jsonview >= 2.0.0',
    'django-tables2 >= 2.3.2',
    'django-user-agents >= 0.4.0',
    'psutil >= 5.7.3',
]

setup(
    name='django-bootleg',
    version=VERSION,
    description='Django additions and ...thingies...',
    long_description=(),
    author='Saturnus Ringar',
    author_email='internets@internet-e-mail.com',
    url='https://github.com/saturnus-ringar/django-bootleg',
    download_url='https://github.com/saturnus-ringar/django-bootleg/tarball/%s' % bootleg.__version__,
    keywords=[],
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[],
    install_requires=install_requires,
)