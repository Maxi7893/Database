import numpy as np
from _decimal import Decimal


class Recursion:

    def __init__(self,
                 auftraege,
                 tankbelegung_anfang,
                 endzeitpunkt,
                 anzahl_tanks,
                 kann_in_tank,
                 kapa_tanks,
                 abfallpreis_gebinde,
                 kosten_nachladen,
                 kosten_tankreinigung,
                 kosten_abfallentsorgung,
                 kosten_tankleerung_pro_einheit,
                 reinigungszeit):
        self.auftraege = auftraege
        self.tankbelegung_anfang = tankbelegung_anfang
        self.endzeitpunkt = endzeitpunkt
        self.anzahl_tanks = anzahl_tanks
        self.kann_in_tank = kann_in_tank
        self.kapa_tanks = kapa_tanks
        self.abfallpreis_gebinde = abfallpreis_gebinde
        self.kosten_nachladen = kosten_nachladen
        self.kosten_tankreinigung = kosten_tankreinigung
        self.kosten_abfallentsorgung = kosten_abfallentsorgung
        self.kosten_tankleerung_pro_einheit = kosten_tankleerung_pro_einheit
        self.reinigungszeit = reinigungszeit

    def run(self):
        search_history = 1
        best_search_history = [0]
        best = [99999999999]

        self.__rekursion(self.auftraege,
                         self.tankbelegung_anfang,
                         search_history,
                         0,
                         0,
                         best,
                         best_search_history)

        self.__interpret_history(best_search_history[0], self.endzeitpunkt)

    def __rekursion(self, auftraege, tankbelegung, history, zeitpunkt, zielfunktion, best_val, best_history):
        if zeitpunkt == self.endzeitpunkt:
            if zielfunktion < best_val[0]:
                best_val[0] = zielfunktion
                print('Verbesserung: ' + str(best_val[0]))
                # print(History)
                best_history[0] = history
            return best_val[0], best_history

        if zielfunktion > best_val[0]:  # cutte Äste
            return

        else:
            # kein Tank Option 0
            # langsam aber klappt
            self.__rekursion(auftraege,
                             tankbelegung,
                             history * 100,
                             zeitpunkt + 1,
                             zielfunktion + abs(auftraege[zeitpunkt][2]) * self.abfallpreis_gebinde,
                             best_val,
                             best_history)
            for i in range(self.anzahl_tanks):
                kann_in_tank_i = False
                for j in range(np.shape(self.kann_in_tank[i])[0]):
                    if int(self.kann_in_tank[i][j]) == auftraege[zeitpunkt][0]:
                        kann_in_tank_i = True

                if kann_in_tank_i:
                    temp1 = tankbelegung[i][1]
                    temp2 = tankbelegung[i][2]
                    tankbelegung[i][2] = zeitpunkt  # Tank wird jetzt benutzt

                    if tankbelegung[i][0] == auftraege[zeitpunkt][0]:  # Rohstoff ist schon im Tank
                        tankbelegung[i][1] -= auftraege[zeitpunkt][1]

                        if tankbelegung[i][1] < 0:  # voll machen
                            tankbelegung[i][1] += self.kapa_tanks[i]
                            self.__rekursion(auftraege, tankbelegung, history * 100 + 40 + i, zeitpunkt + 1,
                                             zielfunktion + self.kosten_nachladen, best_val, best_history)

                        elif tankbelegung[i][1] > self.kapa_tanks[i]:  # Abfall überschüttet Tank
                            tankbelegung[i][1] -= self.kapa_tanks[i]
                            self.__rekursion(auftraege,
                                             tankbelegung,
                                             history * 100 + 2,
                                             zeitpunkt + 1,
                                             zielfunktion + self.kosten_abfallentsorgung,
                                             best_val,
                                             best_history)

                        else:
                            self.__rekursion(auftraege,
                                             tankbelegung,
                                             history * 100 + 10 + i,
                                             zeitpunkt + 1,
                                             zielfunktion,
                                             best_val,
                                             best_history)
                    elif zeitpunkt - tankbelegung[i][2] > self.reinigungszeit:  # kann der schon gereinigt werden
                        if auftraege[zeitpunkt][1] > 0:
                            tankbelegung[i][1] = self.kapa_tanks - auftraege[zeitpunkt][1]

                        else:  # Abfall
                            tankbelegung[i][1] = auftraege[zeitpunkt][1]
                        self.__rekursion(auftraege,
                                         tankbelegung, history * 100 + i + 70, zeitpunkt + 1,
                                         zielfunktion
                                         + self.kosten_tankreinigung
                                         + self.kosten_tankleerung_pro_einheit * temp1,
                                         best_val,
                                         best_history)
                    tankbelegung[i][1] = temp1
                    tankbelegung[i][2] = temp2

    def __interpret_history(self, history, zeitpunkt):
        """
        History:
        * 10-39 nutze Tank
        * 40-69 fülle auf und nutze Tank
        * 70-99 reinige Tank vor 30 und nutze ihn jetzt
        * 0 nutze Gebinde
        """
        temp = []
        for i in range(zeitpunkt):
            temp.append(history % 100)
            history -= temp[i]
            history = Decimal(history) / Decimal(100)

        for i in range(zeitpunkt):
            if temp[zeitpunkt - 1 - i] == 0:
                print(str(i) + ': Nutze Gebinde.')

            if temp[zeitpunkt - 1 - i] == 2:
                print(str(i) + ': Abfall wird in einen Tank geschüttet der überläuft und daher direkt geleert wird.')

            if temp[zeitpunkt - 1 - i] >= 10:
                if temp[zeitpunkt - 1 - i] >= 40:
                    if temp[zeitpunkt - 1 - i] >= 70:
                        print(str(i) + ': Reinige Tank ' + str(int(temp[zeitpunkt - 1 - i] - 70)) + ' vor ' + str(
                            self.reinigungszeit) + ' Tagen, fülle ihn und nutze ihn direkt.')
                    else:
                        print(str(i) + ': Fülle Tank ' + str(
                            int(temp[zeitpunkt - 1 - i] - 40)) + ' auf und nutze ihn direkt.')
                else:
                    print(str(i) + ': Nutze Tank ' + str(int(temp[zeitpunkt - 1 - i] - 10)) + '.')
