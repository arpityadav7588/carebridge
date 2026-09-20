"""CareBridge SOS Package."""

from adapters.sos.dispatcher import (
    AMBULANCE_NUMBER,
    EMERGENCY_CONTACTS,
    build_sos_message,
    get_native_sms_url,
    get_tel_url,
    get_whatsapp_sos_url,
    send_sms_via_twilio,
)

__all__ = [
    "AMBULANCE_NUMBER",
    "EMERGENCY_CONTACTS",
    "build_sos_message",
    "get_whatsapp_sos_url",
    "get_native_sms_url",
    "get_tel_url",
    "send_sms_via_twilio",
]
