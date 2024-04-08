import os
import sys
import Orange.data
import faiss
import numpy as np
import pandas as pd
from Orange.data.pandas_compat import table_from_frame, table_to_frame
from PyQt5 import uic, QtWidgets
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output


from sentence_transformers import SentenceTransformer
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QPushButton
from PyQt5 import QtCore


class DocumentEater(widget.OWWidget):
    name = "DocumentEater"
    description = "Documents ingestion to generate embeddings and store it in db and add it to input file"
    icon = "icons/data-integration.png"
    want_control_area = False

    dossier_du_script = os.path.dirname(os.path.abspath(__file__))
    input_data = None
    working_dir = os.path.dirname(os.path.abspath(__file__) + '/tests/')
    model_dir = os.path.join(working_dir, "Models")
    data_dir = os.path.join(working_dir, "Data")
    db_dir = os.path.join(data_dir, "db")

    class Inputs:
        input_data = Input("Data", Orange.data.Table)

    class Outputs:
        data_out = Output("Data", Orange.data.Table)

    @Inputs.input_data
    def set_data(self, input_data):
        self.input_data = input_data

    def __init__(self):
        super().__init__()

        self.setFixedWidth(497)
        self.setFixedHeight(266)
        # QT Management
        uic.loadUi(self.dossier_du_script + '/widget_designer/document_eater.ui', self)

        self.selectFolderButton = self.findChild(QPushButton, 'push')
        # Connexion du clic du bouton à la méthode pour ouvrir le sélecteur de fichier
        self.selectFolderButton.clicked.connect(self.select_folder)

        self.generate = self.findChild(QPushButton, 'generate')
        self.generate.clicked.connect(self.generate_embeddings)

    def select_folder(self):
        # Ouvrir la boîte de dialogue pour sélectionner un dossier
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        # Si un dossier a été sélectionné
        if folder_path:
            # Récupérer la liste des fichiers dans le dossier
            files = os.listdir(folder_path)
            # Vérifier s'il y a des fichiers dans le dossier
            if files:
                # Sélectionner le premier fichier dans la liste (peu importe lequel)
                file_name = files[0]
                # Construire le chemin complet du fichier en utilisant le chemin du dossier et le nom du fichier
                model_name = os.path.join(folder_path, file_name)
                # Mettre à jour self.model_name avec le chemin complet du fichier
                self.model_name = model_name
                # Imprimer le chemin complet du dossier et le nom du fichier
                print("Chemin du dossier sélectionné:", folder_path)
                print("Nom du fichier dans le dossier:", file_name)
                print("Chemin complet du fichier:", self.model_name)
            else:
                print("Le dossier sélectionné est vide.")
        else:
            print("Aucun dossier sélectionné.")

    def generate_embeddings(self):
        try:
            data = self.input_data

            df = table_to_frame(data)

            # Initialisation du modèle Sentence Transformers
            # Ajout repertoire pour aller chercher
            model_name = getattr(self, 'model_name', None)  # Obtient self.model_name s'il est défini, sinon None
            if model_name is None: #or model_name not in SentenceTransformer.available_models():
                # Utilise "all-mini-lm-6-v2" comme valeur par défaut si self.model_name n'est pas défini ou inconnu
                model_name = "all-MiniLM-L6-v2"
                print("Using default model:", model_name)

            model = SentenceTransformer(model_name)

            # Génération des embeddings pour chaque contenu dans la colonne "content"
            embeddings = []

            # Copie de la table d'entrée + génération des colonnes d'embeddings
            # Création d'un DataFrame à partir de la datatable
            data_dict = {}
            for col in data.domain.variables + data.domain.metas:
                data_dict[col.name] = []

            for row in data:
                for col in data.domain.variables + data.domain.metas:
                    data_dict[col.name].append(row[col].value)

            df = pd.DataFrame(data_dict)

            # Génération des embeddings pour chaque contenu dans la colonne "content"
            embeddings = []
            for content in df["content"]:
                embedding = model.encode(content)
                embeddings.append(embedding)

            # Création d'un DataFrame pour stocker les embeddings
            df_embeddings = pd.DataFrame(embeddings, columns=[f'embedding_{i}' for i in range(len(embeddings[0]))])

            # Concaténation du DataFrame des embeddings avec le DataFrame original
            df_concat = pd.concat([df, df_embeddings], axis=1)

            # Convertir les embeddings en un tableau numpy
            embeddings = np.array(df[[col for col in df.columns if col.startswith("embedding_")]].values.tolist())

            # Créer un index FAISS
            d = embeddings.shape[1]  # Dimension des embeddings
            index = faiss.IndexFlatL2(d)  # Indexeur FAISS

            # Ajouter les embeddings à l'index FAISS
            index.add(embeddings)

            current_directory = os.getcwd()
            print("Répertoire de travail actuel :", current_directory)
            # Enregistrer l'index FAISS dans un fichier
            faiss.write_index(index, "faiss_index.index")

            out_data = table_from_frame(df_concat)
            print('df_concat', df_concat.columns)
            print("Embeddings processed successfully and saved in faiss_index.index")

            self.Outputs.data_out.send(out_data)
        except Exception as e:
            print("An error occurred during embeddings processing:", str(e))


    def load_input_data(self):
        print("load input data called")
        print("self.data", self.input_data.domain)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.refresh_all()

        return super().eventFilter(source, event)

    def does_vectorstore_exist(self, db_dir: str) -> bool:
        """
        Checks if vectorstore exists
        """
        if os.path.exists(os.path.join(db_dir, 'index.faiss')) and os.path.exists(os.path.join(db_dir, 'index.pkl')):
            return True
        return False

    def show_warning_box(self, title: str, text: str):
        # Afficher une boîte de dialogue indiquant que les colonnes nécessaires sont manquantes
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec_()

    def refresh_all(self):
        print('Refreshing all')
        self.load_input_data()


if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication

    app = QApplication(sys.argv)
    mon_objet = DocumentEater()
    mon_objet.show()

    app.exec_()

