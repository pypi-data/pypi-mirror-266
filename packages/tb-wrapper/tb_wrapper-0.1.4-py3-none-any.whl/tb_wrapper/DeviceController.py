from tb_wrapper.handle_exception import *
from tb_wrapper.MainController import *
from typing import Dict


@handle_tb_wrapper_exception
class DeviceController(MainController):

    def __init__(self, tb_url=None, userfile=None, passwordfile=None, connection=None):
        super().__init__(tb_url, userfile, passwordfile, connection)

    def get_tenant_device(self, device_name):
        return self.tb_client.get_tenant_device(device_name)

    def check_device_exists_by_name(self, device_name):
        info_device = self.tb_client.get_tenant_device_infos(
            page_size=10000, page=0)
        found = False
        for info in info_device.data:
            if info.name == device_name:
                found = True
        return found

    def check_device_profile_exists_by_name(self, device_profile_name):
        info_device = self.tb_client.get_tenant_profile_infos(
            page_size=10000, page=0)
        found = False
        for info in info_device.data:
            if info.name == device_profile_name:
                found = True
        return found

    def create_device_with_customer(self, device_profile_id, device_name, customer_obj_id):
        device = Device(
            name=device_name, device_profile_id=device_profile_id, customer_id=customer_obj_id)
        device = self.tb_client.save_device(device)
        return device

    def create_device_without_customer(self, device_profile_id, device_name):
        device = Device(name=device_name, device_profile_id=device_profile_id)
        device = self.tb_client.save_device(device)
        return device

    def update_device_with_customer(self, device_profile_id, device_id, device_name, customer_obj_id):
        device = Device(id=device_id,
                        name=device_name, device_profile_id=device_profile_id, customer_id=customer_obj_id)
        device = self.tb_client.save_device(device)
        return device

    def update_device_without_customer(self, device_profile_id, device_id, device_name):
        device = Device(id=device_id, name=device_name,
                        device_profile_id=device_profile_id)
        device = self.tb_client.save_device(device)
        return device

    # TODO: Aggiungere un altro metodo che assegni un device esistente a un customer

    def save_device_attributes(self, device_id, scope, body):
        return self.tb_client.save_device_attributes(device_id, scope, body)

    def get_default_device_profile_info(self):
        return self.tb_client.get_default_device_profile_info()

    def save_device_telemetry(self, token, body):
        return self.tb_client.post_telemetry(token, body)

    def create_device_profile(self, device_profile_name: str, transport_type: str, profile_type: str) -> DeviceProfile:
        tenant_id = self.tb_client.get_user().tenant_id
        print("SOno in create device profile prima del costruttore")
        device_profile = DeviceProfile(
            name=device_profile_name, tenant_id=tenant_id, description=device_profile_name, type=profile_type, transport_type=transport_type)
        return self.tb_client.save_device_profile(device_profile)

    def get_device_profile_id(self, device_profile_name: str):
        device_profile = self.tb_client.get_device_profile_infos(
            page=0, page_size=10000, text_search=device_profile_name)

        return device_profile.data[0].id

    def delete_device_profile(self, device_profile_name: str):
        return self.tb_client.delete_device_profile(device_profile_id=self.get_device_profile_id(device_profile_name))

    def delete_device(self, device_id: str):
        return self.tb_client.delete_device(device_id=device_id)

    def delete_device_with_profile(self, device_profile_id: str, device_id: str):
        self.tb_client.delete_device(device_id=device_id)
        self.tb_client.delete_device_profile(
            device_profile_id=device_profile_id)
        return True

    def create_profile_from_bodyMQTT(self, params: Dict) -> DeviceProfile:
        tenant_id = self.tb_client.get_user().tenant_id
        rulechain_obj = RuleChainId(
            id=params["rulechain_id"], entity_type="RULE_CHAIN")
        configs = params["config"]["profile_data"]
        transportData = {'configuration': {'type': 'DEFAULT'},
                         'transport_configuration': {'deviceAttributesSubscribeTopic': configs["deviceAttributesSubscribeTopic"],
                                                     'deviceAttributesTopic': configs["deviceAttributesTopic"],
                                                     'deviceTelemetryTopic': configs["deviceTelemetryTopic"],
                                                     'sendAckOnValidationException': False,
                                                     'sparkplug': False,
                                                     'sparkplugAttributesMetricNames': ['Properties/*',
                                                                                        'Device '
                                                                                        'Control/*',
                                                                                        'Node '
                                                                                        'Control/*'],
                                                     'transportPayloadTypeConfiguration': {'transportPayloadType': 'JSON'},
                                                     'type': 'MQTT'}}
        profileData = DeviceProfileData(**transportData)

        device_profile = DeviceProfile(
            name=params["profile_name"], tenant_id=tenant_id, default_rule_chain_id=rulechain_obj, profile_data=profileData, type="DEFAULT", transport_type="MQTT")
        return self.tb_client.save_device_profile(device_profile)

    def create_profile_from_bodyAToken(self, params: Dict) -> DeviceProfile:
        tenant_id = self.tb_client.get_user().tenant_id
        rulechain_obj = RuleChainId(
            id=params["rulechain_id"], entity_type="RULE_CHAIN")
        configs = params["config"]
        profileData = DeviceProfileData(**configs)
        device_profile = DeviceProfile(
            name=params["profile_name"], tenant_id=tenant_id, default_rule_chain_id=rulechain_obj, profile_data=profileData, type="DEFAULT", transport_type="DEFAULT")
        return self.tb_client.save_device_profile(device_profile)

    def create_device_with_profile(self, device_body: Dict) -> Device:
        # TODO: check if device_profile and device exist before creating

        created_device = None
        credentials_type = device_body["credentials"]["credentialsType"]
        device = dict()
        if credentials_type == "MQTT_BASIC":
            profile_parameters = device_body["profile"]
            self.create_profile_from_bodyMQTT(
                profile_parameters)
            device_profile_objid = self.get_device_profile_id(
                device_body["profile"]["profile_name"])
            device["device"] = device_body["device"]
            device["device"]["deviceProfileId"] = device_profile_objid
            device["credentials"] = device_body["credentials"]
            created_device = self.tb_client.save_device_with_credentials(
                device)
        elif credentials_type == "ACCESS_TOKEN":
            profile_parameters = device_body["profile"]
            self.create_profile_from_bodyAToken(profile_parameters)
            device_profile_objid = self.get_device_profile_id(
                device_body["profile"]["profile_name"])
            if "customer_id" in device_body["device"].keys():
                created_device = self.create_device_with_customer(
                    device_profile_id=device_profile_objid, device_name=device_body["device"]["name"], customer_obj_id=device_body["device"]["customer_id"])
            else:
                created_device = self.create_device_without_customer(
                    device_profile_id=device_profile_objid, device_name=device_body["device"]["name"])

        return created_device

    """ def update_device_with_profile(self, device_body: Dict) -> Device:
        # TODO: check if device_profile and device exist before creating

        created_device = None
        credentials_type = device_body["credentials"]["credentialsType"]
        device = dict()
        if credentials_type == "MQTT_BASIC":
            profile_parameters = device_body["profile"]
            self.create_profile_from_bodyMQTT(
                profile_parameters)
            device_profile_objid = self.get_device_profile_id(
                device_body["profile"]["profile_name"])
            device["device"] = device_body["device"]
            device["device"]["deviceProfileId"] = device_profile_objid
            device["credentials"] = device_body["credentials"]
            updated_device = self.tb_client.save_device_with_credentials(
                device)
        elif credentials_type == "ACCESS_TOKEN":
            profile_parameters = device_body["profile"]
            self.create_profile_from_bodyAToken(profile_parameters)
            device_profile_objid = self.get_device_profile_id(
                device_body["profile"]["profile_name"])
            if "customer_id" in device_body["device"].keys():
                updated_device = self.update_device_with_customer(
                    device_profile_id=device_profile_objid,device_id=device_body["device"]["id"], device_name=device_body["device"]["name"], customer_obj_id=device_body["device"]["customer_id"])
            else:
                updated_device = self.update_device_without_customer(
                    device_profile_id=device_profile_objid, device_id=device_body["device"]["id"],device_name=device_body["device"]["name"])

        return updated_device
 """