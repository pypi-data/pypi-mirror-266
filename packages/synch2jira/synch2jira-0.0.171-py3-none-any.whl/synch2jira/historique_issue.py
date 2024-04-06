from synch2jira.historique import HistoriqueSynchronisation
import config


class Historique(HistoriqueSynchronisation):

    def save_synch(self):
        try:
            with open(config.history_file, "a") as history:
                history.write(self.date + "," + self.synchro_message + "\n")
                history.close()
                return True
        except Exception as e:
            print(e)
            return False
