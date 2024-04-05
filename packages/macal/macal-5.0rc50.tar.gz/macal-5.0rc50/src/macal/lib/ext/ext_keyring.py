# Product:   Macal
# Author:    Marco Caspers
# Date:      23-11-2023
#
#    This library is licensed under the MIT license.
#
#    (c) 2023 Westcon-Comstor
#    (c) 2023 WestconGroup, Inc.
#    (c) 2023 WestconGroup International Limited
#    (c) 2023 WestconGroup EMEA Operations Limited
#    (c) 2023 WestconGroup European Operations Limited
#    (c) 2023 Sama Development Team
#
# Keyring Library external functions

import keyring


def GetPassword(username):
    return keyring.get_password("passwords", username)


def SetPassword(username, password):
    keyring.set_password("passwords", username, password)


def DeletePassword(username):
    keyring.delete_password("passwords", username)


def SetMerakiApiKey(customer, key):
    keyring.set_password("meraki", customer, key)


def GetMerakiApiKey(customer):
    return keyring.get_password("meraki", customer)
