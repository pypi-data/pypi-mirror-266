import requests
from .schemas import CollectorItem


class Collector:
    def __init__(self, collector_api_key: str, collector_url: str):
        self.collector_api_key = collector_api_key
        self.collector_url = collector_url

    def get_mapped_data(self, ms_ids):
        url = f"{self.collector_url}/v1/products/additional/cmd_list"
        headers = {"Authorization": self.collector_api_key}

        mapped_data = requests.post(url, headers=headers, json={"ms_id": ms_ids}).json()
        return [
            CollectorItem(
                ms_id=item.get("ms_id"),
                product_id=item.get("ozon_product_id"),
                offer_id=item.get("code"),
                price=round(item.get("ozon_max_price") / 100, 2),
                sku=item.get("ozon_sku"),
            )
            for item in mapped_data
        ]
