import torch 
from openai import OpenAI
import pandas as pd

class VectorDatabase:
    def __init__(self):
        self.index = None
        self.dimension = 768
        self.metric = "cosine"
        self.index_name = "hotel-recommendations"
        self.openai.api_key = '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'
        self.name_model = "text-embedding-3-small"
        self.client = OpenAI(
        api_key=self.openai.api_key,
        )
    def process_room_type(room_type):
        if isinstance(room_type, list):  # Nếu 'room_type' là list
            return ', '.join(room_type)
        return room_type
# Hàm lấy embedding từ OpenAI
    def get_openai_embeddings(text):
        response = self.client.embeddings.create(
        input="input",
        model=self.name_model
        )   
        return response.data[0].embedding
    def prepare_hotel_embedding(self, data = '../data/hotel_processed.csv'):
        self.df = self.prepare_hotel_data(data)

        client = OpenAI(
        # This is the default and can be omitted
        api_key=self.openai.api_key,
        )
    def prepare_hotel_data(self, data = '../data/hotel_processed.csv'):
        self.df = pd.read_csv(data)
        self.df['price'] = self.df['price'].replace({'VND': '', ',': '', '\xa0': '', '\.': ''}, regex=True)
        self.df['price'] = self.df['price'].astype(float)
        self.df['rating'].fillna(self.df['rating'].mean(), inplace=True)
        self.df['index'] = ['hotel_' + str(i).zfill(5) for i in range(1, len(self.df) + 1)]
        self.df['rating'] = self.df['rating'].astype(float)
        return self.df
def main():
    pass

if __name__ == "__main__":
    main()