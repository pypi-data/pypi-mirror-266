import json
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from .logger import Logger
import time
import requests

class Fedml:
    def __init__(self, aic_service_key):
        self.logger = Logger.get_instance()
        self._create_ai_core_connection(aic_service_key)
        return
    
    def _create_ai_core_connection(self, aic_service_key):
        try:
            with open(aic_service_key) as ask:
                ai_core_json = json.load(ask)
            self.logger.info("Creating AI Core Connection ....")
            self.ai_core_client = AICoreV2Client(
                base_url = ai_core_json["serviceurls"]["AI_API_URL"] + "/v2", # The present AI API version is 2
                auth_url=  ai_core_json["url"] + "/oauth/token",
                client_id = ai_core_json['clientid'],
                client_secret = ai_core_json['clientsecret']
            )
            self.logger.info("Sucessfully Created AI Core Connection")
        except Exception as e:
            self.logger.error("AI Core Connection Unsuccessful: " + str(e))
            raise
        
    def _onboard_github_repo(self, name, url, username, password):
            self.ai_core_client.repositories.create(
                name = name,
                url = url,
                username = username,
                password = password
            )
            response = self.ai_core_client.repositories.query()
            for repository in response.resources:
                print('Name:', repository.name)
                print('URL:', repository.url)
                print('Status:', repository.status)
    
    def onboard_ai_core(self, resource_group, github_info_path, 
                        create_resource_group=False, 
                        onboard_new_repo=False, 
                        secret_path=None):
        
        if create_resource_group:
            self.logger.info("Creating resource group....")
            self.ai_core_client.resource_groups.create(resource_group)
            resource_group_details = self.ai_core_client.resource_groups.get(resource_group_id=resource_group)
            while resource_group_details.__dict__["status"]== "PROVISIONING":
                resource_group_details = self.ai_core_client.resource_groups.get(resource_group_id=resource_group)
            self.logger.info(f"{resource_group_details.resource_group_id} resource group: {resource_group_details.status_message}.")
        
        if onboard_new_repo:
            self.logger.info("Onboarding Github Repository....")
            with open(github_info_path) as file:
                git_key = json.load(file)
            self._onboard_github_repo(git_key["name"], 
                                      git_key["url"], 
                                      git_key["username"], 
                                      git_key["password"])
        
        if secret_path is not None:
            self.logger.info("Creating secret....")
            with open(secret_path) as file:
                secret = json.load(file)
            response = self.ai_core_client.docker_registry_secrets.create(
                name = secret["name"],
                data = secret["data"])
            self.logger.info(response.__dict__)

    def register_application(self, application_details):
        if application_details is not None:
            try:
                response = self.ai_core_client.applications.create(**application_details) 
                self.logger.info(response.__dict__)
            except Exception as e:
                self.logger.error("Could not register application: " + str(e))
                raise
            
            response = self.ai_core_client.applications.get_status(application_name=application_details["application_name"])
            while response.message == "Unknown":
                response = self.ai_core_client.applications.get_status(application_name=application_details["application_name"])

            self.logger.info(response.message)

    def _create_deploy_configuration(self, deployment_config):
        config_response = self.ai_core_client.configuration.create(**deployment_config)
        self.logger.info(config_response.__dict__)
        if(config_response.__dict__["message"] == "Configuration created"):
            response = self.ai_core_client.configuration.query(
                resource_group = deployment_config['resource_group']
            )
            for configuration in response.resources:
                self.logger.info(configuration.__dict__)
                if configuration.name == deployment_config['name']:
                    return True,config_response
        return False,config_response
    
    def ai_core_deploy(self, deployment_config):
        if deployment_config is not None:
            created,config_response = self._create_deploy_configuration(deployment_config)
            if created:
                deployment_response = self.ai_core_client.deployment.create(
                    resource_group = deployment_config['resource_group'],
                    configuration_id = config_response.__dict__['id']
                )
                self.logger.info(deployment_response.__dict__)
                while str(deployment_response.status) != 'Status.RUNNING' and str(deployment_response.status) != 'Status.DEAD':
                    time.sleep(15)
                    deployment_response = self.ai_core_client.deployment.get(
                        resource_group = deployment_config['resource_group'],
                        deployment_id = deployment_response.__dict__['id']
                    )
                    self.logger.info("Deployment status...." + str(deployment_response.status))
                if str(deployment_response.status) == "Status.DEAD":
                    self.logger.error("Error deploying to AI Core" + str(deployment_response.__dict__))
                elif str(deployment_response.status) == "Status.RUNNING":
                    self.logger.info("Sucessfully deployed. " + str(deployment_response.__dict__))
                    self.logger.info("Deployment url: " + str(deployment_response.deployment_url))
                    self.logger.info("Invoke endpoint using: " +  str(deployment_response.deployment_url)+"/v2/invocations")
                    return str(deployment_response.deployment_url)+"/v2/invocations"

    def get_ai_core_token(self):
        return self.ai_core_client.rest_client.get_token()
    
    def ai_core_inference(self, endpoint, headers, body):
        response = requests.post(endpoint, headers=headers, data=body)
        return response
        
