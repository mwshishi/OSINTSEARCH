# phone/phonechecker.py
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

def check_phone_number(phone):
    try:
        default_region = "ID"
        parsed_number = phonenumbers.parse(phone, default_region)

        if not phonenumbers.is_possible_number(parsed_number) or not phonenumbers.is_valid_number(parsed_number):
            return {"error": "The phone number is invalid or not possible."}

        info = {
            "location": geocoder.description_for_number(parsed_number, "id"),
            "region_code": phonenumbers.region_code_for_number(parsed_number),
            "timezone": ', '.join(timezone.time_zones_for_number(parsed_number)),
            "operator": carrier.name_for_number(parsed_number, "en"),
            "valid": phonenumbers.is_valid_number(parsed_number),
            "possible": phonenumbers.is_possible_number(parsed_number),
            "formatted_international": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "formatted_mobile": phonenumbers.format_number_for_mobile_dialing(parsed_number, default_region, with_formatting=True),
            "original_number": parsed_number.national_number,
            "e164": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
            "country_code": parsed_number.country_code,
            "local_number": parsed_number.national_number,
        }

        # Optional: add number type
        from phonenumbers import PhoneNumberType
        number_type = phonenumbers.number_type(parsed_number)
        if number_type == PhoneNumberType.MOBILE:
            info["type"] = "Mobile"
        elif number_type == PhoneNumberType.FIXED_LINE:
            info["type"] = "Fixed line"
        else:
            info["type"] = "Other"

        return info

    except Exception as e:
        return {"error": f"Parsing failed: {e}"}
