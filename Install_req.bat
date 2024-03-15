where python
echo "setting proxies..."
set http_proxy=http://internet.ford.com:83
set https_proxy=http://internet.ford.com:83
set no_proxy=ford.com,localhost
echo %http_proxy%
echo %https_proxy%
echo %no_proxy%

pip install -r requirements.txt


pause