"""Agave CLI

Rewriting of agave-cli in python.
"""
from __future__ import print_function
import argparse
import socket
import sys
from os import path
from agavecli import auth, clients, files, systems, tenants

# Parser and subparsers definition.
parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument(
    "-A",
    "--agavedb",
    default=path.expanduser("~"),
    help="Location of Agave database (only provide the directory). Default to homedir (~/).")

main_parser = argparse.ArgumentParser()

commands_subparsers = main_parser.add_subparsers(
    title="Commands", dest="commands_cmd")

###############################################################################
#                                                                             #
#                        Tenant Command Line Option                           #
#                                                                             #
###############################################################################
tenant_command_parser = commands_subparsers.add_parser(
    "tenant", help="Manage Agave tenants", parents=[parent_parser])

tenant_command_parser.add_argument(
    "-H",
    "--hosturl",
    default="https://api.tacc.utexas.edu/tenants",
    help="URL of Agave central service.")

tenant_action_subparser = tenant_command_parser.add_subparsers(
    title="tenantaction", dest="tenant_actioncmd")

# Tenant init command.
tenant_init_parser = tenant_action_subparser.add_parser(
    "init",
    help="Configure the context for a given tenant.",
    parents=[parent_parser])

tenant_init_parser.add_argument(
    "tenant_name", help="Name of agave tenant to use.")

# Tenant ls command.
tenant_ls_parser = tenant_action_subparser.add_parser(
    "ls",
    help="List all available tenants from the Agave central database.",
    parents=[parent_parser])


###############################################################################
#                                                                             #
#                        Client Command Line Option                           #
#                                                                             #
###############################################################################
client_command_parser = commands_subparsers.add_parser(
    "client", help="Manage Agave clients", parents=[parent_parser])

client_command_parser.add_argument(
    "-e",
    "--endpoint",
    default="clients/v2",
    help="Client service endpoint of Agave (default: clients/v2).")

client_action_subparser = client_command_parser.add_subparsers(
    title="clientaction", dest="client_actioncmd")

# Client create command.
client_create_parser = client_action_subparser.add_parser(
    "create", help="Create a new Agave client.", parents=[parent_parser])

client_create_parser.add_argument(
    "-n", "--name",
    dest="client_name",
    default=socket.gethostname(),
    help="Name of client.")

client_create_parser.add_argument(
    "-d",
    "--description",
    default="Autogenerated client",
    help="Description of client.")


# client ls command.
client_ls_parser = client_action_subparser.add_parser(
    "ls",
    help="List all Agave clients registered to the authenticated user.",
    parents=[parent_parser])


# client rm command.
client_rm_parser = client_action_subparser.add_parser(
    "rm",
    help="Delete a client application and associated API keys",
    parents=[parent_parser])

client_rm_parser.add_argument(
    "client_name",
    default=socket.gethostname(),
    help="Name of client.")


###############################################################################
#                                                                             #
#                          Auth Command Line Option                           #
#                                                                             #
###############################################################################
auth_command_parser = commands_subparsers.add_parser(
    "auth", help="Manage Agave authentication", parents=[parent_parser])

auth_command_parser.add_argument(
    "-e",
    "--endpoint",
    default="token",
    help="Token service endpoint for Agave authenticaion service (default: token).")

auth_action_subparser = auth_command_parser.add_subparsers(
    title="authaction", dest="auth_actioncmd")

# auth create command.
auth_create_parser = auth_action_subparser.add_parser(
    "create", help="Obtain a new Oauth bearer token.", parents=[parent_parser])


# auth refresh command.
auth_refresh_parser = auth_action_subparser.add_parser(
    "refresh", help="Retrieve a new Oauth bearer token.", parents=[parent_parser])


###############################################################################
#                                                                             #
#                       Systems Command Line Option                           #
#                                                                             #
###############################################################################
system_command_parser = commands_subparsers.add_parser(
    "system", help="Manage Agave systems", parents=[parent_parser])

system_command_parser.add_argument(
    "-e",
    "--endpoint",
    default="systems/v2",
    help="Systems service endpoint for Agave (default: systems/v2).")

system_command_parser.add_argument(
    "-t",
    "--token-endpoint",
    dest="token_endpoint",
    default="token",
    help="Token service endpoint for Agave (default: token).")

systems_action_subparser = system_command_parser.add_subparsers(
    title="systemsaction", dest="systems_actioncmd")

# system ls command.
system_ls_parser = systems_action_subparser.add_parser(
    "ls", help="List all Agave systems available to the authenticated user.", parents=[parent_parser])

system_ls_parser.add_argument(
    "-s", "--storage",
    action="store_true",
    help="Only list storage systems.")

system_ls_parser.add_argument(
    "-x", "--execution",
    action="store_true",
    help="Only list execution systems.")


############################################################################### 
#                                                                             # 
#                    File System Command Line Option                          # 
#                                                                             # 
###############################################################################
fs_command_parser = commands_subparsers.add_parser(
    "fs", help="Manage Agave remote filesystems", parents=[parent_parser])

fs_command_parser.add_argument(
    "-t",
    "--token-endpoint",
    dest="token_endpoint",
    default="token",
    help="Token service endpoint for Agave authenticaion service (default: token).")

fs_action_subparser = fs_command_parser.add_subparsers(
    title="fsaction", dest="fs_actioncmd")

