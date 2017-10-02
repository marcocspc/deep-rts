import copy
import os
import time

from game import Config
from game.api.Event import Event
from game.graphics.GUI import GUI
from game.graphics.NoGUI import NoGUI
from game.loaders.AdjacentMap import AdjacentMap
from game.loaders.MapLoader import MapLoader
from game.logic.Player.Player import Player
from game.logic.UnitManager import UnitManager
from game.util.FastDict import FastDict
from game.util.GameClock import GameClock

if not MapLoader.preloaded:
    MapLoader.preload(Config.GAME_MAP)
    AdjacentMap.generate()

class Game:
    def __init__(self, players=2, ai_instance=False):
        """
        # Constructs a game instance
        :param players: Number of players in this game
        :param ai_instance: Describes if this game should be considered a instance of a AI simulation
        """
        self.UnitManager = UnitManager
        self.Map = MapLoader
        self.AdjacentMap = AdjacentMap

        self.n_players = players
        self.ai_instance = ai_instance


        self.parallel_worker = None

        self.units = {}

        self.winner = None
        self.paused = False

        # Data Matrix
        self.data = {
            "unit": FastDict(),
            "unit_pid": FastDict(),
        }

        # Create game clock
        self.clock = GameClock()

        # Create Players
        self.players = []

        # Create GUI
        self.gui = GUI(self) if Config.GUI_ON else NoGUI(self)

    def init(self, no_players=False):
        self.clock = GameClock()
        self.clock.schedule(self.caption, 1.0)
        self.clock.schedule(self.scheduled_save, Config.SAVE_FREQUENCY)
        self.clock.update(self.process, Config.UPS)  # 16
        self.clock.render(self.render, Config.FPS)  # 607

        if not no_players:
            self.players = [Player(self, x) for x in range(self.n_players)]
            [p.reset() for p in self.players]

    def set_gui(self):
        if not Config.GUI_ON and not self.ai_instance:
            return

        self.gui.player = self.players[0]

    def get_unit(self, x, y):
        return self.units[self.data['unit'][x, y]]


    @staticmethod
    def start(n_players, ParallellWorker=None):
        g = Game(n_players)
        g.init()
        g.parallell_worker = ParallellWorker
        return g

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def reset(self):
        self.gui.reset()
        self.clock.reset()
        self.units = dict()
        self.data = {
            "unit": FastDict(),
            "unit_pid": FastDict(),
        }

        [p.reset() for p in self.players]

    def toJSON(self):
        return {
            'players': [p.toJSON() for p in self.players],
            'map_name': Config.GAME_MAP,
            'winner': self.winner,
            'clock': self.clock.toJSON(),
            'units': {uid: u.toJSON() for uid, u in self.units.items()},
            'version': Config.VERSION
        }

    def caption(self):
        self.gui.caption()

    def hook(self,
             on_victory=None,
             on_defeat=None,
             on_event=None):
        """
        Hook a local AI
        :return:
        """
        p = self.players[0]
        p.Event.on_event(on_event)
        p.Event.on_defeat(on_defeat)
        p.Event.on_victory(on_victory)
        return p.id, p.Event.Action

    def loop(self):
        while Config.IS_RUNNING:
            if self.paused:
                self.clock.tick_schedule()  # Continue to tick scheduled tasks
                time.sleep(.1)
                continue
            self.clock.tick()

    def process(self, frame):
        for p in self.players:
            p.process(1)

        #Event.notify_broadcast(Event.NEW_STATE, frame)

    def scheduled_save(self):
        if not self.winner and not self.ai_instance:
            self.save()

    def save(self):
        data = self.toJSON()
        if Config.SAVE_TO_FILE and not self.ai_instance:
            with open(Config.REPORT_DIR + "state.json", "w") as f:
                f.write(Config.LIBRARY_JSON.dumps(data))
        return data

    @staticmethod
    def load(fromfile=True, state=None, ai_instance=False):
        save_file = Config.REPORT_DIR + "state.json"
        data = None
        if fromfile and os.path.isfile(save_file):
            data = Config.LIBRARY_JSON.load(open(save_file), parse_int=None)

        if fromfile and state is None and data is None:
            print("Could not find state-file, starting new game...")
            g = Game()
            g.init()
            return g
        else:
            data = state

        if data['version'] != Config.VERSION:
            print("Incorrect version of the game! %s found, %s required" % (data['version'], Config.VERSION))
            # Start plain game
            g = Game(ai_instance=ai_instance)
            g.init()
            return g

        g = Game(players=len(data['players']), ai_instance=ai_instance)
        g.init(no_players=True)

        g.clock.load(data['clock'])

        g.players = []
        for p_data in data['players']:
            player = Player(g, p_data['id'], ai_instance=True)
            player.load(p_data)
            g.players.append(player)

            for uid in player.units:
                try:
                    u_data = data['units'][uid]
                except:
                    u_data = data['units'][uid]
                unit_class = UnitManager.get_class_by_id(u_data['id'])

                u = unit_class(player, init=False)

                u.load(u_data, uid)
                g.units[uid] = u
                u.unit_id = uid

                for xy in u.unit_area():
                    g.data['unit'][xy] = uid
                    g.data['unit_pid'][xy] = p_data['id']

        return g

    def calculate_winner(self):
        alive = [p for p in self.players if not p.defeated]

        if len(alive) == 1:
            #self.scheduled_save(0)                              # Save terminal game state
            self.winner = alive[0]                              # Retrieve winning player

            # Emit terminal state for defeated players
            for p in self.players:
                if p == self.winner: continue
                p.Event.notify_defeat({"shoiuld be savegame":None})

            # Emit terminal state for winning player
            self.winner.Event.notify_victory({"shoiuld be savegame":None})

            self.reset()

    def render(self):
        self.gui.render()