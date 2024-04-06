from .contact_location_local_constants import CONTACT_LOCATION_PYTHON_PACKAGE_CODE_LOGGER_OBJECT
from database_mysql_local.generic_mapping import GenericMapping
from database_mysql_local.point import Point
from location_local.locations_local_crud import LocationsLocal
from location_local.location_local_constants import LocationLocalConstants
from language_remote.lang_code import LangCode
from user_context_remote.user_context import UserContext
from logger_local.LoggerLocal import Logger
from location_local.city import City
from location_local.state import State
from location_local.country import Country
from location_local.county import County
from location_local.region import Region
from location_local.neighborhood import Neighborhood
from groups_local.groups_local import GroupsLocal
import pycountry
import phonenumbers


DEFAULT_SCHEMA_NAME = "contact_location"
DEFAULT_ENTITY_NAME1 = "contact"
DEFAULT_ENTITY_NAME2 = "location"
DEFAULT_ID_COLUMN_NAME = "contact_location_id"
DEFAULT_TABLE_NAME = "contact_location_table"
DEFAULT_VIEW_TABLE_NAME = "contact_location_view"
# TODO Move those to group_category.py in group-local-python-package, we'll generate this file using sql2code
# TODO develop file group_category.py in group-local-python-package
STATE_THEY_LIVE_IN_GROUP_CATEGORY = 501
CITY_THEY_LIVE_IN_GROUP_CATEGORY = 201
DEFAULT_COORDINATE = Point(0, 0)
logger = Logger.create_logger(
    object=CONTACT_LOCATION_PYTHON_PACKAGE_CODE_LOGGER_OBJECT)

user_context = UserContext.login_using_user_identification_and_password()


