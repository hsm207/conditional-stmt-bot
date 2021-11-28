# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.spacy_parser import parse_device_instruction


class ActionParseDeviceInstruction(Action):
    def __init__(self) -> None:

        super().__init__()

    def name(self) -> Text:
        return "action_parse_device_instruction"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        msg = tracker.latest_message["text"]

        if_stmt, then_stmt = parse_device_instruction(msg)

        if not if_stmt:
            dispatcher.utter_message(
                response="utter_acknowledge_instruction", then_text=then_stmt
            )
        else:
            dispatcher.utter_message(
                response="utter_acknowledge_conditional_instruction",
                if_text=if_stmt,
                then_text=then_stmt,
            )

        return [
            SlotSet("condition", if_stmt),
            SlotSet("action", then_stmt),
            SlotSet("action_intent", tracker.latest_message["intent"]["name"]),
        ]
