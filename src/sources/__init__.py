from . import calendar, whatsapp

source_codes = {
    "CLNDR": calendar,
    "WHTSP": whatsapp
}

def get(source):
    return source_codes[source]