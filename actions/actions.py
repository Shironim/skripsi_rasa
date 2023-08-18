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


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []

class ActionSayMerkKamera(Action):

    def name(self) -> Text:
        return "action_tanya_kamera_spesifik"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        merk_kamera = tracker.get_slot("merk_kamera")
        if not merk_kamera:
            dispatcher.utter_message(text="Saya tidak tahu merk kamera yang kamu cari")
        else:
            dispatcher.utter_message(text=f"kamera yang kamu cari {merk_kamera}!")
        return []