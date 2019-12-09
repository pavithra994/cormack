"""tests.utils.py - This module contains standalone utilities for Ocom test cases"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

import os
import signal
import datetime
import pathlib
import tempfile
import time

from django.core.management import call_command
from django.conf import settings
from bs4 import BeautifulSoup
# noinspection PyPackageRequirements
from PIL import Image   # Pillow->PIL
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from . import wait

# region Browser Types
FIREFOX = 'Firefox'
GOOGLE_CHROME = 'Chrome'
PHANTOMJS = 'PhantomJS'
NO_BROWSER = 'No Browser'
# endregion

# region Screen resolution in pixels
DEFAULT_SCREEN_WIDTH = 1280
DEFAULT_SCREEN_HEIGHT = 1024
# endregion

# Fixture(s) to always load and check
ALWAYS_LOAD = ['testdata/order.json']
# App to test loaddata with for current testdb content
LOAD_TEST_APP = 'order'


def console(message, tabs=0, newlines=0, verbosity=1):
    """Display text to console window if verbose setting is greater than 0

    :param str message: the text to display on the console
    :param int tabs: the number of tabs to prepend to the message
    :param int newlines: the number of newline characters to prepend to the message
    :param int verbosity: if value is 0, skip message display
    """

    if verbosity == 0:
        return

    stripped = message.strip() if isinstance(message, str) else ''

    if stripped == '':
        if newlines > 0:
            lines = '\n' * (newlines - 1)
            print(lines)
    else:
        tabbed = '\t' * tabs
        lines = '\n' * newlines
        # noinspection PyArgumentEqualDefault
        # print(lines + tabbed + stripped.encode('utf-8'))
        print(lines + tabbed + stripped)


def clear_files(directory, extensions=('.png', '.jpg')):
    """Remove files from directory

    :param str directory: the directory where the jpeg files are located
    :param tuple extensions: tuple of image file extensions
    :return: Number of tagged files, number of deleted files
    :rtype: int, int
    """

    removed = 0
    tagged = 0

    for root, dirs, files in os.walk(directory):
        for current_file in files:
            if any(current_file.lower().endswith(ext) for ext in extensions):
                tagged += 1

                # noinspection PyBroadException
                try:
                    os.remove(os.path.join(root, current_file))
                    removed += 1
                except OSError:
                    # do nothing
                    pass

    return tagged, removed


def all_fixtures(full_auth=False):
    """Get the loading sequence for all the fixtures

    :param bool full_auth: if True, use the full auth test fixture
    :return: A list containing the sequence of data fixtures to be loaded
    :rtype: list
    """

    return [
        'testdata/sites.json',
        'testdata/codeship/auth.json' if full_auth else 'testdata/codeship/auth_min.json',
        'testdata/codeship/catalogue.json',
        'testdata/flatpages.json',
        'testdata/codeship/merchant.json',
        'testdata/codeship/product.json',
        'testdata/codeship/stockrecord.json',
        'testdata/order.json']


def get_available_browser_type(webdriver_to_use=None):
    """Get the available browser type based on the current settings

    :param str webdriver_to_use: the browser to use (available are 'CHROME', 'FIREFOX', 'PHANTOMJS')
    :return: the browser type that is available after cross-matching settings
    :rtype: str
    """

    mapper = {
        'GOOGLE_CHROME': GOOGLE_CHROME,
        'FIREFOX': FIREFOX,
        'PHANTOMJS': PHANTOMJS
    }

    if webdriver_to_use is None:
        webdriver_to_use = getattr(settings, 'TEST_WEBDRIVER', 'CHROME')

    try:
        result = mapper[webdriver_to_use]
    except KeyError:
        result = NO_BROWSER
    return result


def firefox_bin_path():
    """Convenience function to get the path where the firefox binary is located, based on settings

    :return: the full path where the firefox binary is located
    :rtype: str
    """

    path = "/usr/bin/firefox" if getattr(settings, 'LOCAL_SERVER', False) else "/home/rof/firefox/firefox"

    if os.path.isfile(path):
        return path

    return ''


def get_screen_sizes(height=None, width=None):
    """Get the screen size or from definition defaults

    :param None or int height: the initial screen height
    :param None or int width: the initial screen width
    :return: the height and width of the screen
    :rtype: int, int
    """

    if width is None:
        width = DEFAULT_SCREEN_WIDTH

    if height is None:
        height = DEFAULT_SCREEN_HEIGHT

    return height, width


# noinspection PyUnusedLocal
def timeout_handler(signum, frame):
    """Timeout Handler for signal"""

    raise TimeoutException("Timeout while waiting for webdriver to be set.")


def firefox_webdriver():
    """Get Firefox browser

    :returns: Firefox webdriver, Firefox (or Chrome, if not available) definition
    :rtype: WebDriver, FIREFOX or CHROME
    """

    if firefox_bin_path() == '':
        driver, browser_type = chrome_webdriver()
        return driver, browser_type

    if settings.VERBOSE_OCOM_TEST_CLASSES:
        console("Selecting Webdriver: Firefox", tabs=1)

    caps = DesiredCapabilities.FIREFOX
    caps["marionette"] = True
    caps["binary"] = firefox_bin_path()
    old_alarm = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(wait.BROWSER_LOAD_TIMEOUT)

    try:
        result = webdriver.Firefox(capabilities=caps, log_path="/dev/null")
    except TimeoutException:
        result = None

    signal.alarm(0)
    signal.signal(signal.SIGALRM, old_alarm)
    # fix for file upload issue on selenium 3.3.0-3.3.1
    result._is_remote = False
    return result, FIREFOX


def chrome_webdriver():
    """Get Google Chrome browser

    :return: Google Chrome browser, Chrome definition
    :rtype: WebDriver, GOOGLE_CHROME
    """

    if settings.VERBOSE_OCOM_TEST_CLASSES:
        console("Selecting Webdriver: Google Chrome", tabs=1)

    # we need to add --no-sandbox option for pytest to work
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--allow-file-access-from-files")
    # chrome_options.add_argument("--disable-web-security")
    service_args = ['--log-path=/dev/null']
    old_alarm = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(wait.BROWSER_LOAD_TIMEOUT)

    try:
        result = webdriver.Chrome(chrome_options=chrome_options, service_args=service_args)
    except TimeoutException:
        result = None

    signal.alarm(0)
    signal.signal(signal.SIGALRM, old_alarm)
    return result, GOOGLE_CHROME


def phantomjs_webdriver():
    """Get PhantomJS headless browser

    :return: PhantomJS webdriver, PhantomJs definition
    :rtype: WebDriver, PHANTOMJS
    """

    if settings.VERBOSE_OCOM_TEST_CLASSES:
        console("Selecting Webdriver: PhantomJS", tabs=1)

    return webdriver.PhantomJS(), PHANTOMJS


def no_webdriver():
    """Get non-existent browser

    :return: No browser, No Browser definition
    :rtype: None, NO_BROWSER
    """

    if settings.VERBOSE_OCOM_TEST_CLASSES:
        console("No webdriver selected...", tabs=1)

    return None, NO_BROWSER


def call_command_silent(command, message='', verbosity=1, skip_checks=True, interactive=False, tabs=0):
    """Run call_command and pipe output as return object

    :param str or list command: the command or command set to run
    :param str message: the message to display
    :param int verbosity: the verbosity level. Set to zero to prevent showing messages
    :param bool skip_checks: refer to call_command options
    :param bool interactive: refer to call_command options
    :param int tabs: the number of tabs to prepend to the message
    :return: the piped output
    :rtype: str
    """

    console(message, tabs=tabs, verbosity=verbosity)

    with tempfile.TemporaryFile() as tmp:
        if isinstance(command, list):
            call_command(*command, skip_checks=skip_checks, interactive=interactive, verbosity=verbosity, stdout=tmp)
        else:
            call_command(command, skip_checks=skip_checks, interactive=interactive, verbosity=verbosity, stdout=tmp)

        tmp.seek(0)
        text = tmp.read()
        tabbed = '\t' * (tabs + 1)
        return text.replace('\n', '\n' + tabbed)


def clear_data(message="Clearing test DB contents...", verbosity=1, tabs=1):
    """Convenience function to remove existing contents from the test DB

    :param str message: the message to display
    :param int verbosity: the verbosity level. Set to zero to prevent showing messages
    :param int tabs: the number of tabs to prepend to the message
    """

    console(message, tabs=tabs, verbosity=verbosity)
    call_command('flush', interactive=False, load_initial_data=False, verbosity=verbosity)


def show_time_difference(start_time, finish_time, message="Time elapsed: ", tabs=1, newlines=0, verbosity=1):
    """Display to the console the time difference of two datetime objects in minutes and seconds

    :param datetime.datetime start_time: the starting time to compute
    :param datetime.datetime finish_time: the finish time to get the difference with start_time
    :param str message: the message to display
    :param int tabs: the number of tabs to prepend message
    :param int newlines: the number of newline characters to prepend to the message
    :param int verbosity: if value is 0, no message is shown
    """

    if verbosity > 0:
        elapsed_time = finish_time - start_time
        (quotient, remainder) = divmod(elapsed_time.total_seconds(), 60)
        console("{}{} minutes, {} seconds".format(message, int(quotient), round(remainder, 2)),
                tabs=tabs, newlines=newlines)


def load_fixtures(sequence=None, message='', clear_db=False, populate_countries=True):
    """Attempt to load fixtures into the test DB

    :param list sequence: the sequence of JSON files to load
    :param bool clear_db: if True, clears the contents of the database prior to loading fixtures
    :param str message: the message to display on the console
    :param bool populate_countries: if True, populates countries for currency conversion stuff
    """

    start_time = datetime.datetime.now()
    verbosity = 0
    load = False

    if settings.VERBOSE_OCOM_TEST_CLASSES:
        verbosity = 1
        console(message)

    if clear_db:
        clear_data(verbosity=verbosity)
        load = True

    if sequence is None:
        loading_sequence = ['loaddata'] + all_fixtures()
    else:
        loading_sequence = ['loaddata', 'testdata/order.json']

        if sequence != ALWAYS_LOAD:
            loading_sequence += list(set(sequence) - set(ALWAYS_LOAD))

    if not load:
        test_command = ['dumpdata', LOAD_TEST_APP]
        dump = call_command_silent(test_command, "Checking existence of previously-loaded fixtures...",
                                   verbosity=verbosity, tabs=1)

        if dump == '[]':
            console("Test DB is clear.", verbosity=verbosity, tabs=2)
            load = True
        else:
            console("Test DB has fixtures.", verbosity=verbosity, tabs=2)

    if load:
        if populate_countries:
            response = call_command_silent(
                'oscar_populate_countries', "Populating country info to DB...", verbosity=verbosity, tabs=1)
            console(response, verbosity=verbosity, tabs=1)

        response = call_command_silent(
            loading_sequence,
            "Loading all fixtures..." if sequence is None else "Loading fixtures from sequence...",
            verbosity=verbosity, tabs=1)
        console(response, verbosity=verbosity, tabs=1)

    show_time_difference(start_time, datetime.datetime.now(), verbosity=verbosity)


def local_test_server():
    """Get the local test server status

    :return: True if server is set to local; False if using Codeship server
    :rtype: bool
    """

    return getattr(settings, 'LOCAL_SERVER', False)


def mocks_path():
    """Get the mocks directory/path

    :return: the mocks path based on settings
    :rtype: str
    """

    return '/vagrant/tests/mocks/' \
        if local_test_server() else '/home/rof/src/github.com/sourcecoopita/store-demo/tests/mocks/'


def screenshot_path():
    """Get the screenshot directory/path

    :return: the screenshot path based on settings
    :rtype: str
    """

    return '/vagrant/tests/screenshots/' if local_test_server() else '/home/rof/screenshots/'


def image_asset_path():
    """Get the image asset path for tests

    :return: the image asset path based on settings
    :rtype: str
    """

    return '/vagrant/tests/images/' \
        if local_test_server() else '/home/rof/src/github.com/sourcecoopita/store-demo/tests/images/'


def html_path():
    """Get the html save path/directory

    :return: the html save path based on settings
    :rtype: str
    """

    return '/vagrant/tests/html/' if local_test_server() else '/home/rof/html/'


def save_html(filename_without_path, page_source, message, prettify=True):
    """Save html dump of the current page. Path is determined by LOCAL_SERVER setting

    :param str filename_without_path: The base filename without the absolute path
    :param str page_source: The html source to save
    :param str message: The message to display
    :param bool prettify: if True, prettifies html
    """

    if getattr(settings, 'TAKE_TEST_HTML', False):
        if settings.VERBOSE_OCOM_TEST_CLASSES:
            console(message)

        # check extension
        extension = os.path.splitext(filename_without_path)[1].lower()

        if extension != '.html':
            raise KeyError("Unknown extension for file: {}".format(filename_without_path))

        save_path = html_path()

        if not os.path.exists(save_path):
            pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

        with open(html_path() + filename_without_path, 'w') as html_file:
            the_html = BeautifulSoup(str(page_source), 'html.parser').prettify() if prettify else str(page_source)
            # noinspection PyArgumentEqualDefault
            html_file.write(the_html.strip())


def save_screenshot(filename_without_path, browser, message, quality=60):
    """Save screenshot of the current page. Path is determined by LOCAL_SERVER setting

    :param str filename_without_path: filename, without path
    :param selenium.webdriver.remote.webdriver.WebDriver browser: the browser to use
    :param str message: The message to display
    :param int quality: If saving as JPEG, the compression quality (higher is better)
    """

    if getattr(settings, 'TAKE_TEST_SCREENSHOTS', False):
        if settings.VERBOSE_OCOM_TEST_CLASSES:
            console(message)

        # check extension
        extension = os.path.splitext(filename_without_path)[1].lower()

        def save_jpeg():
            """Save image in JPEG format"""
            save_path = screenshot_path()

            if not os.path.exists(save_path):
                pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

            # noinspection PyProtectedMember
            temp_filename = next(tempfile._get_candidate_names())
            temp_full_path_filename = save_path + temp_filename
            browser.save_screenshot(temp_full_path_filename)
            png = Image.open(temp_full_path_filename).convert('RGBA')
            bg = Image.new('RGBA', png.size, (255, 255, 255))
            alpha_composite = Image.alpha_composite(bg, png)
            alpha_composite.save(screenshot_path() + filename_without_path, 'JPEG', quality=quality)
            # remove temp file
            os.unlink(temp_full_path_filename)

        def save_png():
            """Save image in PNG format"""

            browser.save_screenshot(screenshot_path() + filename_without_path)

        extensioner_mapper = {
            '.jpg': save_jpeg,
            '.jpeg': save_jpeg,
            '.png': save_png,
        }

        try:
            extensioner_mapper[extension]()
        except KeyError:
            raise KeyError("Unknown extension for file: {}".format(filename_without_path))


def wait_for_timeout(timeout, message="Waiting..."):
    """Wait for timeout function

    :param float timeout: the timeout to expire
    :param str message: the message to display before commencing wait
    """

    console(message, tabs=1, verbosity=1 if settings.VERBOSE_OCOM_TEST_CLASSES else 0)
    time.sleep(timeout)


def wait_for_function(condition_function, finish_message='', prewait=False):
    """Wait for function

    :param __function__ condition_function: the function to run until condition is true
    :param str finish_message: the message to display when condition check is done
    :param bool prewait: if True, waits for a time equivalent to wait.POLL_FREQUENCY before starting check
    """

    start_time = time.time()
    wait_time = start_time
    verbosity = 1 if settings.VERBOSE_OCOM_TEST_CLASSES else 0

    if prewait:
        console("Waiting...", tabs=1, verbosity=verbosity)
        time.sleep(wait.POLL_FREQUENCY)

    while time.time() < start_time + wait.PAGE_TIMEOUT:
        if condition_function():
            console(finish_message, tabs=1, verbosity=verbosity)
            return True
        else:
            time.sleep(wait.POLL_FREQUENCY)

            if time.time() >= wait_time + wait.WAIT_INTERVAL:
                console("Waiting...", tabs=1, verbosity=verbosity)
                wait_time = time.time()

    raise TimeoutException("Timed out while waiting for {}".format(condition_function.__name__))