# fs ls command.
fs_ls_parser = fs_action_subparser.add_parser(
    "ls", 
    help="List all files on a remote Agave system.", parents=[parent_parser])

fs_command_parser.add_argument(
    "-e",
    "--endpoint",
    default="files/v2/listings/system",
    help="Files-listings service endpoint for Agave (default: files/v2/listings/system).")

fs_ls_parser.add_argument(
    "-l", dest="long", action="store_true", help="Long format.")

fs_ls_parser.add_argument(
    "syspath",
    help="System ID and path (i.e., hpc-stampede2-user/apps).")

# fs mkdir command.
fs_mkdir_parser = fs_action_subparser.add_parser(
    "mkdir",
    help="Create a directory on a remote Agave system.", parents=[parent_parser])

fs_mkdir_parser.add_argument(
    "-e",
    "--endpoint",
    default="files/v2/media/system",
    help="Files-media service endpoint for Agave (default: files/v2/media/system).")

fs_mkdir_parser.add_argument(
    "syspath",
    help="System ID and path (i.e., hpc-stampede2-user/apps creates apps/ dir).")

# fs rm command.
fs_rm_parser = fs_action_subparser.add_parser(
    "rm",
    help="Delete a file or directory on a remote Agave system.", parents=[parent_parser])

fs_rm_parser.add_argument(
    "-e",
    "--endpoint",
    default="files/v2/media/system",
    help="Files-media service endpoint for Agave (default: files/v2/media/system).")

fs_rm_parser.add_argument(
    "syspath",
    help="System ID and path (i.e., hpc-stampede2-user/apps creates apps/ dir).")

# fs cp command.
fs_cp_parser = fs_action_subparser.add_parser(
    "cp",
    help="Copy a file using the Agave APIi.", parents=[parent_parser])

fs_cp_parser.add_argument(
    "-e",
    "--endpoint",
    default="files/v2/media/system",
    help="Files-media service endpoint for Agave (default: files/v2/media/system).")

fs_cp_parser.add_argument(
    "origin",
    help="File to be copied. Use the prefix 'agave://' if moving files within Agave.")

fs_cp_parser.add_argument(
    "destination",
    help="""Path to copy file to. Use the prefix 'agave://' if moving files within Agave. 
    
    To move a file from a directory to another do: ... cp /path/file.ext /newpath/ 
    (notice the destination ends with a forwards slash to denote a directory).

    To move a file from a directory and give it a new name: ... cp /path/file.ext /newpath/newname.ext
    """)



def main(args=None):
    """ Agave CLI entrypoint
    """
    if args is None:
        args = main_parser.parse_args()

    if len(sys.argv) == 1:
        main_parser.print_help()
        sys.exit(0)

    agavedb = args.agavedb
    if hasattr(args, "hosturl"):
        hosturl = args.hosturl
    if hasattr(args, "endpoint"): 
        endpoint = args.endpoint
    if hasattr(args, "token_endpoint"):
        token_endpoint = args.token_endpoint

    # tenant command.
    if args.commands_cmd == "tenant":
        # tenant init command.
        if args.tenant_actioncmd == "init":
            tenant_name = args.tenant_name
            tenants.tenant_init(hosturl, tenant_name, agavedb)
        # tenant ls command.
        elif args.tenant_actioncmd == "ls":
            tenants.tenant_list(hosturl)
    # client command.
    elif args.commands_cmd == "client":
        # client create command.
        if args.client_actioncmd == "create":
            client_name = args.client_name
            description = args.description
            clients.client_create(agavedb, endpoint, client_name, description)
        # client ls command.
        elif args.client_actioncmd == "ls":
            clients.client_list(agavedb, endpoint)
        # client rm command.
        elif args.client_actioncmd == "rm":
            client_name = args.client_name
            clients.client_delete(agavedb, endpoint, client_name)
    # auth command.
    elif args.commands_cmd == "auth":
        if args.auth_actioncmd == "create":
            auth.token_create(agavedb, endpoint)
        # auth refresh command.
        elif args.auth_actioncmd == "refresh":
            auth.token_refresh(agavedb, endpoint)
    # system command.
    elif args.commands_cmd == "system":
        # system ls command.
        if args.systems_actioncmd == "ls":
            print_execution = args.execution
            print_storage   = args.storage
            systems.system_list(agavedb, endpoint, token_endpoint, print_execution, print_storage)
    # fs command.
    elif args.commands_cmd == "fs":
        # fs ls command.
        if args.fs_actioncmd == "ls":
            syspath     = args.syspath
            long_format = args.long
            files.files_list(agavedb, token_endpoint, endpoint, syspath, long_format)
        # fs mkdir command.
        elif args.fs_actioncmd == "mkdir":
            syspath = args.syspath
            files.files_mkdir(agavedb, token_endpoint, endpoint, syspath)
        # fs rm command.
        elif args.fs_actioncmd == "rm":
            syspath = args.syspath
            files.files_remove(agavedb, token_endpoint, endpoint, syspath)
        # fs cp command.
        elif args.fs_actioncmd == "cp":
            origin      = args.origin
            destination = args.destination
            files.files_copy(agavedb, token_endpoint, endpoint, origin, destination)

if __name__ == "__main__":
    args = main_parser.parse_args()
    main(args)
