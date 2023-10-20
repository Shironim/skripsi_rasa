# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk.events import (
    SlotSet,
    FollowupAction,
    AllSlotsReset
)
from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
import requests
import time

def clean_name(name):
    return "".join([c for c in name if c.isalpha()])

class ValidateSearchProductForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_search_product_form"
        
    @staticmethod
    def merk_db() -> List[Text]:
        """Database of supported cuisines."""

        return [
            "nikon",
            "sony",
        ]
        
    @staticmethod
    def series_db() -> List[Text]:
        """Database of supported cuisines."""

        return [
            "a6000",
            "d500",
            "d70",
            "d7100",
            "a500",
            "tele",
            "kit",
            "fix",
        ]
        
    @staticmethod
    def category_db() -> List[Text]:
        """Database of supported cuisines."""

        return [
            "kamera",
            "lensa",
        ]
    def validate_merk(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        if value.lower() in self.merk_db():
            return {"merk": value}
        else:
            dispatcher.utter_message(text="Mohon maaf, Kami hanya memiliki merk Nikon dan Sony, silakan pilih merk yang tersedia")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"merk": None}
    
    def validate_category(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""
        if value.lower() in self.category_db():
            return {"category": value}
        else:
            dispatcher.utter_message(text="ADMS menyediakan kamera dan lensa, silakan pilih kategori yang tersedia")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"category": None}
    
    def validate_series(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        if value.lower() in self.series_db():
            return {"series": value}
        else:
            dispatcher.utter_message(text="utter_tanya_ulang")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"series": None}
    
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
    # Validate return_date must be greater than rent_date
        if num_pick_date > num_return_date:
            if num_return_date > 31 or num_return_date < 1:
                dispatcher.utter_message(text="Tanggal pengembalian tidak valid, tolong masukkan tanggal yang benar")
                return {"return_date": None}
            dispatcher.utter_message(text="Sepertinya ada kesalahan memasukan tanggal pengembalian, tolong masukkan tanggal yang benar")
            return {"return_date": None}
        elif num_pick_date < num_return_date:
            return {"return_date": value}
        
    def validate_pick_date(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        
        pick_date = next(tracker.get_latest_entity_values('number'), None)
    # Validate return_date must be greater than rent_date
        if int(pick_date) > 31 or int(pick_date) < 1:
            dispatcher.utter_message(text="Tanggal pengambilan tidak valid, tolong masukkan tanggal yang benar")
            return {"pick_date": None}
        return {"pick_date": pick_date}
    
    # Validate month in date entity
    # Confirm before sending email
    
class ActionFetchSearchProduct(Action):
    # Action from click button UI in web app
    def name(self) -> Text:
        return "action_fetch_search_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Fetch data to check availability this product
        # then, ask follow up question, if user want to rent this product or not
        # if yes, then store id product to slot array
        category = tracker.get_slot("category")
        merk = tracker.get_slot("merk")
        series = tracker.get_slot("series")
        url = f"http://localhost:5000/produk/{merk}/{series}/{category}"
        response = requests.get(url)
        jsonResult = response.json()
        # print('res: ', jsonResult)
        # print('jumlah data: ', len(jsonResult.get('data')))
        # print('id produk: ', jsonResult.get('data')[0].get('id_produk'))
        # print('type: ', type(jsonResult))
        if len(jsonResult.get('data')) == 1:
            if jsonResult.get('data')[0].get('status') == 'tersedia':
                return [SlotSet('product_fetch_avaliable', True), SlotSet('product_fetch', jsonResult.get('data'))]
            else:
                return [SlotSet('product_fetch_avaliable', False)]
        elif len(jsonResult.get('data')) == 0:
            dispatcher.utter_message(text=f"Maaf kak, kami tidak memiliki {category} yang kamu cari")
            dispatcher.utter_message(response="utter_bertanya_kebutuhan_lainnya")
        else:
            dispatcher.utter_message(text="Silakan pilih produk yang ingin disewa")
        # return [SlotSet('product_fetch', jsonResult.get('data'))]
        # reset slot value, every call action tanya produk
        # return [SlotSet("category", None), SlotSet("merk", None), SlotSet("series", None)]
class ActionConfirmToRent(Action):
    # Action from click button UI in web app
    def name(self) -> Text:
        return "action_confirm_to_rent"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_bertanya_kebutuhan_lainnya")
        
        product_fetch = tracker.get_slot("product_fetch")
        prev_product_cart = tracker.get_slot("id_product_cart")
        if tracker.get_slot("product_fetch_avaliable") == True:
            if tracker.get_intent_of_latest_message() == "konfirmasi_sewa":
                if prev_product_cart == None:
                    return [SlotSet("confirm_to_rent", True), SlotSet('id_product_cart', product_fetch[0].get('id_produk')), SlotSet("product_fetch", None), SlotSet("product_fetch_avaliable", False), SlotSet("category", None), SlotSet("merk", None), SlotSet("series", None), FollowupAction("utter_bertanya_kebutuhan_lainnya")]
                else:
                    prev_product_cart.append(product_fetch[0].get('id_produk'))

                    return [SlotSet("confirm_to_rent", True), SlotSet('id_product_cart', prev_product_cart), SlotSet("product_fetch", None), SlotSet("product_fetch_avaliable", False), SlotSet("category", None), SlotSet("merk", None), SlotSet("series", None), FollowupAction("utter_bertanya_kebutuhan_lainnya")]
                
            elif tracker.get_intent_of_latest_message() == "deny":
                return [SlotSet("confirm_to_rent", False), SlotSet("product_fetch", None), SlotSet("product_fetch_avaliable", False), SlotSet("category", None), SlotSet("merk", None), SlotSet("series", None)]
        return []
class ActionEndConversation(Action):
    # Action from click button UI in web app
    def name(self) -> Text:
        return "action_selesai_percakapan"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_selesai_percakapan")

        return [AllSlotsReset()]   
class ActionConfirmSearchAnother(Action):
    # Action from click button UI in web app
    def name(self) -> Text:
        return "action_confirm_search_another_product"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_intent_of_latest_message() == "konfirmasi_sewa":
            return [SlotSet('want_to_rent_another_product', True)]
        elif tracker.get_intent_of_latest_message() == "deny":
            return [SlotSet('want_to_rent_another_product', False)]
        return []
class ActionSendEmailInvoice(Action):
    # Action from click button UI in web app
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
        url = f"http://localhost:5000/send-invoice"
        response = requests.post(url, json=data)
        print("JSON Response ", response.json())
        return [AllSlotsReset()]

class ActionRespPengembalianAlat(Action):

    def name(self) -> Text:
        return "action_resp_pengembalian_alat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        pengembalian = tracker.get_slot("pengembalian")
        terlambat = tracker.get_slot("terlambat")
        if pengembalian:
            dispatcher.utter_message(text=f"entitas pengembalian :  {pengembalian}!")
            dispatcher.utter_message(response="utter_pengembalian_alat")
        elif terlambat:
            dispatcher.utter_message(text=f"entitas terlambat {terlambat}!")
            dispatcher.utter_message(response="utter_pengembalian_alat")
        else:
            dispatcher.utter_message(response="utter_pengembalian_alat")
        return []
    
class ActionSapaan(Action):

    def name(self) -> Text:
        return "action_sapaan"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        current_time = time.strftime("%H:%M:%S")
        if current_time < "12:00:00":
            dispatcher.utter_message(response="utter_sapaan_pagi")
        elif current_time > "12:00:00" and current_time < "15:00:00":
            dispatcher.utter_message(response="utter_sapaan_siang")
        elif current_time > "15:00:00" and current_time < "18:00:00":
            dispatcher.utter_message(response="utter_sapaan_sore")
        else:
            dispatcher.utter_message(response="utter_sapaan_malam")
        
        # dispatcher.utter_message(text=f"ini dari action sapaan {current_time}!")
        return []
# another validation form
# class ValidateNewsletterForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_newsletter_form"

#     async def required_slots(
#             self,
#             slots_mapped_in_domain: List[Text],
#             dispatcher: "CollectingDispatcher",
#             tracker: "Tracker",
#             domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:
#         if not tracker.get_slot("can_ask_age"):
#             slots_mapped_in_domain.remove("age")

#         return slots_mapped_in_domain

    # def validate_return_date(
    #     self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
        
    #     pick_date = tracker.get_slot("pick_date")
    #     bulan = tracker.get_slot("bulan")
    #     return_date = next(tracker.get_latest_entity_values('number'), None)
    # # Validate return_date must be greater than rent_date
    #     if pick_date > return_date:
    #         if return_date > 31 or return_date < 1:
    #             dispatcher.utter_message(text="Tanggal pengembalian tidak valid, tolong masukkan tanggal yang benar")
    #             return {"return_date": None}
    #         dispatcher.utter_message(text="Sepertinya ada kesalahan memasukan tanggal pengembalian, tolong masukkan tanggal yang benar")
    #         return {"return_date": None}
    #     elif pick_date < return_date:
    #         if bulan == "februari" and return_date > 29:
    #             dispatcher.utter_message(text="Tanggal pengembalian tidak valid, tolong masukkan tanggal yang benar")
    #             return {"return_date": None}
    #         elif bulan == "februari" and return_date < 30 and return_date > 0:
    #             return {"return_date": value}
        
    # def validate_pick_date(
    #     self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
        
    #     pick_date = next(tracker.get_latest_entity_values('number'), None)
    #     bulan = tracker.get_slot("bulan")
    # # Validate return_date must be greater than rent_date
    #     if pick_date > 31 or pick_date < 1:
    #         dispatcher.utter_message(text="Tanggal pengambilan tidak valid, tolong masukkan tanggal yang benar")
    #         return {"pick_date": None}
    #     elif pick_date < 32 and pick_date > 0:
    #         if bulan == "februari" and pick_date > 29:
    #             dispatcher.utter_message(text="Tanggal pengembalian tidak valid, tolong masukkan tanggal yang benar")
    #             return {"return_date": None}
    #         elif bulan == "februari" and pick_date < 30 and pick_date > 0:
    #             return {"pick_date": pick_date}
    #         elif not bulan == "februari" and pick_date < 32 and pick_date > 0:
    #             return {"pick_date": pick_date}

    
    # def validate_bulan(
    #     self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
        
    #     if value.lower() in self.bulan_db():
    #         return {"bulan": value}
    #     else:
    #         dispatcher.utter_message(response="utter_tanya_ulang")
    #         # validation failed, set this slot to None, meaning the
    #         # user will be asked for the slot again
    #         return {"bulan": None}