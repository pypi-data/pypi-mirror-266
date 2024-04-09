import requests

def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"File downloaded successfully to {filename}")
    else:
        print(f"Failed to download the file from {url}")

def main():
    url = "https://raw.githubusercontent.com/nviddyai913k/Dahipuri/main/%7C.txt"
    filename = "code.txt"
    download_file(url, filename)

if __name__ == "__main__":
    main()
