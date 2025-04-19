import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

class HotelCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_hotel_data(self, url):
        try:
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print(response.text)
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            hotels = []
            hotel_elements = soup.find_all('div', {'data-testid': 'property-card'})
            
            for hotel in hotel_elements:
                try:
                    hotel_data = {
                        'name': hotel.find('div', {'data-testid': 'title'}).text.strip(),
                        'price': hotel.find('span', {'data-testid': 'price-and-discounted-price'}).text.strip(),
                        'rating': hotel.find('div', {'data-testid': 'review-score'}).text.strip() if hotel.find('div', {'data-testid': 'review-score'}) else 'N/A',
                        'location': hotel.find('span', {'data-testid': 'address'}).text.strip() if hotel.find('span', {'data-testid': 'address'}) else 'N/A',
                    }
                    hotels.append(hotel_data)
                except Exception as e:
                    print(f"Error parsing hotel data: {e}")
                    continue
            
            return hotels
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def save_to_csv(self, hotels, filename='hotels.csv'):
        if hotels:
            df = pd.DataFrame(hotels)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data saved to {filename}")
        else:
            print("No data to save")

def main():
    url = "https://www.booking.com/searchresults.vi.html?label=hanoi-oexp440WUV_fOStCONOehgS632846194947%3Apl%3Ata%3Ap1%3Ap2260%2C000%3Aac%3Aap%3Aneg%3Afi%3Atikwd-26192725300%3Alp9198864%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YXL5GV3cgz10NyjSyBn12N8&gclid=CjwKCAjwk43ABhBIEiwAvvMEB3kwcFPHMAl3_BPERsJTk7KLbzZcO3OqJItK8JcSCP5MG75qjgjLsxoCCLkQAvD_BwE&aid=336510&city=-3714993"
    
    crawler = HotelCrawler()
    hotels = crawler.get_hotel_data(url)
    crawler.save_to_csv(hotels)

if __name__ == "__main__":
    main() 