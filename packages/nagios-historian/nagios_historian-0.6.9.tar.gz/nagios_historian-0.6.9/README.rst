Title1
======

Checks historian tags and samples.

`VERSION  <nagios_historian/VERSION>`__

Install
=======

Linux::

    sudo pip3 install nagios_historian --upgrade

Also is possible to use::

    sudo python3 -m pip install nagios_historian --upgrade

On windows with python3.5::

    pip install nagios_historian --upgrade

For proxies add::

    --proxy='http://user:passw@server:port'

Usage
=====

Use the command line::

    > nagios_historian --help
      usage: nagios_historian [-h] [-u [URL]] [-e [EXTRA_ARGS]]

        optional arguments:
        -h, --help            show this help message and exit
        -u [URL], --url [URL]
                              url to check 
		--client_id
                              oauth2 client_id example client id: user01
		--client_secret
                              oauth2 client_secret client password
		--auth_url
                              oauth2 auth_url example: https://login.microsoftonline.com/company.onmicrosoft.com/oauth2/v2.0/token
		--tags
                              tags names of historian
		--oauth2
                              Flag to use or not token for oauth2 before creating the request, used to check published services that uses azure oauth2
        -e [EXTRA_ARGS], --extra_args [EXTRA_ARGS]
                              extra args


Example usage
=============

Example use:

    > nagios_historian -u "https://xxx/yyy/currentvalue?tagNames=" --client_id "admin1234" --client_secret "pass1234" --auth_url "https://xxxx/oauth/token" --oauth2 --tags "TAG1;TAG2;TAG3"


Nagios config
=============

Example command::

    define command{
        command_name  check_nagios_historian
        command_line  /usr/local/bin/nagios_historian -u "$ARG1$" --client_id "$ARG2$" --client_secret "$ARG3$" --auth_url "$ARG4$" --oauth2 --tags "$ARG5$" --extra_args='$ARG6$'
    }

Example service::

    define service {
            host_name                       SERVERX
            service_description             service_name
            check_command                   check_nagios_historian!http://url/path!admin123!pass1234!http://authurl/oauth2!Tags
            use				                generic-service
            notes                           some useful notes
    }

You can use ansible role that already has the installation and command: https://github.com/CoffeeITWorks/ansible_nagios4_server_plugins

TODO
====

* Use hash passwords
* Add Unit tests?