class ContactLocationLocal(GenericMapping):
    def __init__(self, default_schema_name: str = DEFAULT_SCHEMA_NAME, default_entity_name1: str = DEFAULT_ENTITY_NAME1,
                 default_entity_name2: str = DEFAULT_ENTITY_NAME2, default_id_column_name: str = DEFAULT_ID_COLUMN_NAME,
                 default_table_name: str = DEFAULT_TABLE_NAME, default_view_table_name: str = DEFAULT_VIEW_TABLE_NAME,
                 lang_code: LangCode = None, is_test_data: bool = False) -> None:

        GenericMapping.__init__(
            self, default_schema_name=default_schema_name, default_entity_name1=default_entity_name1,
            default_entity_name2=default_entity_name2, default_id_column_name=default_id_column_name,
            default_table_name=default_table_name, default_view_table_name=default_view_table_name,
            is_test_data=is_test_data)
        self.locations_local = LocationsLocal()
        # TODO: is self.lang_code still needed?
        self.lang_code = lang_code or user_context.get_effective_profile_preferred_lang_code()
        self.is_test_data = is_test_data
        self.profile_id = user_context.get_effective_profile_id()
        self.groups_local = GroupsLocal(is_test_data=is_test_data)

    def insert_contact_and_link_to_location(self, location_information: dict, contact_id: int) -> dict:
        """
        Process city information create city group if not exist and add city to city group
        and linking the contact to the city
        :param location_info: location information: dict
        dict keys:
        - coordinate : Point
        - city : dict
        - state : dict
        - country : dict
        - region : dict
        - neighborhood : dict
        :param contact_id: contact id

        """
        logger.start("process_location", object={
                     'location_information': location_information, 'contact_id': contact_id})
        if not self.__validate_method_arguments(location_information, contact_id):
            logger.warning("location_information or contact_id is None",
                           object={"location_information": location_information, "contact_id": contact_id})
            return None
        city_name = location_information.get('city')
        state_name = location_information.get('state')
        county_name = location_information.get('county')
        country_name = location_information.get('country')
        region_name = location_information.get('region')
        neighborhood_name = location_information.get('neighborhood')
        coordinate = location_information.get('coordinate')

        # insert to database temporary ignore duplicate entry exception
        try:
            country_id, country_data = self.__process_country(
                country_name=country_name, coordinate=coordinate)

            state_id = self.__process_state(
                state_name=state_name)

            city_id = self.__process_city(
                city_name=city_name, state_id=state_id, coordinate=coordinate)

            county_id = self.__process_county(
                county_name=county_name, state_id=state_id, coordinate=coordinate)

            region_id = self.__process_region(
                region_name=region_name, country_id=country_id, coordinate=coordinate)

            neighborhood_id = self.__process_neighborhood(
                neighborhood_name=neighborhood_name, city_id=city_id, coordinate=coordinate)

            location_info = {
                'coordinate': coordinate or DEFAULT_COORDINATE,
                'city_id': city_id,
                'state_id': state_id,
                'county_id': county_id,
                'country_id': country_id,
                'region_id': region_id,
                'neighborhood_id': neighborhood_id,
                'is_test_data': self.is_test_data,
            }

            if country_data is not None:
                location_info['plus_code'] = country_data.get("plus_code")
            else:
                location_info['plus_code'] = LocationLocalConstants.DEFAULT_PLUS_CODE

            location_id = self.locations_local.insert(data=location_info,
                                                      lang_code=self.lang_code,
                                                      is_test_data=self.is_test_data)

            contact_location_id = self.insert_mapping(schema_name='contact_location',
                                                      entity_name1=self.default_entity_name1,
                                                      entity_name2=self.default_entity_name2,
                                                      entity_id1=contact_id,
                                                      entity_id2=location_id,
                                                      data_json={'contact_id': contact_id, 'location_id': location_id})
            location_result = {
                'location_id': location_id,
                'contact_location_id': contact_location_id,
            }
            logger.end(log_message="location successfully processed",
                       object={"location_result": location_result})
            return location_result
        except Exception as e:
            logger.exception("error in process_location" + str(e))
            raise e

    # TODO Should this method be here or in location package?
    def get_country_information(self, country_name: str) -> dict:
        """
        Get country information by country name
        :param country_name: country name
        :return: country information: dict
        example:
        {
            "alpha_2(iso2)": "IL",  :str
            "name": "Israel", :str
            "alpha_3(iso3)": "ISR", :str
            "flag": "🇮🇱", :str
            "numeric": 376, :str
            "plus_code": 972 :int
        }
        """
        try:
            if not self.__validate_method_arguments(country_name):
                logger.warning("country_name is None", object={"country_name": country_name})
                return None
            country = pycountry.countries.get(
                name=country_name).__dict__.get('_fields')
            if country:
                country_alpha_2 = country.get('alpha_2')
                country_code = phonenumbers.COUNTRY_CODE_TO_REGION_CODE.keys()
                for code in country_code:
                    if country_alpha_2 in phonenumbers.COUNTRY_CODE_TO_REGION_CODE[code]:
                        country['plus_code'] = code
                        break
                return country
        except Exception as exception:
            logger.exception("error in get_country_information" + str(exception))
            logger.exception(str(exception))
            raise exception
        return None

    def __process_country(self, country_name: str, coordinate: Point) -> tuple[int, dict]:
        """
        Process country information
        :param country_name: country name
        :param coordinate: coordinate
        :return: country_id: int, country_data: dict
        """
        if not self.__validate_method_arguments(country_name, coordinate):
            logger.warning("country_name or coordinate is None",
                           object={"country_name": country_name, "coordinate": coordinate})
            return None, None
        country_data = {}
        country_id = Country().get_country_id_by_country_name(country_name=country_name)
        if country_id is None:
            country_information = self.get_country_information(
                country_name=country_name)
            country_data.update({
                'coordinate': coordinate,
                'iso': country_information.get("alpha_2"),
                'name': country_name,
                'iso3': country_information.get("alpha_3"),
                'numcode': country_information.get("numeric"),
                'plus_code': country_information.get("plus_code"),
            })
            country_lang_code = LangCode.detect_lang_code(text=country_name)
            if country_lang_code != LangCode.ENGLISH and country_lang_code != LangCode.HEBREW:
                logger.info("country_lang_code is not english or hebrew", object={"country_lang_code": country_lang_code})
                country_lang_code = LangCode.ENGLISH
                logger.info("country_lang_code is set to english", object={"country_lang_code": country_lang_code})
            country_id = Country().insert(country=country_name,
                                          lang_code=country_lang_code,
                                          new_country_data=country_data, coordinate=coordinate)
        return country_id, country_data

    def __process_state(self, state_name: str) -> int:
        """
        Process state information
        :param state_name: state name
        :param country_id: country id
        :param coordinate: coordinate
        :return: state_id: int
        """
        if not self.__validate_method_arguments(state_name):
            logger.warning("state_name is None",
                           object={"state_name": state_name})
            return None
        state_lang_code = LangCode.detect_lang_code(text=state_name)
        if state_lang_code != LangCode.ENGLISH and state_lang_code != LangCode.HEBREW:
            logger.info("state_lang_code is not english or hebrew", object={"state_lang_code": state_lang_code})
            state_lang_code = LangCode.ENGLISH
            logger.info("state_lang_code is set to english", object={"state_lang_code": state_lang_code})
        state_id = State().get_state_id_by_state_name(
            state_name=state_name, lang_code=state_lang_code)
        if state_id is None:
            group_id = self.get_or_create_group_id(
                group_name=state_name, group_category_id=STATE_THEY_LIVE_IN_GROUP_CATEGORY,
                is_test_data=self.is_test_data, profile_id=self.profile_id)
            state_id = State().insert(
                state=state_name,
                lang_code=state_lang_code,
                group_id=group_id)
        return state_id

    def __process_city(self, city_name: str, state_id: int, coordinate: Point) -> int:
        """
        Process city information
        :param city_name: city name
        :param state_id: state_id id
        :param coordinate: coordinate
        :return: city_id: int
        """
        if not self.__validate_method_arguments(city_name):
            logger.warning("city_name is None",
                         object={"city_name": city_name})
            return None
        city_lang_code = LangCode.detect_lang_code(text=city_name)
        if city_lang_code != LangCode.ENGLISH and city_lang_code != LangCode.HEBREW:
            logger.info("city_lang_code is not english or hebrew", object={"city_lang_code": city_lang_code})
            city_lang_code = LangCode.ENGLISH
            logger.info("city_lang_code is set to english", object={"city_lang_code": city_lang_code})
        city_id = City().get_city_id_by_city_name(
            city_name=city_name, lang_code=city_lang_code)
        if city_id is None:
            group_id = self.get_or_create_group_id(
                group_name=city_name, group_category_id=CITY_THEY_LIVE_IN_GROUP_CATEGORY,
                is_test_data=self.is_test_data, profile_id=self.profile_id)
            city_id = City().insert(city=city_name, state_id=state_id,
                                    lang_code=city_lang_code, coordinate=coordinate, group_id=group_id)
        return city_id

    def __process_county(self, county_name: str, state_id: int, coordinate: Point) -> int:
        """
        Process county information
        :param county_name: county name
        :param state_id: state id
        :param coordinate: coordinate
        :return: county_id: int
        """
        if not self.__validate_method_arguments(county_name, state_id):
            logger.warning("county_name or state_id is None",
                           object={"county_name": county_name, "state_id": state_id})
            return None
        county_lang_code = LangCode.detect_lang_code(text=county_name)
        if county_lang_code != LangCode.ENGLISH and county_lang_code != LangCode.HEBREW:
            logger.info("county_lang_code is not english or hebrew", object={"county_lang_code": county_lang_code})
            county_lang_code = LangCode.ENGLISH
            logger.info("county_lang_code is set to english", object={"county_lang_code": county_lang_code})
        county_id = County().get_county_id_by_county_name_state_id(
            county_name=county_name, lang_code=county_lang_code)
        if county_id is None:
            group_id = self.get_or_create_group_id(
                group_name=county_name, group_category_id=None,
                is_test_data=self.is_test_data, profile_id=self.profile_id)
            county_id = County().insert(county=county_name, lang_code=county_lang_code,
                                        coordinate=coordinate, group_id=group_id)
        return county_id

    def __process_region(self, region_name: str, country_id: int, coordinate: Point) -> int:
        """
        Process region information
        :param region_name: region name
        :param country_id: country id
        :param coordinate: coordinate
        :return: region_id: int
        """
        if not self.__validate_method_arguments(region_name, country_id):
            logger.warning("region_name or country_id is None",
                           object={"region_name": region_name, "country_id": country_id})
            return None
        region_lang_code = LangCode.detect_lang_code(text=region_name)
        if region_lang_code != LangCode.ENGLISH and region_lang_code != LangCode.HEBREW:
            logger.info("region_lang_code is not english or hebrew", object={"region_lang_code": region_lang_code})
            region_lang_code = LangCode.ENGLISH
            logger.info("region_lang_code is set to english", object={"region_lang_code": region_lang_code})
        region_id = Region().get_region_id_by_region_name(
            region_name=region_name, lang_code=region_lang_code)
        if region_id is None:
            group_id = self.get_or_create_group_id(
                group_name=region_name, group_category_id=None,
                is_test_data=self.is_test_data, profile_id=self.profile_id)
            region_id = Region().insert(region=region_name,
                                        lang_code=region_lang_code,
                                        coordinate=coordinate,
                                        country_id=country_id,
                                        group_id=group_id)
        return region_id

    def __process_neighborhood(self, neighborhood_name: str, city_id: int, coordinate: Point) -> int:
        """
        Process neighborhood information
        :param neighborhood_name: neighborhood name
        :param city_id: city id
        :param coordinate: coordinate
        :return: neighborhood_id: int
        """
        if not self.__validate_method_arguments(neighborhood_name, city_id):
            logger.warning("neighborhood_name or city_id is None",
                           object={"neighborhood_name": neighborhood_name, "city_id": city_id, "coordinate": coordinate})
            return None
        neighborhood_lang_code = LangCode.detect_lang_code(text=neighborhood_name)
        if neighborhood_lang_code != LangCode.ENGLISH and neighborhood_lang_code != LangCode.HEBREW:
            logger.info("neighborhood_lang_code is not english or hebrew", object={"neighborhood_lang_code": neighborhood_lang_code})
            neighborhood_lang_code = LangCode.ENGLISH
            logger.info("neighborhood_lang_code is set to english", object={"neighborhood_lang_code": neighborhood_lang_code})
        neighborhood_id = Neighborhood().get_neighborhood_id_by_neighborhood_name(
            neighborhood_name=neighborhood_name, lang_code=neighborhood_lang_code)
        if neighborhood_id is None:
            group_id = self.get_or_create_group_id(
                group_name=neighborhood_name, group_category_id=None,
                is_test_data=self.is_test_data, profile_id=self.profile_id)
            neighborhood_id = Neighborhood().insert(neighborhood=neighborhood_name,
                                                    lang_code=neighborhood_lang_code,
                                                    coordinate=coordinate,
                                                    city_id=city_id,
                                                    group_id=group_id)
        return neighborhood_id

    # Refactored repeated database processing code into a helper function
    def get_or_create_group_id(self, group_name: str, group_category_id: int, is_test_data: bool, profile_id: int) -> int:
        logger.start("get_or_create_group_id", object={
                     'group_name': group_name, 'group_category_id': group_category_id,
                     'is_test_data': is_test_data, 'profile_id': profile_id})

        if not self.__validate_method_arguments(group_name, profile_id):
            logger.warning("group_name, is_test_data or profile_id is None",
                           object={"group_name": group_name, "profile_id": profile_id})
            return None

        # TODO Can we use a function in group-local repo? -We should take into account the end_timestamp, visibility, is_approved if the UserContext.effective user is not the owner
        group_id = self.groups_local.select_one_value_by_where(
            schema_name='group', view_table_name='group_ml_view',
            select_clause_value='group_id',
            where='title = %s', params=(group_name,))
        if group_id is None:
            group_json = {
                'title': group_name,
                'name': group_name,
                'profile_id': profile_id,
            }
            data_json_compare = {
                'name': group_name,
            }
            if group_category_id:
                group_json['group_category_id'] = group_category_id
            group_lang_code = LangCode.detect_lang_code(text=group_name)
            if group_lang_code != LangCode.ENGLISH and group_lang_code != LangCode.HEBREW:
                group_lang_code = LangCode.ENGLISH
            group_id, group_ml_id = self.groups_local.upsert_group(
                group_dict=group_json,
                data_json_compare=data_json_compare,
                lang_code=group_lang_code)
        return group_id

    def __validate_method_arguments(*args):
        """
        Validate method arguments to ensure they are not None or ''
        :param args: Variable number of arguments to validate
        :return: True if all arguments are not None or '', False otherwise
        """
        for arg in args:
            if arg is None or arg == '':
                return False
        return True
