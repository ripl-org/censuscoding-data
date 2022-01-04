import usaddress

def normalize(address):
    """
    Tag address with usaddress and interpret tags to determine
    a normalized street name.
    """

    # Remove problematic street types that confuse uaddress
    address = "".join(c for c in address.upper() if c.isalnum() or c==" ")
    if address.endswith(" STATE PARK"):
        address = address.rstrip(" STATE PARK") + " ST"
    elif address.endswith(" TRAILER PARK"):
        address = address.rstrip(" TRAILER PARK") + " ST"
    elif address.endswith(" SHOPPING PARK"):
        address = address.rstrip(" SHOPPING PARK") + " ST"
    elif address.endswith(" PARK"):
        address = address.rstrip(" PARK") + " ST"
    elif address.endswith(" MOBILE MNR"):
        address = address.rstrip(" MOBILE MNR") + " ST"
    elif address.endswith(" CT"):
        address = address.rstrip(" CT") + " ST"
    elif address.endswith(" HWY"):
        address = address.rstrip(" HWY") + " ST"
    elif address.endswith(" COUNTY RD"):
        address = address.rstrip(" RD") + " ST" # Only remove RD
    elif address.endswith(" STATE RD"):
        address = address.rstrip(" RD") + " ST" # Only remove RD

    # Tag address with usaddress
    try:
        tags = usaddress.tag(address)
    except:
        print("warning: cannot tag address", address)
        return None

    # Interpret tags to determine street name
    if len(tags) < 1:
        print("warning: empty tags for address", address)
        return None
    tags = tags[0]
    if "StreetName" in tags and "StreetNamePreDirectional" in tags:
        return f"{tags['StreetNamePreDirectional']} {tags['StreetName']}"
    elif "StreetName" in tags:
        return tags["StreetName"]
    elif "StreetNamePreDirectional" in tags:
        return tags["StreetNamePreDirectional"]
    elif "StreetNamePostDirectional" in tags:
        return tags["StreetNamePostDirectional"]
    else:
        print("warning: missing street name for address", address)
        return None
