#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests import api


class AuthTokenApi(api.AuthTokenApiEndpoint):
    pass


class JobApi(api.ApiEndpoint):
    alias = "Job API"
    url_path = '/api/job/'


class SubbieApi(api.ApiEndpoint):
    alias = "Subbie API"
    url_path = '/api/subbie/'


class SupervisorApi(api.ApiEndpoint):
    alias = "Supervisor API"
    url_path = '/api/supervisor/'


class ClientApi(api.ApiEndpoint):
    alias = "Client API"
    url_path = '/api/client/'


class FilesApi(api.ApiEndpoint):
    alias = "Files API"
    url_path = '/api/files/'


class NotesApi(api.ApiEndpoint):
    alias = "Notes API"
    url_path = '/api/notes/'


class CodeJobTypeApi(api.ApiEndpoint):
    alias = "CodeJobType API"
    url_path = '/api/code_job_type/'


class CodeSubbieTypeApi(api.ApiEndpoint):
    alias = "CodeSubbieType API"
    url_path = '/api/code_subbie_type/'


class CodePavingColourApi(api.ApiEndpoint):
    alias = "CodePavingColour API"
    url_path = '/api/code_paving_colour/'


class CodePavingTypeApi(api.ApiEndpoint):
    alias = "CodePavingType API"
    url_path = '/api/code_paving_type/'


class CodeRepairTypeApi(api.ApiEndpoint):
    alias = "CodeRepairType API"
    url_path = '/api/code_repair_type/'


class CodeDrainTypeApi(api.ApiEndpoint):
    alias = "CodeDrainType API"
    url_path = '/api/code_drain_type/'


class CodeFileTypeApi(api.ApiEndpoint):
    alias = "CodeFileType API"
    url_path = '/api/code_file_type/'


class CodeTaskTypeApi(api.ApiEndpoint):
    alias = "CodeTaskType API"
    url_path = '/api/code_task_type/'


class UserApi(api.ApiEndpoint):
    alias = "User API"
    url_path = '/api/users/'


class RoleApi(api.ApiEndpoint):
    alias = "Role API"
    url_path = '/api/roles/'
