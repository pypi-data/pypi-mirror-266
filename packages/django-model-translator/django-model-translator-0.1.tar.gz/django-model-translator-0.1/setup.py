from setuptools import setup, find_packages

setup(
    name="django-model-translator",
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    author="Muhammad Mamajonov",
    author_email="muhammadbekmamajonov@gmail.com",
    description="Django Model Translator",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/muhammadmamajonov/django-model-translator.git',
    license='MIT',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django'
    ],
)