import sys
from pulp import *
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QTextEdit

class OptimizationApp(QWidget):
    def __init__(self, dados_unidades):
        super().__init__()
        self.dados_unidades = dados_unidades
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Criação de widgets
        self.label_ataque_defesa = QLabel('Deseja otimizar tropas de ataque ou defesa?')
        self.combo_ataque_defesa = QComboBox()
        self.combo_ataque_defesa.addItems(['ataque', 'defesa'])

        self.label_horas = QLabel('Quer gastar quantas horas de produção de recursos em tropas?')
        self.input_horas = QLineEdit()

        self.label_madeira = QLabel('Produção de Madeira:')
        self.input_madeira = QLineEdit()

        self.label_argila = QLabel('Produção de Argila:')
        self.input_argila = QLineEdit()

        self.label_ferro = QLabel('Produção de Ferro:')
        self.input_ferro = QLineEdit()

        self.button_executar = QPushButton('Executar Otimização')
        self.button_executar.clicked.connect(self.executar_otimizacao)

        self.resultado_texto = QTextEdit()

        # Adição de widgets ao layout
        layout.addWidget(self.label_ataque_defesa)
        layout.addWidget(self.combo_ataque_defesa)
        layout.addWidget(self.label_horas)
        layout.addWidget(self.input_horas)
        layout.addWidget(self.label_madeira)
        layout.addWidget(self.input_madeira)
        layout.addWidget(self.label_argila)
        layout.addWidget(self.input_argila)
        layout.addWidget(self.label_ferro)
        layout.addWidget(self.input_ferro)
        layout.addWidget(self.button_executar)
        layout.addWidget(self.resultado_texto)

        self.setLayout(layout)

        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle('Otimização de Recursos')
        self.show()

    def executar_otimizacao(self):
        ataque_ou_defesa = self.combo_ataque_defesa.currentText()
        horas = int(self.input_horas.text())
        producao_madeira = int(self.input_madeira.text())
        producao_argila = int(self.input_argila.text())
        producao_ferro = int(self.input_ferro.text())

        # Criação do problema de maximização
        prob = LpProblem("Otimizacao_de_Recursos", LpMaximize)

        # Restante do código para a otimização
        unidades = list(self.dados_unidades.keys())
        recrutamento = LpVariable.dicts("Recrutamento", unidades, 0, None, LpInteger)
        recrutamento_total = LpVariable("Recrutamento_Total", 0, None, LpInteger)

        if ataque_ou_defesa == "ataque":
            prob += lpSum([self.dados_unidades[u]['ataque'] * recrutamento[u] for u in unidades])
        else:
            prob += lpSum([self.dados_unidades[u]['defesa']['geral'] * recrutamento[u] +
                           self.dados_unidades[u]['defesa']['arquearia'] * recrutamento[u] +
                           self.dados_unidades[u]['defesa']['cavalaria'] * recrutamento[u]
                           for u in unidades])

        prob += lpSum([self.dados_unidades[u]['custo']['Madeira'] * recrutamento[u] for u in unidades]) <= horas * producao_madeira
        prob += lpSum([self.dados_unidades[u]['custo']['Argila'] * recrutamento[u] for u in unidades]) <= horas * producao_argila
        prob += lpSum([self.dados_unidades[u]['custo']['Ferro'] * recrutamento[u] for u in unidades]) <= horas * producao_ferro

        prob += recrutamento_total == lpSum([self.dados_unidades[u]['tempo_construcao'] * recrutamento[u] for u in unidades]), "Tempo_Total"

        for u in unidades:
            prob += recrutamento[u] <= (horas * 3600) / self.dados_unidades[u]['tempo_construcao']

        prob += lpSum([self.dados_unidades[u]['custo']['Madeira'] * recrutamento[u] for u in unidades]) <= horas * 6420
        prob += lpSum([self.dados_unidades[u]['custo']['Argila'] * recrutamento[u] for u in unidades]) <= horas * 6420
        prob += lpSum([self.dados_unidades[u]['custo']['Ferro'] * recrutamento[u] for u in unidades]) <= horas * 6420

        # Solução do problema
        status = prob.solve()

        # Limpar resultados anteriores
        self.resultado_texto.clear()

        # Adicionar resultados ao QTextEdit
        self.resultado_texto.append(f"Status: {LpStatus[status]}")

        for u in unidades:
            if recrutamento[u].varValue > 0:
                self.resultado_texto.append(f"{u}: {recrutamento[u].varValue}")

        self.resultado_texto.append(f"Madeira gasta: {value(lpSum([self.dados_unidades[u]['custo']['Madeira'] * recrutamento[u] for u in unidades]))}")
        self.resultado_texto.append(f"Argila gasta: {value(lpSum([self.dados_unidades[u]['custo']['Argila'] * recrutamento[u] for u in unidades]))}")
        self.resultado_texto.append(f"Ferro gasto: {value(lpSum([self.dados_unidades[u]['custo']['Ferro'] * recrutamento[u] for u in unidades]))}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dados_unidades = {
        'Lanceiro': {
            'custo': {'Madeira': 48, 'Argila': 29, 'Ferro': 10},
            'ataque': 10,
            'defesa': {'geral': 15, 'arquearia': 20, 'cavalaria': 45},
            'tempo_construcao': 850,
            'tipo_ataque': 'corpo a corpo'
        },
        'Espadachim': {
            'custo': {'Madeira': 29, 'Argila': 29, 'Ferro': 67},
            'ataque': 25,
            'defesa': {'geral': 50, 'arquearia': 40, 'cavalaria': 15},
            'tempo_construcao': 1250,
            'tipo_ataque': 'corpo a corpo'
        },
        'Bárbaro': {
            'custo': {'Madeira': 57, 'Argila': 29, 'Ferro': 38},
            'ataque': 40,
            'defesa': {'geral': 10, 'arquearia': 10, 'cavalaria': 5},
            'tempo_construcao': 1100,
            'tipo_ataque': 'corpo a corpo'
        },
        'Arqueiro': {
            'custo': {'Madeira': 95, 'Argila': 29, 'Ferro': 57},
            'ataque': 15,
            'defesa': {'geral': 50, 'arquearia': 5, 'cavalaria': 40},
            'tempo_construcao': 1500,
            'tipo_ataque': 'a distância'
        },
        'Cavalaria Leve': {
            'custo': {'Madeira': 119, 'Argila': 95, 'Ferro': 238},
            'ataque': 130,
            'defesa': {'geral': 30, 'arquearia': 30, 'cavalaria': 40},
            'tempo_construcao': 1500,
            'tipo_ataque': 'cavalaria'
        },
        'Arqueiro a Cavalo': {
            'custo': {'Madeira': 238, 'Argila': 95, 'Ferro': 143},
            'ataque': 120,
            'defesa': {'geral': 40, 'arquearia': 50, 'cavalaria': 30},
            'tempo_construcao': 2250,
            'tipo_ataque': 'a distância'
        }
    }
    ex = OptimizationApp(dados_unidades)
    sys.exit(app.exec_())
