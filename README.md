This plugin is in development and is not fully functional yet.

It uses the pybotvac library from https://github.com/stianaske/pybotvac.git

# Testing/development

Clone the repo

    $ git clone https://github.com:mzanetti/nymea-plugin-neato

Install dependencies (pybotvac library)

    $ cd nymea-plugin-neato
    $ pip3 install -t modules -r requirements.txt


Then start nymead manually, pointing it to the plugin

    $ NYMEA_PLUGINS_PATH=/path/to/nymea-plugin-neato nymead -n -d Neato -d PythonIntegrations


