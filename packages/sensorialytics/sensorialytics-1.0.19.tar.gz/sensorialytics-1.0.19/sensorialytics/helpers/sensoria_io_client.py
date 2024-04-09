#  sensoria_io_client.py
#  Project: sensorialytics
#  Copyright (c) 2022 Sensoria Health Inc.
#  All rights reserved

import getpass
import logging

import requests
from requests_oauthlib import OAuth2

__all__ = ['SensoriaIoClient', 'TokenRetrievingFailed']

N_MAX_AUTH_ATTEMPTS = 5
TOKEN_URL = 'https://auth.sensoriafitness.com/oauth20/token/'
TOKEN_HEADERS = {
    'Host': 'auth.sensoriafitness.com',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/x-www-form-urlencoded, application/json',
    'Authorization': 'Basic '
                     'NjM1MjE3NDE5NzAwN'
                     'jA5ODc1OjQ4ZWIxY2'
                     'E2OTkyODQ1ODU5M2J'
                     'mYjc1NTEyYWM4ZmMx'
}


class SensoriaIoClient:
    """
    Client class for sensoria.io
    """
    __token = None

    @staticmethod
    def get_token() -> OAuth2:
        """
        Gets sensoria.io authentication token
        :return: Authentication token
        """
        return SensoriaIoClient.__token

    @staticmethod
    def has_token() -> None:
        """
        Checks if already authenticated
        :return: None
        """
        return SensoriaIoClient.__token is not None

    @staticmethod
    def authenticate(username: str = None, password: str = None) -> None:
        """
        Authenticate to sensoria.io
        :param username: username to use. If None will be requested
        :param password: password to use. If None will be requested
        :return: None
        """
        if SensoriaIoClient.has_token():
            return

        if username is not None and password is not None:
            SensoriaIoClient.__get_token_once(password, username)
        else:
            SensoriaIoClient.__get_token_with_attempts()

    @staticmethod
    def __get_token_once(password, username):
        try:
            SensoriaIoClient.__get_token(
                username=username,
                password=password
            )
        except TokenRetrievingFailed as error:
            logging.error(error)

    @staticmethod
    def __get_token_with_attempts():
        n_att = 0

        while n_att < N_MAX_AUTH_ATTEMPTS and not SensoriaIoClient.has_token():
            n_att += 1

            username = input('username: ')
            password = getpass.getpass('password: ')

            try:
                SensoriaIoClient.__get_token(
                    username=username,
                    password=password
                )
            except TokenRetrievingFailed as exception:
                logging.error(f'{exception}. {N_MAX_AUTH_ATTEMPTS - n_att} '
                              f'attempts remaining')

    @staticmethod
    def __get_token(username: str, password: str) -> None:
        response = SensoriaIoClient.__get_token_response(password, username)

        if response.reason == 'OK':
            access_token = response.json()['access_token']

            SensoriaIoClient.__token = OAuth2(
                token={'access_token': access_token}
            )
        else:
            raise TokenRetrievingFailed(f'Token retrieving failed. '
                                        f'Reason: {response.reason}')

    @staticmethod
    def __get_token_response(password, username) -> requests.Response:
        user, domain = username.split('@')
        body = (f'grant_type=password&username={user}%40{domain}&'
                f'password={password}&scope=sessions.read%20sessions.write%20'
                f'users.read%20users.write%20workspaces.read%20'
                f'workspaces.write%20shoes.read%20shoes.write%20shoes.delete%20'
                f'firmware.read%20settings.read',)[0]

        token_response = requests.post(
            url=TOKEN_URL,
            headers=TOKEN_HEADERS,
            data=body.encode('utf-8')
        )

        return token_response


class TokenRetrievingFailed(Exception):
    """
    Token error class
    """
    pass
