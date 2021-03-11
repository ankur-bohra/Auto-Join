from . import google_calendar#, whatsapp

source_codes = {
    "CLNDR": google_calendar,
    # "WHTSP": whatsapp
}

def get_source(source):
    return source_codes[source]