from flask import *
from flask_cors import CORS

from AI.MCTS import MCTS
from TicTacToe import TTTInstance
from Constants import *
import ErrorHandlers
from datetime import datetime
import atexit
from apscheduler.schedulers.background import BackgroundScheduler


class App:

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.config["DEBUG"] = True

        self.Instances = []
        self.ClosedIDs = []

        @self.app.route("/game/create", methods=["POST"])
        def createGame():
            if len(self.ClosedIDs) != 0:
                instanceID = self.ClosedIDs.pop()
                self.Instances[instanceID] = TTTInstance()
            else:
                if len(self.Instances) >= MAX_GAMES:
                    ErrorHandlers.insufficient_resources(
                        "Max number of concurrent game has been hit. Try play again later.")
                    return
                else:
                    self.Instances.append(TTTInstance())
                    instanceID = len(self.Instances) - 1

            print("Game created with ID: " + str(instanceID))
            return str(instanceID)

        @self.app.route("/game/ping", methods=["GET"])
        def pingGame():
            passed, error = validateIDInput(request.args)
            if not passed:
                return error
            instanceID = int(request.args["id"])
            self.Instances[instanceID].ping()
            return "true"

        @self.app.route("/game/close", methods=["DELETE"])
        def closeGame():
            passed, error = validateIDInput(request.args)
            if not passed:
                return error
            instanceID = int(request.args["id"])
            self.Instances[instanceID].close()
            self.ClosedIDs.append(instanceID)

        @self.app.route("/game/play", methods=["POST"])
        def playGame():
            passed, error = validateIDInput(request.args)
            if not passed:
                return error
            passed, error = validateIndexInput(request.args)
            if not passed:
                return error

            instanceID = int(request.args["id"])
            index = int(request.args["index"])
            instance = self.Instances[instanceID]

            passed, error = validatePlay(instance, index)
            if not passed:
                return error

            instance.play(index)
            return instance.getBoard()

        @self.app.route("/game/play/ai", methods=["POST"])
        def playGameAi():
            passed, error = validateIDInput(request.args)
            if not passed:
                return error

            instanceID = int(request.args["id"])
            instance = self.Instances[instanceID]

            passed, error = validateAiPlay(instance)
            if not passed:
                return error
            aiPlay = MCTS().GetPlayFromState(instance, MCTS_TRIALS)
            instance.play(aiPlay)
            return instance.getBoard()

        @self.app.route("/game", methods=["GET"])
        def getGame():
            passed, error = validateIDInput(request.args)
            if not passed:
                return error

            instanceID = int(request.args["id"])
            return self.Instances[instanceID].getBoard()

        @self.app.route("/game/jump", methods=["POST"])
        def jumpTo():
            passed, error = validateIDInput(request.args)
            if not passed:
                return error

            instanceID = int(request.args["id"])
            instance = self.Instances[instanceID]
            passed, error = validateJumpTo(instance, request.args)
            if not passed:
                return error

            step = int(request.args["step"])
            instance.jumpToHistory(step)
            return instance.getBoard()

        def validateIDInput(args):
            if "id" not in args:
                return False, ErrorHandlers.bad_request("Please provide the game ID")
            try:
                instanceID = int(args["id"])
            except ValueError:
                return False, ErrorHandlers.bad_request("Game ID provided was not a number")

            if instanceID < 0 or instanceID >= len(self.Instances) or instanceID in self.ClosedIDs:
                return False, ErrorHandlers.not_found("Ongoing game with ID " + str(instanceID) + " was not found.")

            return True, None

        def validateIndexInput(args):
            if "index" not in args:
                return False, ErrorHandlers.bad_request("Please provide the index of the intended play.")
            try:
                index = int(args["index"])
            except ValueError:
                return False, ErrorHandlers.bad_request("Index provided not number")

            if index < 0 or index >= 9:
                return False, ErrorHandlers.bad_request("Index provided was out of bounds")

            return True, None

        def validatePlay(instance, index):
            gameEnded, winner = instance.hasGameEnded()
            if gameEnded:
                return False, ErrorHandlers.bad_request("Game has already been won by " + winner)

            if not instance.isCurrentSubBoardCellBlank(index) and not instance.isCurrentSubBoardFull():
                return False, ErrorHandlers.bad_request("Chosen cell has already been played in!")

            return True, None

        def validateJumpTo(instance, args):
            if "step" not in args:
                return False, ErrorHandlers.bad_request("Please provide the step of history to jump to.")
            try:
                index = int(args["step"])
            except ValueError:
                return False, ErrorHandlers.bad_request("Step provided not number")

            historyLength = len(instance.getHistory())
            if index < 0 or index >= historyLength:
                return False, ErrorHandlers.bad_request("History step out of range")
            else:
                return True, None
            
        def validateAiPlay(instance):
            if instance.winner == 0:
                return True, None
            else:
                return False, ErrorHandlers.bad_request("Game already Ended")

    def run(self):
        self.registerBackgroundTasks()
        self.app.run()

    def registerBackgroundTasks(self):
        def checkForStaleGames():
            self.app.logger.info("Checking for stale games")
            for ID in range(len(self.Instances)):
                if ID not in self.ClosedIDs:
                    game = self.Instances[ID]
                    if (datetime.now() - game.lastPingTime).total_seconds() > TIME_TILL_SELF_CLOSE:
                        self.app.logger.info(f"Stale game with ID {ID} found. Closing.")
                        game.close()
                        self.ClosedIDs.append(ID)

        self.app.logger.info("Starting Background Tasks")
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=checkForStaleGames, trigger="interval", seconds=TIME_TILL_SELF_CLOSE)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
