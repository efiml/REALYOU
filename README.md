# RealYou?

## Description

RealYou? is a command-line tool designed to validate phone numbers using the IRBIS API. It allows users to verify phone numbers, retrieve associated information, and display results. The tool supports storing and sanitizing API keys securely.

## Features

- Validate phone numbers in international format
- Retrieve detailed information associated with the phone number
- Securely store and sanitize API keys
- Display information in different formats based on user preference

## Installation

### Windows (PowerShell)

1. **Clone the Repository:**
    ```powershell
    git clone https://github.com/yourusername/realyou.git
    cd realyou
    ```

2. **Set Up a Virtual Environment:**
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate
    ```

3. **Install Dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```

### macOS

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/realyou.git
    cd realyou
    ```

2. **Set Up a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Linux

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/realyou.git
    cd realyou
    ```

2. **Set Up a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Get Your API Key

1. **Register to IRBIS**:
    - Visit [IRBIS Registration Page](https://irbis.espysys.com/auth/register) and create an account.

2. **Choose a Subscription Package**:
    - Select the subscription package that best fits your needs.

3. **Navigate to the Developer Page**:
    - After logging in, go to the [Developer page](https://irbis.espysys.com/developer).

4. **Generate and Copy the API Key**:
    - Generate your API key and copy the value shown. Store it in a safe place.

## Usage

1. **Show Available Commands**:
    ```bash
    python realyou.py -h
    ```

2. **Set API Key**:
    Replace `YOUR_API_KEY` with your actual API key.
    ```bash
    python realyou.py -k "YOUR_API_KEY"
    ```

3. **Show Current API Key**:
    ```bash
    python realyou.py -s
    ```

4. **Validate a Phone Number (Full Information)**:
    Replace `+1234567890` with the phone number you want to validate.
    ```bash
    python realyou.py -p "+1234567890" -i all
    ```

5. **Validate a Phone Number (Score Only)**:
    ```bash
    python realyou.py -p "+1234567890" -i score
    ```

## Dependencies

- Python 3.6 or higher
- `requests`
- `cryptography`
- `tqdm`
- `certifi`
- `cffi`
- `charset-normalizer`
- `colorama`
- `idna`
- `pycparser`
- `urllib3`

Install dependencies using:
```bash
pip install -r requirements.txt