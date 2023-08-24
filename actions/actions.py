# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionTanyaProduk(Action):

    def name(self) -> Text:
        return "action_tanya_produk"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        produk = tracker.get_slot("produk")
        merk = tracker.get_slot("merk")
        if not produk and not merk:
            dispatcher.utter_message(text="Saya tidak tahu produk yang kamu cari")
        else:
            dispatcher.utter_message(text=f"produk yang kamu cari {produk}!")
            dispatcher.utter_message(text=f"merk yang kamu cari {merk}!")
        return []

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
            dispatcher.utter_message(template="utter_pengembalian_alat")
        elif terlambat:
            dispatcher.utter_message(text=f"entitas terlambat {terlambat}!")
            dispatcher.utter_message(template="utter_pengembalian_alat")
        else:
            dispatcher.utter_message(template="utter_pengembalian_alat")
        return []