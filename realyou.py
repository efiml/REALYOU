import requests
import argparse
import time
import os
import re
from datetime import datetime
from cryptography.fernet import Fernet
from tqdm import tqdm

API_KEY_FILE = "apikey.txt"
KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    return open(KEY_FILE, 'rb').read()

def encrypt_message(message):
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message

def decrypt_message(encrypted_message):
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_intro():
    print("""
    ************************************
    *                                  *
    *         Real You?                *
    *                                  *
    ************************************
    """)
    print("A tool to validate phone numbers using the IRBIS API.")

def get_stored_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'rb') as file:
            encrypted_key = file.read()
            try:
                return decrypt_message(encrypted_key)
            except Exception as e:
                print(f"Error decrypting API key: {e}")
                return None
    return None

def store_api_key(api_key):
    encrypted_key = encrypt_message(api_key)
    with open(API_KEY_FILE, 'wb') as file:
        file.write(encrypted_key)
    print("API key encrypted and stored successfully.")

def validate_api_key(api_key):
    sanitized_key = sanitize_api_key(api_key)
    print(f"Validating API key: {sanitized_key}")
    response = requests.get(
        f"https://irbis.espysys.com/api/request-monitor/credit-stat?key={api_key}",
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        print("API key validated successfully.")
        return response.json()
    else:
        print(f"Error validating API key: {response.status_code} {response.text}")
        return None

def validate_phone_number(phone_number):
    if re.match(r'^\+\d+$', phone_number):
        return True
    return False

def sanitize_api_key(api_key):
    return f"${'*' * (len(api_key) - 5)}{api_key[-5:]}"

def display_account_info(account_info):
    balance = account_info["balance"]
    currency = account_info["currency"]
    credits = account_info["credits"]
    expiration_date = datetime.strptime(account_info["expiratioDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
    status = account_info["status"]

    print(f"Balance: {balance} {currency}")
    print(f"Credits: {credits}")
    print(f"Expiration Date: {expiration_date}")
    print(f"Status: {status}")

def display_command_options():
    print("\nAvailable Commands:")
    print("  -h            Help")
    print("  -k APIKEY     Replace API key")
    print("  -s            Show current API key")
    print("  -p PHONE      Phone to search")
    print("  -i {score,all} Type of information to retrieve")
    print("  -d            Debug mode\n")

def trigger_phone_lookup(api_key, phone_number):
    response = requests.post(
        "https://irbis.espysys.com/api/developer/real_phone",
        headers={"Content-Type": "application/json"},
        json={"key": api_key, "value": phone_number}
    )
    response_data = response.json()

    # Check for the specific error message in the response
    if response_data.get("statusCode") == 404 and "You have to buy package for this services" in response_data.get("message", ""):
        print("""
    ***********************************************
    *                                             *
    *  You have to buy package for this services  *
    *                                             *
    ***********************************************
    """)
        return None

    return response_data.get("id")

def get_phone_lookup_result(api_key, lookup_id):
    while True:
        for _ in tqdm(range(10), desc="Checking status", unit="s"):
            time.sleep(1)
        
        response = requests.get(
            f"https://irbis.espysys.com/api/request-monitor/api-usage/{lookup_id}?key={api_key}",
            headers={"Content-Type": "application/json"}
        )
        response_data = response.json()
        
        if response_data["status"] == "finished":
            # Adding a 20-second delay with animation
            for _ in tqdm(range(20), desc="Finalizing", unit="s"):
                time.sleep(1)
            # Retrieve the final data after the timeout
            final_response = requests.get(
                f"https://irbis.espysys.com/api/request-monitor/api-usage/{lookup_id}?key={api_key}",
                headers={"Content-Type": "application/json"}
            )
            return final_response.json()

def display_results(data, info_type, debug_mode):
    if debug_mode:
        print(f"Data received for processing: {data}")
    
    if info_type == "score":
        verifier_data = next((item for item in data if isinstance(item, dict) and 'verifier' in item), None)
        if verifier_data:
            verifier = verifier_data['verifier']
            print(f"Real Person: {verifier.get('finalClassification')}")
            print(f"Score: {verifier.get('score')}")
        else:
            print("No verifier data found.")
    elif info_type == "all":
        names = []
        emails = []
        linkedin_profiles = []
        birthdays = []
        facebook_ids = []
        verifier = None
        
        for source in data:
            if isinstance(source, dict):
                for key, value in source.items():
                    if isinstance(value, dict):
                        if 'name' in value:
                            names.append(value['name'])
                        if 'emails' in value:
                            for email in value['emails']:
                                emails.append(email['email'])
                        if 'linkedinPubProfileUrl' in value:
                            linkedin_profiles.append(value['linkedinPubProfileUrl']['id'])
                        if 'birthday' in value and isinstance(value['birthday'], dict):
                            birthday = value['birthday']
                            formatted_birthday = f"{birthday['formattedDay']}/{birthday['formattedMonth']}/{birthday['formattedYear']}"
                            birthdays.append(formatted_birthday)
                        if 'facebookID' in value and value['facebookID']['sure']:
                            facebook_ids.append(value['facebookID']['id'])
                        if key == 'verifier':
                            verifier = value
        
        print(f"Names: {', '.join(names)}")
        print(f"Emails: {', '.join(emails)}")
        print(f"LinkedIn Profiles: {', '.join(linkedin_profiles)}")
        print(f"Birthdays: {', '.join(birthdays)}")
        print(f"Facebook IDs: {', '.join(facebook_ids)}")
        
        if verifier:
            print(f"Real Person: {verifier.get('finalClassification')}")
            print(f"Score: {verifier.get('score')}")
        else:
            print("No verifier data found.")

def main():
    clear_screen()
    show_intro()

    parser = argparse.ArgumentParser(description="RealYou? Phone Validation Tool")
    parser.add_argument("-k", "--apikey", type=str, help="Your IRBIS API Key")
    parser.add_argument("-p", "--phone", type=str, help="Phone number to validate")
    parser.add_argument("-i", "--info", choices=["score", "all"], help="Type of information to retrieve")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-s", "--showkey", action="store_true", help="Show current API key")

    args = parser.parse_args()

    if args.apikey:
        api_key = args.apikey
        account_info = validate_api_key(api_key)
        if account_info:
            store_api_key(api_key)
            clear_screen()
            print("API key replaced and validated successfully!\n")
            display_account_info(account_info)
        else:
            print("Invalid API key. Please try again.")
            return
    elif args.showkey:
        api_key = get_stored_api_key()
        if api_key:
            print(f"Current API key: {sanitize_api_key(api_key)}")
        else:
            print("No API key found. Please set an API key using the -k option.")
        return
    else:
        api_key = get_stored_api_key()
        if not api_key:
            api_key = input("Enter your API key: ")
            account_info = validate_api_key(api_key)
            if account_info:
                store_api_key(api_key)
                clear_screen()
                print("API key validated successfully!\n")
                display_account_info(account_info)
            else:
                print("Invalid API key. Please try again.")
                return
        else:
            account_info = validate_api_key(api_key)
            if not account_info:
                print("Stored API key is invalid. Please run the script with a new API key using the -k option.")
                return
            display_account_info(account_info)
            display_command_options()

    if args.phone and args.info:
        if not validate_phone_number(args.phone):
            print("Invalid phone number format. Please use the international format without spaces, e.g., +1234567890.")
            return
        
        lookup_id = trigger_phone_lookup(api_key, args.phone)
        if lookup_id:
            result_data = get_phone_lookup_result(api_key, lookup_id)
            display_results(result_data["data"], args.info, args.debug)
        else:
            print("Error triggering phone lookup.")
    else:
        print("\nNo phone search command provided. Use -h for help.")

if __name__ == "__main__":
    main()
