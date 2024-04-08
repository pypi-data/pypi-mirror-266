

import requests

def get_ip_location():
    try:
        response = requests.get('https://ipinfo.io/')
        if response.status_code == 200:
            data = response.json()
            ip = data.get('ip')
            city = data.get('city')
            region = data.get('region')
            country = data.get('country')
            return {'ip': ip, 'city': city, 'region': region, 'country': country}
        else:
            print(f"Failed to fetch IP location. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching IP location: {e}")
        return None

if __name__ == "__main__":
    ip_location = get_ip_location()
    if ip_location:
        print(f"IP: {ip_location['ip']}, City: {ip_location['city']}, Region: {ip_location['region']}, Country: {ip_location['country']}")
    else:
        print("Failed to retrieve IP location.")
