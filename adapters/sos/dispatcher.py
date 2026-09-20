"""
CareBridge — SOS & Emergency Contact Dispatcher
================================================
One-tap emergency actions:
  1. Call 108 (ambulance tel: link)
  2. WhatsApp SOS with location link (wa.me)
  3. SMS fallback for WhatsApp (via Twilio or native sms: protocol)
  4. Quick emergency contacts (Police, Fire, Women helpline)

TRD §5 compliance:
  - Twilio SMS as WhatsApp fallback
  - SOS sends urgency level + coordinates only (no symptoms/diagnosis)
  - Privacy: no persistent data, session context only
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote_plus

try:
    from twilio.rest import Client as TwilioClient
    _TWILIO_AVAILABLE = True
except ImportError:
    _TWILIO_AVAILABLE = False


AMBULANCE_NUMBER = "108"
POLICE_NUMBER = "100"
FIRE_NUMBER = "101"
DISASTER_MANAGEMENT = "1078"
WOMEN_HELPLINE = "1091"
CHILD_HELPLINE = "1098"

EMERGENCY_CONTACTS = {
    "ambulance": {"number": AMBULANCE_NUMBER, "label_en": "Ambulance", "label_hi": "एम्बुलेंस"},
    "police":    {"number": POLICE_NUMBER,    "label_en": "Police",    "label_hi": "पुलिस"},
    "fire":      {"number": FIRE_NUMBER,      "label_en": "Fire",      "label_hi": "अग्निशमन"},
}


def build_sos_message(
    urgency_level: str,
    user_lat: Optional[float],
    user_lng: Optional[float],
    lang: str = "en",
    facility_name: Optional[str] = None,
) -> str:
    """
    Builds a privacy-safe SOS text message.
    Sends urgency level + coordinates + Google Maps link only.
    """
    maps_link = ""
    if user_lat and user_lng:
        maps_link = f"https://maps.google.com/?q={user_lat},{user_lng}"

    if lang == "hi":
        level_label = {"RED": "🔴 आपातकाल", "YELLOW": "🟡 उच्च प्राथमिकता", "GREEN": "🟢 सामान्य"}.get(urgency_level, "")
        msg = f"CareBridge SOS — {level_label}\n"
        if facility_name:
            msg += f"निकटतम सुविधा: {facility_name}\n"
        if maps_link:
            msg += f"मेरी लोकेशन: {maps_link}\n"
        msg += "कृपया तुरंत मदद करें। 108 पर कॉल करें।"
    else:
        level_label = {"RED": "🔴 EMERGENCY", "YELLOW": "🟡 HIGH PRIORITY", "GREEN": "🟢 NON-URGENT"}.get(urgency_level, "")
        msg = f"CareBridge SOS — {level_label}\n"
        if facility_name:
            msg += f"Nearest facility: {facility_name}\n"
        if maps_link:
            msg += f"My location: {maps_link}\n"
        msg += "Please help immediately. Call 108."

    return msg


def get_whatsapp_sos_url(
    contact_number: str,
    urgency_level: str,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    facility_name: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Returns a WhatsApp deep-link that pre-fills an SOS message."""
    msg = build_sos_message(urgency_level, user_lat, user_lng, lang, facility_name)
    clean_num = "".join(c for c in contact_number if c.isdigit())
    return f"https://wa.me/{clean_num}?text={quote_plus(msg)}"


def get_native_sms_url(
    contact_number: str,
    urgency_level: str,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    facility_name: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Returns a native sms: protocol link for mobile devices."""
    msg = build_sos_message(urgency_level, user_lat, user_lng, lang, facility_name)
    clean_num = "".join(c for c in contact_number if c.isdigit())
    return f"sms:{clean_num}?body={quote_plus(msg)}"


def get_tel_url(phone_number: str) -> str:
    """Returns tel: URL for click-to-call buttons."""
    clean = "".join(c for c in phone_number if c.isdigit() or c == "+")
    return f"tel:{clean}"


@dataclass
class SMSResult:
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None
    fallback_used: bool = False


def send_sms_via_twilio(
    to_number: str,
    message: str,
    account_sid: Optional[str] = None,
    auth_token: Optional[str] = None,
    from_number: Optional[str] = None,
) -> SMSResult:
    """Sends an emergency SMS via Twilio with graceful failure."""
    sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
    token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
    sender = from_number or os.getenv("TWILIO_PHONE_NUMBER")

    if not _TWILIO_AVAILABLE:
        return SMSResult(success=False, error="twilio library not installed")
    if not (sid and token and sender):
        return SMSResult(success=False, error="Twilio credentials not configured")

    try:
        client = TwilioClient(sid, token)
        msg = client.messages.create(body=message, from_=sender, to=to_number)
        return SMSResult(success=True, message_sid=msg.sid)
    except Exception as exc:
        return SMSResult(success=False, error=str(exc))


@dataclass
class SOSActions:
    """All one-tap actions for a given urgency context."""
    call_108_url: str
    whatsapp_sos_url: Optional[str]
    sos_message: str
    urgency_level: str
    emergency_contacts: dict


def build_sos_actions(
    urgency_level: str,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    emergency_contact_number: Optional[str] = None,
    facility_name: Optional[str] = None,
    lang: str = "en",
) -> SOSActions:
    """Assembles all SOS action URLs for UI rendering."""
    sos_msg = build_sos_message(urgency_level, user_lat, user_lng, lang, facility_name)
    wa_url = None
    if emergency_contact_number:
        wa_url = get_whatsapp_sos_url(
            emergency_contact_number,
            urgency_level,
            user_lat,
            user_lng,
            facility_name,
            lang,
        )

    return SOSActions(
        call_108_url=f"tel:{AMBULANCE_NUMBER}",
        whatsapp_sos_url=wa_url,
        sos_message=sos_msg,
        urgency_level=urgency_level,
        emergency_contacts=EMERGENCY_CONTACTS,
    )

