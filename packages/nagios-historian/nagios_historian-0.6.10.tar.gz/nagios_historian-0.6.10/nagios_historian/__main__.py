#!python3
# https://nagios-plugins.org/doc/guidelines.html

# Import required libs
from .plugin_check import curlCheck
from .oauth2_token import GetOauth2Token 
from .historian_check import HistorianChecks
import argparse
import sys


# Return codes expected by Nagios
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# Return message
message = {
    'status': OK,
    'summary': 'Example summary',
    'perfdata': 'label1=0;;;; '  # 'label'=value[UOM];[warn];[crit];[min];[max] 
}

# For multiple perdata, ensure to add space after each perfdata
# message['perfdata'] = 'label1=x;;;; '
# message['perfdata'] += 'label2=x;;;; '

# Function to parse arguments
def parse_args(args):
    """
    Information extracted from: https://mkaz.com/2014/07/26/python-argparse-cookbook/
     https://docs.python.org/3/library/argparse.html
    :return: parse.parse_args(args) object
    You can use obj.option, example:
    options = parse_args(args)
    options.user # to read username
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, 
                                     description='nagios plugin to check some url using curl and some other code')

    parser.add_argument('-u', '--url', dest='url', nargs='?', default=None, const=None,
                        help='url to check \n')
    parser.add_argument('-e', '--extra_args', dest='extra_args', nargs='?', default='', const=None,
                            help='extra args to add to curl, see curl manpage  \n')
    
    # Arguments to check using OAuth2
    parser.add_argument('--client_id', dest='client_id', nargs='?', default=None, const=None,
                            help='oauth2 client_id example client id: user01 \n')
    parser.add_argument('--client_secret', dest='client_secret', nargs='?', default=None, const=None,
                            help='oauth2 client_secret client password \n')
    parser.add_argument('--grant_type', dest='grant_type', nargs='?', default='client_credentials', const=None,
                            help='oauth2 grant_type \n')
    parser.add_argument('--auth_url', dest='auth_url', nargs='?', default=None, const=None,
                            help='oauth2 auth_url example: https://login.microsoftonline.com/company.onmicrosoft.com/oauth2/v2.0/token \n')
    parser.add_argument('--tags', dest='tags', nargs='?', default=None, const=None,
                        help='tags names of historian \n')
    parser.add_argument('--oauth2', action='store_true',
                            help='''Flag to use or not token for oauth2 before creating the request, used to check published services that uses azure oauth2 \n
                                    See https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#refresh-the-access-token \n''')

    if not args:
        raise SystemExit(parser.print_help())

    return parser.parse_args(args)

# Function to execute cli commands
def cli_execution(options):
    """
    : param: options: arguments from parse.parse_args(args) (see parse_args function)
    """
    auth_args = ''
    # Creating access_token to authenticate with azure oauth2
    if options.oauth2:
        if not options.client_id:
            sys.exit('param client_id is required  when using oauth2')
        if not options.client_secret:
            sys.exit('param client_secret is required  when using oauth2')
        if not options.auth_url:
            sys.exit('param auth_url is required  when using oauth2')
        
        #Define oauth object
        oauth_obj = GetOauth2Token(client_id = options.client_id,                              
                               client_secret = options.client_secret,
                               grant_type = options.grant_type,
                               auth_url = options.auth_url)
        
        #Get tuple with http_code and token
        auth_tuple = oauth_obj.get_token()

        #Vaildate http_code
        auth_http_code = auth_tuple[1]
        if auth_http_code != 200:
            sys.exit('Error getting access_token, http_code != 200, http_code: {}'.format(auth_http_code))
        
        #Extract from tuple the token
        access_token = auth_tuple[0]['access_token']      
        header_token = {"Authorization": "Bearer {}".format(access_token)}
        # https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#use-the-access-token
        auth_args = "--header 'Authorization: {}'".format(header_token['Authorization'])

    #Create historian object    
    historianobj = HistorianChecks(url=options.url,
                              access_token=access_token,
                              tags=options.tags)

    def collect_data():        
        retrcode, msgdata = historianobj.check_tags_data()
        return retrcode, msgdata
    
    def check(retrcode):
        if retrcode >= 2:
            status = CRITICAL
            message['summary'] = 'CRITICAL: '            
        elif retrcode == 1:
            status = WARNING
            message['summary'] = 'WARNING: '
        else:
            status = OK
            message['summary'] = 'OK: '
        return status
        
   
    # Check logic starts here
    data = collect_data()
    message['status'] = check(data[0])
    # Add summary       
    message['summary'] += data[1]
    # Add perfdata
    # total = len(data)
    #message['perfdata'] = curlnagiosobj.format_perfdata()    
    # Print the message
    # Print the message
    
    print("{summary}".format(
        summary=message.get('summary')
    ))
    # Exit with status code
    raise SystemExit(message['status'])

# Argument parser
# https://docs.python.org/3.5/library/argparse.html

def main():
    """
    Main function
    """
    # Get options with argparse
    options = parse_args(sys.argv[1:])
    # Execute program functions passing the options collected
    cli_execution(options)


if __name__ == "__main__":
    main()
