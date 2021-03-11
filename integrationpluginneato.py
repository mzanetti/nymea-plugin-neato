import nymea
from pybotvac import Account, Neato, OAuthSession, PasswordlessSession, PasswordSession, Vorwerk, Robot
import json
import time
import threading

# pybotvac library: https://github.com/stianaske/pybotvac

thingsAndRobots = {}
oauthSessions = {}

timer = None

def startPairing(info):
    # Start OAuth2 session
    apiKey = apiKeyStorage().requestKey("neato")
    oauthSession = OAuthSession(client_id=apiKey.data("clientId"), client_secret=apiKey.data("clientSecret"), redirect_uri="https://127.0.0.1:8888", vendor=Neato())
    oauthSessions[info.transactionId] = oauthSession;
    authorizationUrl = oauthSession.get_authorization_url()
    info.oAuthUrl = authorizationUrl
    info.finish(nymea.ThingErrorNoError)


def confirmPairing(info, username, secret):
    # The user has successfully logged in at neato. Obtain the token from the OAuth session
    token = oauthSessions[info.transactionId].fetch_token(secret)
    pluginStorage().beginGroup(info.thingId)
    pluginStorage().setValue("token", json.dumps(token))
    pluginStorage().endGroup();
    del oauthSessions[info.transactionId]
    info.finish(nymea.ThingErrorNoError)


def setupThing(info):
    # Setup for the account
    if info.thing.thingClassId == accountThingClassId:
        pluginStorage().beginGroup(info.thing.id)
        token = json.loads(pluginStorage().value("token"))
        logger.log("setup", token)
        pluginStorage().endGroup();

        try:
            oAuthSession = OAuthSession(token=token)
            # Login went well, finish the setup
            info.finish(nymea.ThingErrorNoError)
        except:
            # Login error
            info.finish(nymea.ThingErrorAuthenticationFailure, "Login error")
            return

        # Mark the account as logged-in and connected
        info.thing.setStateValue(accountLoggedInStateTypeId, True)
        info.thing.setStateValue(accountConnectedStateTypeId, True)

        # Create an account session on the session to get info about the login
        account = Account(oAuthSession)

        # List all robots associated with account
        logger.log("account created. Robots:", account.robots);

        thingDescriptors = []
        for robot in account.robots:
            logger.log(robot)
            # Check if this robot is already added in nymea
            for thing in myThing():
                if thing.paramValue(robotThingSerialParamTypeId) == robot.serial:
                    # Yep, already here... skip it
                    continue

            thingDescriptor = nymea.ThingDescriptor(robotThingClassId, robot.name)
            thingDescriptor.params = [
                nymea.Param(robotThingSerialParamTypeId, robot.serial),
                nymea.Param(robotThingSecretParamTypeId, robot.secret)
            ]
            thingDescriptors.append(thingDescriptor)

        # And let nymea know about all the users robots
        autoThingsAppeared(thingDescriptors)
        return


    # Setup for the robots
    if info.thing.thingClassId == robotThingClassId:

        serial = info.thing.paramValue(robotThingSerialParamTypeId)
        secret = info.thing.paramValue(robotThingSecretParamTypeId)
        robot = Robot(serial, secret, info.thing.name)
        thingsAndRobots[info.thing] = robot;
        logger.log(robot.get_robot_state())
        # TODO: Add some states in the json and fill them in here

        info.finish(nymea.ThingErrorNoError)
        return;


def executeAction(info):
    if info.actionTypeId == robotStartCleaningActionTypeId:
        thingsAndRobots[info.thing].start_cleaning()
        info.finish(nymea.ThingErrorNoError)
        return

    if info.actionTypeId == robotStopCleaningActionTypeId:
        thingsAndRobots[info.thing].stop_cleaning()
        info.finish(nymea.ThingErrorNoError)

