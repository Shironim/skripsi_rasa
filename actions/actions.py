from typing import Any, Text, Dict, List
from rasa_sdk.events import (
    SlotSet,
    AllSlotsReset
)
from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
import requests
import times

def clean_name(name):
    return "".join([c for c in name if c.isalpha()])

class ValidateRentProductForm(FormValidationAction):
   
    def name(self) -> Text:
        return "validate_rent_product_form"
        
    def validate_user_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if len(value) <= 2:
            dispatcher.utter_message(text="Namamu terlalu pendek, tolong masukkan nama yang benar")
            return {"user_name": None}
        return {"user_name": value}
    
    def validate_user_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        
        if len(value) <= 2:
            dispatcher.utter_message(text="Emailmu terlalu pendek, tolong masukkan email yang benar")
            return {"user_email": None}
        return {"user_email": value}
    
    def validate_pick_date(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        
        pick_date = next(tracker.get_latest_entity_values('number'), None)
        print('pick_date: ', pick_date)
        if int(pick_date) > 31 or int(pick_date) < 1:
            dispatcher.utter_message(text="Tanggal pengambilan tidak valid, tolong masukkan tanggal yang benar")
            return {"pick_date": None}
        return {"pick_date": pick_date}

    def validate_return_date(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        
        pick_date = tracker.get_slot("pick_date")
        return_date = next(tracker.get_latest_entity_values('number'), None)
        num_pick_date = int(pick_date)
        num_return_date = int(return_date)
        if num_pick_date > num_return_date:
            if num_return_date > 31 or num_return_date < 1:
                dispatcher.utter_message(text="Tanggal pengembalian tidak valid, tolong masukkan tanggal yang benar")
                return {"return_date": None}
            dispatcher.utter_message(text="Sepertinya ada kesalahan memasukan tanggal pengembalian, tolong masukkan tanggal yang benar")
            return {"return_date": None}
        elif num_pick_date < num_return_date:
            return {"return_date": value}
    
class ActionFetchSearchProduct(Action):
    def name(self) -> Text:
        return "action_fetch_search_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        category = tracker.get_slot("category")
        merk = tracker.get_slot("merk")
        series = tracker.get_slot("series")
        rentang_fokus = tracker.get_slot("rentang_fokus")

        search = {
            "kategori": category,
            "merk": merk,
            "seri": series,
            "rentang_fokus": rentang_fokus,
        }
        print('action_fetch_search_product: ', search)
        url = f"https://skripsi-backend-nine.vercel.app/api/search-produk/"
        response = requests.post(url, json=search)
        jsonResult = response.json()
        dispatcher.utter_message(json_message=jsonResult)
        if jsonResult.get('data') == None or len(jsonResult.get('data')) == 0:
            return [SlotSet('product_fetch_avaliable', False), SlotSet("category", None), SlotSet("merk", None), SlotSet("series", None), SlotSet("rentang_fokus", None)]
        elif len(jsonResult.get('data')) >= 1:
            dispatcher.utter_message(response="utter_menawarkan_untuk_disewa")
            return [SlotSet('product_fetch_avaliable', True), SlotSet("category", None), SlotSet("merk", None), SlotSet("series", None), SlotSet("rentang_fokus", None)] 


class ActionInsertToCart(Action):
    def name(self) -> Text:
        return "action_insert_to_cart"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        category = tracker.get_slot("category")
        merk = tracker.get_slot("merk")
        series = tracker.get_slot("series")
        rentang_fokus = tracker.get_slot("rentang_fokus")
        search = {
            "kategori": category,
            "merk": merk,
            "seri": series,
            "rentang_fokus": rentang_fokus,
        }
        print('action_insert_to_cart: ', search)

        url = f"https://skripsi-backend-nine.vercel.app/api/search-produk/"
        response = requests.post(url, json=search)
        jsonResult = response.json()
        result = jsonResult.get('data')
        prev_product_cart = tracker.get_slot("id_product_cart")
        if len(jsonResult.get('data')) == 1:
            dispatcher.utter_message(response="utter_produk_masuk_keranjang_belanja")
            if prev_product_cart == None:
                return [SlotSet('id_product_cart', result[0].get('id_produk')), SlotSet("product_fetch_avaliable", True), SlotSet("category", None), SlotSet("merk", None), SlotSet("series", None), SlotSet("rentang_fokus", None)]
            else:
                prev_product_cart.append(result[0].get('id_produk'))
                return [SlotSet('id_product_cart', prev_product_cart), SlotSet('product_fetch_avaliable', True), SlotSet("category", None), SlotSet("merk", None), SlotSet("series", None), SlotSet("rentang_fokus", None)] 
            
        return []
class ActionCheckCart(Action):
    def name(self) -> Text:
        return "action_check_cart"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        id_product_cart = tracker.get_slot("id_product_cart")
        
        search = {
            "produk": id_product_cart,
        }

        url = f"https://skripsi-backend-nine.vercel.app/api/getSeveralProduct/"
        response = requests.post(url, json=search)
        jsonResult = response.json()
        if id_product_cart == None:
            dispatcher.utter_message(response="utter_keranjang_kosong")
        else:
            dispatcher.utter_message(text="Isi keranjang belanja anda : ")
            dispatcher.utter_message(json_message=jsonResult)   
            dispatcher.utter_message(text="Apakah anda mau checkout sekarang ? ")
        
        return []
class ActionCheckout(Action):
    def name(self) -> Text:
        return "action_checkout"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        produk = tracker.get_slot("id_product_cart")

        if produk == None:
            dispatcher.utter_message(response="utter_keranjang_kosong")
            return [SlotSet('want_to_checkout', False)]
        else:
            dispatcher.utter_message(text="Baik, saya akan bantu untuk melakukan checkout")
            return [SlotSet('want_to_checkout', True)]

class ActionEndConversation(Action):
    def name(self) -> Text:
        return "action_selesai_percakapan"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_selesai_percakapan")

        return [AllSlotsReset()]   
class ActionConfirmSearchAnother(Action):
    def name(self) -> Text:
        return "action_confirm_checkout"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_intent_of_latest_message() == "konfirmasi":
            return [SlotSet('want_to_checkout', True)]
        elif tracker.get_intent_of_latest_message() == "menolak":
            return [SlotSet('want_to_checkout', False)]
        return []
class ActionSendEmailInvoice(Action):
    def name(self) -> Text:
        return "action_send_email_invoice"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        nama_user = tracker.get_slot("user_name")
        email_user = tracker.get_slot("user_email")
        tanggal_diambil = tracker.get_slot("pick_date")
        tanggal_dikembalikan = tracker.get_slot("return_date")
        produk = tracker.get_slot("id_product_cart")

        data = {
            "nama_user": nama_user,
            "email_user": email_user,
            "tanggal_diambil": tanggal_diambil,
            "tanggal_dikembalikan": tanggal_dikembalikan,
            "produk": produk
        }
        print('action_send_email_invoice: ', data)
        url = f"https://skripsi-backend-nine.vercel.app/api/send-invoice"
        requests.post(url, json=data)
        return [AllSlotsReset()]

class ActionSapaan(Action):

    def name(self) -> Text:
        return "action_sapaan"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        now = times.now()
        current_time = times.format(now, 'Asia/Jakarta', '%H:%M:%S')
        if current_time < "12:00:00":
            dispatcher.utter_message(response="utter_sapaan_pagi")
        elif current_time > "12:00:00" and current_time < "15:00:00":
            dispatcher.utter_message(response="utter_sapaan_siang")
        elif current_time > "15:00:00" and current_time < "18:00:00":
            dispatcher.utter_message(response="utter_sapaan_sore")
        else:
            dispatcher.utter_message(response="utter_sapaan_malam")
        
        return []