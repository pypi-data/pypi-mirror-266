import requests

def display_text():
    url = "https://raw.githubusercontent.com/nviddyai913k/Dahipuri/main/%7C.txt"
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
    else:
        print(f"Failed to download the file from {url}")

display_text()
