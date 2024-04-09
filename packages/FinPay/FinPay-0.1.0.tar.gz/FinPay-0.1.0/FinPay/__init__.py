__version__ = '0.1.0'

import hashlib
import random
import string

import requests


def randoms(count: int):
    out = ""
    for i in range(count - 1):
        out = out + random.choice(string.ascii_letters + string.digits)
    return out


class FinPayInvoice:
    api_object = None
    url: str = None
    finpay_id: int = None
    pay_id: str = None
    success: bool = None
    signature: str = None

    def __init__(self, api, invoice_id: str, description: str, amount: int, method: str, country: str, currency: str, signature: str):
        self.api_object = api
        invoice_object = requests.post(api.payment_url,
                                  data={"shop_id": api.merchant_id, "invoice_id": invoice_id, "description": description,
                                        "amount": amount * 100, "method": method, "country": country, "currency": currency,
                                        "signature": signature}).json()
        self.url = invoice_object['url']
        self.finpay_id = invoice_object['id']
        self.pay_id = invoice_object['pay_id']
        self.success = invoice_object['success']
        self.signature = signature

    def check_status(self) -> bool:
        request_url = self.api_object.payment_url + '/' + str(self.finpay_id) + f"?signature={self.signature}"
        data = requests.get(request_url).json()

        return data["status"] == "success"

    def cancel_invoice(self) -> bool:
        request_url = self.api_object.payment_url
        data = requests.delete(request_url, data={"id": self.finpay_id, "signature": self.signature}).json()

        return bool(data["success"])


class FinPayAPI:
    merchant_id: int = None
    key1: str = None
    key2: str = None
    payment_url: str = None

    def __init__(self, merchant_id: int, key1: str, key2: str, payment_url: str = "https://api.finpay.llc/payments"):
        self.merchant_id = merchant_id
        self.key1 = key1
        self.key2 = key2
        self.payment_url = payment_url

    def gen_signature(self, invoice_id: str, amount: int, method_id: str) -> str:
        return hashlib.md5(f'{self.merchant_id}:{invoice_id}:{amount * 100}:{method_id}:{self.key1}'.encode()).hexdigest()

    def create_invoice(self, invoice_id: str, description: str, amount: int, method: str, country: str, currency: str) -> FinPayInvoice:
        return FinPayInvoice(self, invoice_id, description, amount, method, country, currency, self.gen_signature(invoice_id, amount, method))
