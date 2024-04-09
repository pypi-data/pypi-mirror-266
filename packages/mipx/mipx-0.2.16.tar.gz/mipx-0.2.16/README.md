python setup.py sdist bdist_wheel
python setup.py install 


python setup.py sdist
twine upload --repository pypi dist/*    // 用token 登录