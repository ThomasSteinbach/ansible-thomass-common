"""
Ansible Plugin implementing the include_defaults action.

Like include_vars, but the included defaults can be overridden by the
inventory or by group vars. Can be used to read the defaults from another role.

Usage: drop it into a directory called ``action_plugins`` in your playbook
directory. Then you can use it with::

    - name: get the defaults from the web server role
      action: include_defaults roles/web/defaults/main.yml

Proposed for inclusion in <https://github.com/ansible/ansible/pull/8808>.

"""
# (c) 2014 Daniele Varrazzo <daniele.varrazzo@gmail.com>

import os
from ansible.utils import template
from ansible import utils
from ansible import errors
from ansible.runner.return_data import ReturnData

class ActionModule(object):

    TRANSFERS_FILES = False

    def __init__(self, runner):
        self.runner = runner

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):

        if not module_args:
            result = dict(failed=True, msg="No source file given")
            return ReturnData(conn=conn, comm_ok=True, result=result)

        source = module_args
        source = template.template(self.runner.basedir, source, inject)

        if '_original_file' in inject:
            source = utils.path_dwim_relative(inject['_original_file'], 'defaults', source, self.runner.basedir)
        else:
            source = utils.path_dwim(self.runner.basedir, source)

        if os.path.exists(source):
            data = utils.parse_yaml_from_file(source, vault_password=self.runner.vault_pass)
            if data and type(data) != dict:
                raise errors.AnsibleError("%s must be stored as a dictionary/hash" % source)
            elif data is None:
                data = {}
            inject['defaults'].update(data)
            return ReturnData(conn=conn, comm_ok=True, result={})
        else:
            result = dict(failed=True, msg="Source file not found.", file=source)
            return ReturnData(conn=conn, comm_ok=True, result=result)
