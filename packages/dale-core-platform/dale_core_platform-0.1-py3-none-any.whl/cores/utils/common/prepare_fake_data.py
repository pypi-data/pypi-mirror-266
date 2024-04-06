from faker import Faker
from faker.providers.phone_number import Provider

import random
from datetime import datetime


class VietnamProvider(Provider):
    """
    A Provider for phone number.
    """

    def vn_phone_number(self):
        return f'+84{self.msisdn()[3:]}'

    def vn_name(self, gender: str = 'Male'):
        return True
    #     _gender_mapping = dict(
    #         MALE=1,
    #         FEMALE=2
    #     )
    # from vn_fullname_generator import generator
    #     return generator.generate(gender=_gender_mapping[gender.upper()])


class DataGeneratorUtil:
    """
        This function will help to generate fake data with *look like* data.
        To use this funct
        DataGenratorUtil(country).name_generator()
    """

    def __init__(self, country: str = None):
        """
        :param country: List(str)
        :return: faker provider
        """
        __countries = ['en_US']
        if country:
            __countries.append(country)
        self.fake = Faker(__countries)
        self.fake.add_provider(VietnamProvider)

    def full_name_generator(self, is_vn: bool = False) -> str:
        if not is_vn:
            return self.fake.name()
        else:
            return self.fake.vn_name()

    def detail_name_generator(self) -> dict:
        name = self.fake.name()
        return {
            'first_name': name[0],
            'last_name': name[1]
        }

    def date_generator(self, start_date: str = None, end_date: str = None) -> datetime.date:
        """
        :param start_date: str format ('%Y-%m-%d')
        :param end_date: str format ('%Y-%m-%d')
        :return: datetime('%Y-%m-%d')
        """
        if not (start_date and end_date):
            return self.fake.date_between(end_date='today')
        else:
            return self.fake.date_between(start_date=start_date, end_date=end_date)

    def phone_generator(self) -> str:
        return self.fake.vn_phone_number()

    def address_generator(self) -> str:
        return self.fake.address()

    def birth_date_generator(self, min_age: int = 10, max_age: int = 90) -> datetime.date:
        """_summary_

        Args:
            min_age (int, optional): _description_. Defaults to 10.
            max_age (int, optional): _description_. Defaults to 90.

        Returns:
            datetime.date: datetime('%Y-%m-%d')
        """
        if not (min_age and max_age):
            return self.fake.date_of_birth()
        else:
            if max_age < min_age:
                return self.fake.date_of_birth(minimum_age=max_age, maximum_age=min_age)
            else:
                return self.fake.date_of_birth(minimum_age=min_age, maximum_age=max_age)

    @staticmethod
    def random_number_generator(length: int = 2) -> int:
        return random.randrange(10 ** (length - 1), (10 ** length) - 1)

    @staticmethod
    def random_list_generator(length=5) -> list:
        return [random.randint(1, 30) for _ in range(length)]
