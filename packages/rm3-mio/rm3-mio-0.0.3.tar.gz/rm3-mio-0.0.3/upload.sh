rm -rf virt2
rm -rf dist
python3 setup.py sdist bdist_wheel
[ -d virt2 ] || {  
    python3.9 -m venv virt2
}
source virt2/bin/activate
pip install twine
twine upload dist/*