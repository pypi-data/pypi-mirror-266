# Django regex match

> Framework to create customized rules that match and parse urls.

## How to make migrations?

By now it's kind of weird, but it's the simplest way while this project doesn't count with manage.py.

1. Go to a repo where this package is installed.

2. Edit the model you want to change. For example, in adfusion you have to modify the file in your virtualenv `/Users/<your_user>/.pyenv/versions/3.6.7/envs/adfusion/src/django-regex-match/regex_match/models/parser.py`

3. Make migrations `python manage.py makemigrations regex_match`

4. Copy new file to this repo, e.g: `/Users/<your_user>/.pyenv/versions/3.6.7/envs/adfusion/src/django-regex-match/regex_match/migrations/0007_auto_20200715_1610.py`

## How to build, upload and try a new version

Based on https://packaging.python.org/en/latest/tutorials/packaging-projects/

1. First make your changes and edit `__version__` in `regex_match/__init__.py`

2. Build the package of new version

   2.1 Install build `python3 -m pip install --upgrade build` 

   2.2 Run build `python3 -m build`

3. Upload new version

   3.1 Install twine `python3 -m pip install --upgrade twine`

   3.2 Upload

     - To `test.pypi.org`: `python3 -m twine upload --repository testpypi dist/*`

     - To `pypi.org`: `python3 -m twine upload dist/*`

   3.3 Enter credentials, you can get them from passwords' spreadsheet

4. Install new version where you need it

   4.1 From `test.pypi.org`: `pip install --index-url https://test.pypi.org/simple/ django-regex-match==0.1.0`

   4.2 From `pypi.org`: `pip install django-regex-match==0.1.0`
