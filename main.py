"""
Scrape info from www.Slashdot.org
"""

__author__ = 'Phillip Orviss'

from bs4 import BeautifulSoup
import mechanize
import cookielib
import datetime
import re

"""Create browser instance"""

def instantiatebrowser():
    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    #br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    return br

"""Process date string data into datetime format"""

def processdatedata(data):

    def getMonth(x):
        return {
            'january': 1,
            'february': 2,
            'march': 3,
            'april': 4,
            'may': 5,
            'june': 6,
            'july': 7,
            'august': 8,
            'september': 9,
            'october': 10,
            'november': 11,
            'december': 12
            }.get(x, None)

    datestring = (data[4]+str(getMonth(data[2].lower()))+data[3]).replace(',','')

    return datetime.datetime.strptime(datestring, "%Y%m%d").date()

"""Attempt login to Slashdot.org website. Return to login if error occurs"""

browser = instantiatebrowser()
loginSuccess = False

while loginSuccess is False:
    username = raw_input('Please enter your Slashdot.org username: ')
    password = raw_input('Please enter your Slashdot.org password: ')
    browser.open('http://www.slashdot.org')
    browser.select_form(nr=1)
    browser.form['unickname'] = username
    browser.form['upasswd'] = password
    browser.submit()
    soup = BeautifulSoup(browser.response().read())
    if soup.find('div', {'class':'error'}) is None:
        loginSuccess = True
        print 'Login successful!'
    else:
        print 'Your username or password was entered incorrectly. Please try again.'

"""After successful login, get request_date, and scrape site"""

request_date = raw_input('Please enter the date that you would like to retrieve articles from (YYYY-MM-DD): ')
found_last_article = False
resultList = []

while found_last_article is False:
    soup = BeautifulSoup(browser.response().read())
    articleList = soup.body.find_all('h2', {'class':'story'})

    for article in articleList:
        title = article.find('span', {'id':re.compile('^title')}).text
        date = processdatedata(article.parent.find('time').text.split(' ')).strftime('%Y-%m-%d')
        author = article.parent.find('a', {'rel':'nofollow'}).text

        if date > request_date:
            resultset = {'headline': title, 'author': author, 'date': date}
            resultList.append(resultset)
        else:
            found_last_article = True

    if found_last_article == False:
        browser.follow_link(text='Older \xc2\xbb')

"""Output to results to console"""

print resultList