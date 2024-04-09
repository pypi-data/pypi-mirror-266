import os
import sys

import Orange.data
from Orange.widgets import widget

from orangecontrib.development_tool.widgets import shared_functions
from Orange.widgets.utils.signals import Input, Output
from PyQt5 import QtCore, QtWidgets

from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon


from orangecontrib.development_tool.widgets.Gpt4AllManagement import call_completion_api
from PyQt5.QtWidgets import QMessageBox


class LLM(widget.OWWidget):
    name = "LLM"
    description = "Large language model"
    icon = "icons/chat-bot.png"
    priority = 10

    dossier_du_script = os.path.dirname(os.path.abspath(__file__))
    input_data = None
    model_name = "orca-mini-3b-gguf2-q4_0.gguf" #example; a remplacer
    output_data = None
    input_data = None

    localhost = ""
    message_content = ""

    class Inputs:
        input_data = Input("Data", Orange.data.Table)


    class Outputs:
        data_out = Output("Data", Orange.data.Table)

    @Inputs.input_data
    def set_data(self, dataset):
        self.input_data = dataset

    def __init__(self):
        super().__init__()
        self.setFixedWidth(1200)
        self.setFixedHeight(200)


        # QT Management
        uic.loadUi(self.dossier_du_script + '/widget_designer/llm.ui', self)
        self.setAutoFillBackground(True)

        self.label = self.findChild(QtWidgets.QLabel, 'label')
        self.localhost = self.findChild(QtWidgets.QLineEdit, 'localhost')
        self.localhost.setText("localhost:4891")

        self.message_content = self.findChild(QtWidgets.QLineEdit, 'message')

        self.applyButton = self.findChild(QtWidgets.QPushButton, 'applyButton')
        self.applyButton.clicked.connect(self.use_llm)

        self.push_button = self.findChild(QtWidgets.QPushButton, 'pushButton_show_hkh_website')
        self.push_button.setIcon(QIcon(self.dossier_du_script+'/icons/Logo_HKH.svg'))
        self.push_button.setIconSize(QSize(65, 65))
        self.push_button.clicked.connect(shared_functions.openlink)


    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.refresh_all()
        # return super.eventFilter(obj,event) # True on filtre l element
        return super().eventFilter(source, event)


        # True ou False -> False on ne filtre pas

    def refresh_all(self):
        return


    def use_llm(self):

        localhost = self.localhost.text()
        message_content = self.message_content.text()
        res = call_completion_api(localhost, message_content)

        # Si la réponse est vide, afficher un message d'erreur
        if not res:
            QMessageBox.critical(self, "Erreur", "La réponse est vide.")
        else:
            data = json.loads(res)

            # Accéder à la propriété content du premier élément de la liste choices
            response = data["choices"][0]["message"]["content"]
            print("Response", response)

            # Créer une Orange Data Table avec les données de la réponse
            # data = Orange.data.Table([message_content], ["Question"])
            #data_out = Orange.data.Table(res, ["Réponse"])
            df = pd.DataFrame({"Question": [message_content], "Réponse": response})

            # Envoyer la table en sortie
            out_data = table_from_frame(df)
            self.Outputs.data_out.send(out_data)
if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication

    app = QApplication(sys.argv)
    mon_objet = LLM()
    mon_objet.show()


    mon_objet.handleNewSignals()
    app.exec_()
