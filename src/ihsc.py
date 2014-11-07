#!/usr/bin/python
'''
ihsc - I HATE SafeConnect!!!
Created on Nov 29, 2013

@author: mhweaver
'''

import time, urllib2, random, argparse, setproctitle

URLS = ['http://www.reddit.com/api/me.json',
        'https://www.google.com/',
        'http://www.yahoo.com/',
        'http://www.bing.com/',
        'http://www.apple.com/library/test/success.html',
        'http://www.mhweaver.com/success.html']
USER_AGENTS = {'Galaxy Nexus (Android 4.0.4)': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
               'PlayStation 3': 'Mozilla/5.0 (PLAYSTATION 3; 3.55)',
               'iPad': 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
               'iPhone': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_1 like Mac OS X; zh-tw) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8G4 Safari/6533.18.5'}

DELAY = 30

''' Make options a global variable and initially assume there are no args 
    This way, the settings start with their initial values as the defaults
    (to make main() work properly)
'''
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--single', help="only send a single request", action="store_true")
parser.add_argument('-v', '--verbose', help="verbose mode", action="store_true")
parser.add_argument('-d', '--delay', help='number of seconds to wait between requests',
                    default=DELAY, type=int)
parser.add_argument('-r', '--redirect_only', help='only show redirect responses', action='store_true')
parser.add_argument('-gt', '--geek-tool', help='return a useful exit status, for use with GeekTool',
                    action='store_true')
parser.add_argument('-ua', '--user-agent', help='the User-Agent to use', type=str,
                    default=None, nargs='+')
parser.add_argument('-u', '--urls', help='list of URLs to use (separated by spaces)', type=str,
                    default=URLS, nargs='+')
options = parser.parse_args('')

def get_url():
    ''' Return a random URL from the URL list (URLS)
    '''
    return options.urls[random.randint(0, len(options.urls) - 1)]

def get_user_agent():
    ''' Return a random User-Agent from the UA list (USER_AGENTS)
    
        returns (user_agent_name, user_agent)
    '''
    
    ' If a user_agent argument is provided, use it for both the name and user-agent string'
    if options.user_agent is not None:
        ua = options.user_agent[random.randint(0, len(options.user_agent) - 1)]
        return (ua, ua)
    
    ' Turn USER_AGENTS into a dict object, then return a random (name, user-agent) pair.'
    return USER_AGENTS.items()[random.randint(0, len(USER_AGENTS.items()) - 1)]

def send_request():
    ''' Request a random page from the URL list
    
    returns (response, url): response - the response from the request; url - the URL that was requested
    '''
    
    'Create Request object with the specified user-agent and URL'
    url = get_url()
    ua = get_user_agent()
    user_agent_name = ua[0]
    user_agent = ua[1]
    
    req = urllib2.Request(url)
    req.add_header('User-Agent', user_agent)
    response = urllib2.urlopen(req)
    
    '''
    code = response.getcode()
    html = response.read()
    '''
    
    response.close()
    return (response, url, user_agent_name)

def summary_and_exit(count, redirects):
    if options.verbose:
        if not options.single:
            print 'Exiting...'
        print 'requests sent: ' + str(count) + '; redirects: ' + str(redirects)
    
    ''' If this is being used with GeekTool and a redirect has happened, exit with code 1
        This way, the status feedback icon in GeekTool will reflect whether the last request
        was redirected or not.
    '''
    if options.geek_tool and redirects > 0:
        exit(1)
    exit(0)

def print_response(response, requested_url, count, user_agent_name):
    redirected = (requested_url != response.geturl())
    if options.redirect_only and not redirected:
        return
    
    single_text = '' if options.single else (str(count) + ': ')
    redirected_text = ' (Redirected from ' + requested_url + ')' if redirected else ''
    user_agent_text = ' - ' + user_agent_name if options.verbose else ''
    
    print single_text + str(response.getcode()) + ' [' + response.geturl() + ']' + redirected_text + user_agent_text 
    
def main():
    count = 0
    redirects = 0
    try:
        while True:
            count += 1
            try:
                results = send_request()
                response = results[0]
                requested_url = results[1]
                user_agent_name = results[2]
                if requested_url != response.geturl():
                    redirects += 1
                print_response(response, requested_url, count, user_agent_name) 
            except (urllib2.URLError, urllib2.HTTPError) as e: 
                print "Error: " + e.reason
            
            " If this is just a single request, we're done. Otherwise, wait a while and repeat" 
            if options.single: 
                summary_and_exit(count, redirects)
            else: 
                time.sleep(options.delay)
    except KeyboardInterrupt:
        ' Print an empty line, to make it look pretty, then exit (possibly showing a summary)'
        
        print ''
        summary_and_exit(count, redirects)
        
    
    
if __name__ == '__main__':
    options = parser.parse_args()
    setproctitle.setproctitle("ihsc")
    main()
    