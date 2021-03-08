import nymea
from pybotvac import Account, Neato, OAuthSession, PasswordlessSession, PasswordSession, Vorwerk, Robot

# pybotvac library: https://github.com/stianaske/pybotvac

thingsAndRobots = {}


def setupThing(info):
    # Setup for the account
    if info.thing.thingClassId == accountThingClassId:
        username = info.thing.paramValue(accountThingUserParamTypeId)
        password = info.thing.paramValue(accountThingPasswordParamTypeId)
        try:
            password_session = PasswordSession(email=username, password=password, vendor=Neato())
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
        account = Account(password_session)

        # List all robots associated with account
        logger.log("account created. Robots:", account.robots);

        thingDescriptors = []
        for robot in account.robots:
            logger.log(robot)
            # Check if this robot is already added in nymea
            for thing in myThings():
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
        rbtState = thingsAndRobots[info.thing].get_robot_state()
        rbtStateJson = rbtState.json()
        rbtStateCommands = rbtStateJson['availableCommands']
        rbtStartAv = rbtStateCommands['start']
        rbtPauseAv = rbtStateCommands['pause']
        rbtResumeAv = rbtStateCommands['resume']
        if rbtStartAv == True:
            logger.log("Start cleaning")
            thingsAndRobots[info.thing].start_cleaning()
        elif rbtPauseAv == True:
            logger.log("Pause cleaning")
            thingsAndRobots[info.thing].pause_cleaning()
        elif rbtResumeAv == True:
            thingsAndRobots[info.thing].resume_cleaning()
        info.finish(nymea.ThingErrorNoError)
        return

    if info.actionTypeId == robotGoToBaseActionTypeId:
        thingsAndRobots[info.thing].send_to_base()
        info.finish(nymea.ThingErrorNoError)

    if info.actionTypeId == robotStopCleaningActionTypeId:
        thingsAndRobots[info.thing].stop_cleaning()
        info.finish(nymea.ThingErrorNoError)
