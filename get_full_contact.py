#!/usr/bin/env python3

import argparse
from bonsai import LDAPClient
import xml.etree.cElementTree as ET

try:

    #handle arguments
    parser = argparse.ArgumentParser();
    parser.add_argument("-p", "--phone_number", help="type here the phone number part",
    type=str, required = True)
    parser.add_argument("-o", "--outfile", help="type here the output file name",
    type=str, required=True)
    parser.add_argument("-ou", "--organizational_unit",
    help="you can improve accuracy if you give me the organizational unit(optional parameter)",
    type=str, required=False)
    args = parser.parse_args();

    #handle exceptions
    file = args.outfile
    if file.lower().endswith('.xml') == False:
        raise Exception("output file's extension must be xml")
    try:
        int(args.phone_number)
    except ValueError:
        raise Exception("must be only numbers in phone number")

    #search
    client = LDAPClient("ldap://localhost")
    client.set_credentials("SIMPLE",("cn=Manager,dc=irf,dc=local", "LaborImage"))
    conn = client.connect()
    result = list()
    sorted = list()
    dn = "dc=irf,dc=local"
    if args.organizational_unit:
        have_this = conn.search(args.organizational_unit, 2, "(&(objectClass=organizationalUnit))");
        if not have_this:
            raise Exception("the specified DN does not exist not an organizational unit")
        else:
            dn = args.organizational_unit

    result = conn.search(dn , 2,
    "(&(objectClass=person)(telephoneNumber=*" + args.phone_number + "*))",
    attrlist=['givenName', 'sn', 'telephoneNumber']);

    #sort results and format
    for res in result:
        printOu=(res.dn.__getitem__(1)).split("=")
        if printOu[0] != "ou":
            printOu[1] = ""
        sorted.append(res['givenName'][0] + ":" + res['sn'][0] + ":" + res['telephoneNumber'][0] + ":" +  printOu[1])
    sorted.sort()

    #create XML file
    users = ET.Element("users")
    for members in sorted:
        parts = members.split(":")
        #print(parts)
        user = ET.SubElement(users,"user", organizational_unit=parts[3])
        ET.SubElement(user,"givenName").text = parts[0]
        ET.SubElement(user,"surname").text = parts[1]
        ET.SubElement(user,"telephoneNumber").text = parts[2]

    tree = ET.ElementTree(users)
    tree.write(args.outfile,encoding="UTF-8",xml_declaration=True)

except Exception as error:
    print('ERROR:' + str(error))

