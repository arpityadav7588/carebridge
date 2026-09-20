"""
CareBridge — SOS Actions Re-export
==================================
ponytail: thin alias to adapters.sos.dispatcher.
"""

from adapters.sos.dispatcher import (
    AMBULANCE_NUMBER,
    CHILD_HELPLINE,
    DISASTER_MANAGEMENT,
    EMERGENCY_CONTACTS,
    FIRE_NUMBER,
    POLICE_NUMBER,
    WOMEN_HELPLINE,
    SMSResult,
    SOSActions,
    build_sos_actions,
    build_sos_message,
    get_native_sms_url,
    get_tel_url,
    get_whatsapp_sos_url,
    send_sms_via_twilio,
)

# Backwards compatibility alias
send_sos_sms = send_sms_via_twilio

__all__ = [
    "AMBULANCE_NUMBER",
    "POLICE_NUMBER",
    "FIRE_NUMBER",
    "DISASTER_MANAGEMENT",
    "WOMEN_HELPLINE",
    "CHILD_HELPLINE",
    "EMERGENCY_CONTACTS",
    "SMSResult",
    "SOSActions",
    "build_sos_message",
    "build_sos_actions",
    "get_whatsapp_sos_url",
    "get_native_sms_url",
    "get_tel_url",
    "send_sms_via_twilio",
    "send_sos_sms",
]
