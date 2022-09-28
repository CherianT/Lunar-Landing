# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import os
import boto3

from ask_sdk_dynamodb.adapter import DynamoDbAdapter

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')

ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

altitude = 100 # altitude above moon
speed = 10      # speed approaching the moon
fuel = 1000    # how much fuel is left
gravity = 1 # acceleration due to gravity

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to Lunar Landing. You can say Play to start the game or Stop to quit playing. If you have any doubt, just say Help. Which would you like to try?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class PlayHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Play")(handler_input)

    def handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        
        attr['altitudecal'] = altitude
        attr['speedcal'] = speed
        attr['fuelcal'] = fuel
        
        if not attr:
            attr['altitudecal'] = altitude
            attr['speedcal'] = speed
            attr['fuelcal'] = fuel
        # type: (HandlerInput) -> Response
        
        speak_output = "Hello there, Captain. We just entered the moon's atmosphere. The current status of the shuttle is Altitude = " + str(attr['altitudecal']) + " kilometers, Speed = "+ str(attr['speedcal']) + " kilometers per hour and Fuel = "+ str(attr['fuelcal']) + " litres. You can burn between 1 and 100 litres of fuel. How much fuel would you like to burn?"
        
        handler_input.attributes_manager.persistent_attributes = attr
        handler_input.attributes_manager.save_persistent_attributes()

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CalculationHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Calculation")(handler_input)
        
    def handle(self, handler_input):
        
        slots = handler_input.request_envelope.request.intent.slots
        burncal = int(handler_input.request_envelope.request.intent.slots["burnno"].value)
        
        attr = handler_input.attributes_manager.persistent_attributes
        # type: (HandlerInput) -> Response

        attr['altitudecal'] = attr['altitudecal'] - attr['speedcal']
        attr['fuelcal'] = attr['fuelcal'] - burncal
        attr['speedcal'] = attr['speedcal'] + (gravity - burncal//10)

        if attr['fuelcal'] > 0:
            if attr['altitudecal'] > 0:
                speak_output = "The current status of the shuttle is Altitude = " + str(attr['altitudecal']) + " kilometers, Speed = "+ str(attr['speedcal']) + " kilometers per hour, Fuel = "+ str(attr['fuelcal']) + " litres and Previous burn = {b} litres. How much fuel would you like to burn?".format(b=burncal)
                handler_input.attributes_manager.persistent_attributes = attr
                handler_input.attributes_manager.save_persistent_attributes()
            
            elif attr['altitudecal'] <= 0 and attr['speedcal'] >= 4:
                speak_output = "You have crashed landed on the moon's surface. Sorry, there were no survivors. You blew it. In fact, you blasted a new lunar crater. To try again say play again or to quit the game say stop."
                handler_input.attributes_manager.delete_persistent_attributes()
                
            elif attr['altitudecal'] <= 0 and attr['speedcal'] <= 4:
                speak_output = "You have landed successfully on the moon's surface. You have saved your crew and have completed your mission. Everyone back home on Earth is proud of your success. To try again say play again or to quit the game say stop."
                handler_input.attributes_manager.delete_persistent_attributes()
                
        elif attr['fuelcal'] <= 0:
            speak_output = "You are out of fuel. You have crashed landed on the moon's surface. Sorry, there were no survivors. To try again say play again or to quit the game say stop."
            handler_input.attributes_manager.delete_persistent_attributes()
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to the help center. A subgenre of video games called Lunar Lander is partially inspired by the Apollo Lunar Module's Moon landing in 1969. This game is inspired by the Lunar Lander. The basic operation in this game is to use thrusters to slow the ship's descent and manage to land safely. After you start playing, simply enter the amount of litres of fuel you wish to burn between 0 and 100. To start playing, say Play or say Stop to quit playing."
        handler_input.attributes_manager.delete_persistent_attributes()
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "We hope you enjoyed the game. We shall be looking forward to seeing you again. Goodbye!"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Play or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Any cleanup logic goes here.
        handler_input.attributes_manager.delete_persistent_attributes()
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()
sb = CustomSkillBuilder(persistence_adapter = dynamodb_adapter)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PlayHandler())
sb.add_request_handler(CalculationHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()