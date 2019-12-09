# OcomSoft Tests

## Notes

In order to run these tests on your local machine, do the following:

* Install xvfb, google-chrome, chromedriver, and other listed requirements below:
```sh
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get update
apt-get install xvfb
apt-get -y install libxpm4 libxrender1 libgtk2.0-0 libnss3 libgconf-2-4 unzip
apt-get -y install google-chrome-stable
apt-get -y install gtk2-engines-pixbuf
apt-get install xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic
CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/
unzip ~/chromedriver_linux64.zip -d ~/
rm ~/chromedriver_linux64.zip
sudo mv -f ~/chromedriver /usr/local/bin/chromedriver
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod 0755 /usr/local/bin/chromedriver
```
* If you intend to use Firefox as a test browser, install firefox (preferably version 49.0.1) based on the build appropriate for your machine and make a soft-link to the firefox binary under /usr/bin as follows:
```sh
wget ftp.mozilla.org/pub/mozilla.org/firefox/releases/49.0.1/linux-x86_64/en-US/firefox-49.0.1.tar.bz2
tar -xjvf firefox-49.0.1.tar.bz2
sudo rm -rf /opt/firefox
sudo mv firefox /opt/firefox49.0.1
sudo rm firefox-49.0.1.tar.bz2
sudo ln -sf /opt/firefox49.0.1/firefox /usr/bin/firefox
```
* Download and install geckodriver. This is required if you use firefox (check if the file is owned by root and has rwxr-xr-x permissions for it later):
```sh
wget https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-linux64.tar.gz
tar -xzvf geckodriver-v0.14.0-linux64.tar.gz
sudo chown root.root geckodriver
sudo chmod 755 geckodriver
sudo mv geckodriver /opt/firefox49.0.1
sudo rm geckodriver-v0.14.0-linux64.tar.gz
sudo ln -sf /opt/firefox49.0.1/geckodriver /usr/bin/geckodriver
```
* If you intend to use PhantomJs as a test browser, create a bash file, add the following lines, and run it:
```sh
PHANTOM_VERSION=phantomjs-2.1.1
ARCH=$(uname -m)

if ! [ ${ARCH} = x86_64 ]; then
    ${ARCH}=i686
fi
PHANTOM_JS=${PHANTOM_VERSION}-linux-${ARCH}
wget https://bitbucket.org/ariya/phantomjs/downloads/${PHANTOM_JS}.tar.bz2
tar xvjf ${PHANTOM_JS}.tar.bz2
sudo mv ${PHANTOM_JS} /usr/local/share/
ln -sf /usr/local/share/${PHANTOM_JS}/bin/phantomjs /usr/local/share/phantomjs
ln -sf /usr/local/share/${PHANTOM_JS}/bin/phantomjs /usr/local/bin/phantomjs
ln -sf /usr/local/share/${PHANTOM_JS}/bin/phantomjs /usr/bin/phantomjs
```
* On your settings.py, add the following:
```sh
TEST_WEBDRIVER = 'GOOGLE_CHROME'  # allows selenium browser testing using Firefox
TEST_WEBDRIVER = 'FIREFOX'  # allows selenium browser testing using Google Chrome
TEST_WEBDRIVER = 'PHANTOMJS'  # allows selenium browser testing using PhantomJs
TAKE_TEST_SCREENSHOTS = True   # If True, gets screenshots from across selenium tests and save them under tests/screenshots
TAKE_TEST_HTML = True   # If True, saves html from across selenium tests and save them under tests/html
TAKE_TEST_MAIL = True   # If True, saves mail data from across selenium tests and save them under tests/mail
logging.disable(logging.CRITICAL)   # Optional; add this to remove other console messages except from the test dumps
```
* There are settings that require API keys for third party services (e.g. Easyship, Mailchimp). Please provide these in order to run
these tests without failing.
* After installation, you can now run tests like so:
```sh
python manage.py test tests/standard   # Run standard tests only
python manage.py test tests/live       # Run selenium tests only
python manage.py test tests/standard tests/live   # Run all tests
```