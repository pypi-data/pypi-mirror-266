from typing import Optional

from acslib.base.connection import ACSRequestData, ACSRequestMethod, ACSRequestResponse
from acslib.ccure.base import CcureACS
from acslib.ccure.connection import CcureConnection
from acslib.ccure.search import ClearanceFilter, CredentialFilter, PersonnelFilter
from acslib.ccure.types import CredentialCreateData


class CcureAPI:
    def __init__(self, connection: Optional[CcureConnection] = None):
        self.personnel = CCurePersonnel(connection)
        self.clearance = CCureClearance(connection)
        self.credential = CCureCredential(connection)


class CCurePersonnel(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = PersonnelFilter()

    def search(
        self, terms: list, search_filter: Optional[PersonnelFilter] = None
    ) -> ACSRequestResponse:
        self.logger.info("Searching for personnel")
        search_filter = search_filter or self.search_filter
        request_json = {
            "TypeFullName": "Personnel",
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
            "DisplayProperties": search_filter.display_properties,
            "WhereClause": search_filter.filter(terms),
        }

        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
        ).json

    def count(self) -> int:
        request_json = {
            "TypeFullName": "Personnel",
            "pageSize": 0,
            "CountOnly": True,
            "WhereClause": "",
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
        ).json

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        pass

    def create(self, create_data: dict) -> ACSRequestResponse:
        pass

    def delete(self, record_id: str) -> ACSRequestResponse:
        pass


class CCureClearance(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = ClearanceFilter()

    def search(
        self, terms: list, search_filter: Optional[ClearanceFilter] = None
    ) -> ACSRequestResponse:
        self.logger.info("Searching for clearances")
        search_filter = search_filter or self.search_filter
        request_json = {
            "partitionList": [],
            "pageSize": self.connection.config.page_size,
            "pageNumber": 1,
            "sortColumnName": "",
            "whereArgList": [],
            "explicitPropertyList": [],
            "propertyList": search_filter.display_properties,
            "whereClause": search_filter.filter(terms),
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.connection.config.base_url
                + self.connection.config.endpoints.CLEARANCES_FOR_ASSIGNMENT,
                request_json=request_json,
                headers=self.connection.base_headers,
            ),
        ).json[1:]

    def count(self) -> int:
        request_options = {
            "pageSize": 0,
            "TypeFullName": "Clearance",
            "pageNumber": 1,
            "CountOnly": True,
            "WhereClause": "",
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.FIND_OBJS_W_CRITERIA,
                request_json=request_options,
                headers=self.connection.base_headers,
            ),
        ).json

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        pass

    def create(self, create_data: dict) -> ACSRequestResponse:
        pass

    def delete(self, record_id: str) -> ACSRequestResponse:
        pass


class CCureCredential(CcureACS):
    def __init__(self, connection: Optional[CcureConnection] = None):
        super().__init__(connection)
        self.search_filter = CredentialFilter()

    def search(
        self, terms: Optional[list] = None, search_filter: Optional[CredentialFilter] = None
    ) -> list:
        self.logger.info("Searching for credentials")
        if terms:
            search_filter = search_filter or self.search_filter
            request_json = {
                "TypeFullName": "SoftwareHouse.NextGen.Common.SecurityObjects.Credential",
                "pageSize": 100,
                "pageNumber": 1,
                "DisplayProperties": search_filter.display_properties,
                "WhereClause": search_filter.filter(terms),
            }
            response = self.connection.request(
                ACSRequestMethod.POST,
                request_data=ACSRequestData(
                    url=self.connection.config.base_url
                    + self.connection.config.endpoints.FIND_OBJS_W_CRITERIA,
                    request_json=request_json,
                    headers=self.connection.base_headers,
                ),
            )
            return response.json
        else:
            # return all credentials
            return self.connection.request(
                ACSRequestMethod.GET,
                request_data=ACSRequestData(
                    url=self.connection.config.base_url
                    + self.connection.config.endpoints.GET_CREDENTIALS,
                    headers=self.connection.base_headers,
                ),
            ).json[1:]

    def count(self) -> int:
        response = self.connection.request(
            ACSRequestMethod.GET,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.GET_CREDENTIALS,
                headers=self.connection.base_headers,
            ),
        ).json
        return response[0]["TotalRowsInAllPages"]

    def update(self, record_id: str, update_data: dict) -> ACSRequestResponse:
        return self.connection.request(
            ACSRequestMethod.PUT,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.EDIT_OBJECT,
                params={
                    "type": "SoftwareHouse.NextGen.Common.SecurityObjects.Credential",
                    "id": record_id,
                },
                data=self.connection.encode_data(
                    {
                        "PropertyNames": list(update_data.keys()),
                        "PropertyValues": list(update_data.values()),
                    }
                ),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def create(self, personnel_id: int, create_data: CredentialCreateData) -> ACSRequestResponse:
        """
        Create a new credential object associated with a personnel object

        create_data properties:
            - `CHUID` is required.
            - `Name` has no effect on the new credential object.
            - `FacilityCode` defaults to 0.
            - If `CardNumber` isn't present in create_data, CHUID will be saved as 0 regardless
            of the `CHUID` value in create_data.
        """
        create_data_dict = create_data.model_dump()
        request_data = {
            "type": "SoftwareHouse.NextGen.Common.SecurityObjects.Personnel",
            "ID": personnel_id,
            "Children": [
                {
                    "Type": "SoftwareHouse.NextGen.Common.SecurityObjects.Credential",
                    "PropertyNames": list(create_data_dict.keys()),
                    "PropertyValues": list(create_data_dict.values()),
                }
            ],
        }
        return self.connection.request(
            ACSRequestMethod.POST,
            request_data=ACSRequestData(
                url=self.config.base_url + self.config.endpoints.PERSIST_TO_CONTAINER,
                data=self.connection.encode_data(request_data),
                headers=self.connection.base_headers | self.connection.header_for_form_data,
            ),
        )

    def delete(self, record_id: int) -> ACSRequestResponse:
        return self.connection.request(
            ACSRequestMethod.DELETE,
            request_data=ACSRequestData(
                url=self.config.base_url
                + self.config.endpoints.DELETE_CREDENTIAL.format(_id=record_id),
                headers=self.connection.base_headers,
            ),
        )
