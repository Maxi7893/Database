import numpy as np
import gurobipy as gp
import pandas as pd
from gurobipy import GRB, LinExpr, max_


# noinspection DuplicatedCode,SpellCheckingInspection
class LP:
    def __init__(self,
                 rohstoffkosten_r: np.ndarray,
                 abfallkosten_r: np.ndarray,
                 reinigungskosten_rohstoffgebinde_r: np.ndarray,
                 kosten_tankreinigung: int,
                 kosten_bahnkesselwagen: int,
                 Container_oder_Stationär:int,
                 kosten_gebinde_personal: float,
                 kapazitaet_bahnkesselwagen_r: np.ndarray,
                 auftraege_zr: np.ndarray,
                 kosten_bahnkesselwagen_r: np.ndarray,
                 maximale_fuellmengen_tr: np.ndarray,
                 gebindegroessen_r: np.ndarray,
                 initiale_tankfuellung_tr: np.ndarray,
                 anzahl_zeitpunkte: int,
                 anzahl_tanks: int,
                 anzahl_rohstoffe: int,
                 anzahl_zeitpunkte_tankfuellung: int,
                 anzahl_zeitpunkte_reinigung: int):
        """
        Initialisierer für das LP. Alle ndarrays müssen in der Reihenfolge der Subscripts indiziert werden, d.h. z.B.
        initiale_tankfuellung_tr wird in der ersten Dimension mit dem Tank und in der zweiten Dimension mit dem
        Rohstoff indiziert. initiale_tankfuellung_tr[2,5] indiziert Tank 2 mit Rohstoff 5. Die Größe des ndarrays
        ergibt sich als T x R bzw 'anzahl_tanks' x 'anzahl_rohstoffe'. Alle Indizees folgen derselben Reihenfolge
        z -> t -> r.


        :param rohstoffkosten_r: Kosten für Rohstoffe.
        :param abfallkosten_r: Kosten für Abfall.
        :param reinigungskosten_rohstoffgebinde_r: Kosten für Rohstoffgebinde r bei Reinigung.
        :param kosten_tankreinigung: Kosten für Reinigung.
        :param kosten_bahnkesselwagen: Kosten pro Bahnkesselwagen (Fixkosten).
        :param kosten_gebinde_personal: Personalkosten für die Bereitstellung via Stückgut (Fixkosten)
        :param kapazitaet_bahnkesselwagen_r: Kapazität Bahnkesselwagen für Rohstoff r.
        :param auftraege_zr: Benötigte Menge von Rohstoff r zum Zeitpunkt z.
        :param kosten_bahnkesselwagen_r: Kosten pro Bahnkesselwagen für Rohstoff r.
        :param maximale_fuellmengen_tr: Maximale Füllmenge von Tank t mit Rohstoff r.
        :param gebindegroessen_r: Gebindegröße für Rohstoff r.
        :param initiale_tankfuellung_tr: Initialer Füllstand von Tank t mit Rohstoff r.
        :param anzahl_zeitpunkte: Anzahl Zeitpunkte.
        :param anzahl_tanks: Anzahl Tanks.
        :param anzahl_rohstoffe: Anzahl verschiedener Rohstoffe.
        :param anzahl_zeitpunkte_tankfuellung: Anzahl benötigter Zeitpunkte (Zeitschlitze) zum Auffüllen von Tanks.
        :param anzahl_zeitpunkte_reinigung: Anzahl benötigter Zeitpunkte, benötigt für Reinigung von Tanks.
        """
        self.gamma_r = rohstoffkosten_r
        self.gamma_hat_r = abfallkosten_r
        self.c_hat_r = reinigungskosten_rohstoffgebinde_r
        self.c = kosten_tankreinigung
        self.b = kosten_bahnkesselwagen
        self.d = kosten_gebinde_personal
        self.m_r = kapazitaet_bahnkesselwagen_r
        self.a_zr = auftraege_zr
        #for a in range(0, anzahl_rohstoffe):
        #    for i in range(1, 815):
        #        self.a_zr[i, a] = 0
        #for a in [2, 3, 5, 7, 11]:
       #for i in range(1, 815):
        #    if i <= 800:
         #       self.a_zr[i, 2] = 0
        #            self.a_zr[i, a] = 1000
        #        elif i <= 500:
        #            self.a_zr[i, a] = 1000
        #            self.a_zr[i, 11] = 0
        #        else:
        #            self.a_zr[i, a] = 1000
        #            self.a_zr[i, 7] = 0
        self.g_r = kosten_bahnkesselwagen_r
        self.k_tr = maximale_fuellmengen_tr
        self.k_hat_r = gebindegroessen_r
        self.f_0tr = initiale_tankfuellung_tr
        self.Z = anzahl_zeitpunkte
        self.T = anzahl_tanks
        self.R = anzahl_rohstoffe
        self.p_tilde = anzahl_zeitpunkte_tankfuellung #wird nicht benutzt, kann aber bei Bedarf noch benutzt werden
        self.p = anzahl_zeitpunkte_reinigung
        self.sigma = Container_oder_Stationär #Wurde hinzugefügt 1 bei Tankcontainern und bspw. 20 bei stationären Tanks
        self.__check_vars()
        self.__init_model()


    def __init_model(self):
        # initialize model
        self.model = gp.Model("chemie")

        # initialize variables
        self.y_zt = np.ndarray(shape=[self.Z, self.T], dtype=object)
        self.u_ztr = np.ndarray(shape=[self.Z, self.T, self.R], dtype=object)
        self.l_zr = np.ndarray(shape=[self.Z, self.R], dtype=object)
        self.x_tilde_ztr = np.ndarray(shape=[self.Z, self.T, self.R], dtype=object) #wird nicht benutzt, könnte rausgenommen werden
        self.f_ztr = np.ndarray(shape=[self.Z, self.T, self.R], dtype=object)
        self.v_ztr = np.ndarray(shape=[self.Z, self.T, self.R], dtype=object)
        self.s_zr = np.ndarray(shape=[self.Z, self.R], dtype=object)
        self.e_zr = np.ndarray(shape=[self.Z, self.R], dtype=object)
        self.lambda_zt = np.ndarray(shape=[self.Z, self.T], dtype=object) #wird nicht benutzt, könnte später rausgenommen werden
        self.alpha_zt = np.ndarray(shape=[self.Z, self.T], dtype=object) #wird nicht benutzt, könnte später rausgenommen werden
        self.beta_zt = np.ndarray(shape=[self.Z, self.T], dtype=object) #wird nicht benutzt, könnte später rausgenommen werden

        # set up variables, objective and constraints
        print("Adding variables")
        self.__add_vars()
        print("Setting objective")
        self.__set_objective()
        print("Adding constraint 1")
        self.__add_constraint1()
        print("Adding constraint 2")
        self.__add_constraint2()
        print("Adding constraint 3")
        self.__add_constraint3()
        print("Adding constraint 4")
        self.__add_constraint4()
        print("Adding constraint 5")
        self.__add_constraint5()
        print("Adding constraint 6")
        self.__add_constraint6()
        print("Adding constraint 7")
        self.__add_constraint7()
        print("Adding constraint 8")
        self.__add_constraint8()
        print("Adding constraint 9")
        self.__add_constraint9()
        print("Adding constraint 10")
        self.__add_constraint10()
        print("Adding constraint 11")
        self.__add_constraint11()
        print("Adding constraint 12")
        self.__add_constraint12()
        print("Adding constraint 13")
        self.__add_constraint13()
        print("Adding constraint 14")
        self.__add_constraint14()
        #print("Adding constraint 15")
        #self.__add_constraint15()
        print("Adding constraint 16")
        self.__add_constraint16()
        print("Adding constraint 17")
        self.__add_constraint17()
        """     
        print("Adding constraint 18")
        self.__add_constraint18()
        print("Adding constraint 19")
        self.__add_constraint19()
        print("Adding constraint 20")
        self.__add_constraint20()"""


    # region Variables
    def __check_vars(self):
        assert self.Z > 0
        assert self.T > 0
        assert self.R > 0
        assert self.c >= 0
        assert self.b >= 0
        assert self.d >= 0
        assert self.p_tilde > 0
        assert self.p > 0
        assert self.sigma > 0 #hinzugefügt


        assert len(self.gamma_r) == self.R
        assert len(self.gamma_hat_r) == self.R
        assert len(self.c_hat_r) == self.R
        assert len(self.m_r) == self.R
        assert len(self.g_r) == self.R
        assert len(self.k_hat_r) == self.R

        assert len(self.a_zr) == self.Z
        assert len(self.a_zr[0]) == self.R

        assert len(self.k_tr) == self.T
        assert len(self.k_tr[0]) == self.R

        assert len(self.f_0tr) == self.T
        assert len(self.f_0tr[0]) == self.R

        for r in range(self.R):
            assert self.gamma_r[r] >= 0 #geändert, da Rohstoffpreise für Abfälle = 0 sind!
            assert self.gamma_hat_r[r] >= 0
            assert self.c_hat_r[r] >= 0
            assert self.m_r[r] > 0
            assert self.g_r[r] >= 0
            assert self.k_hat_r[r] > 0

    # noinspection PyArgumentList
    def __add_vars(self):
        for z in range(0, self.Z):   #Hier auf 1 geändert
            for t in range(0, self.T):
                self.y_zt[z, t] = self.model.addVar(vtype=GRB.BINARY, name=f"y_{z}_{t}")
                self.lambda_zt[z, t] = self.model.addVar(vtype=GRB.BINARY, name=f"g_{z}_{t}")
                self.alpha_zt[z, t] = self.model.addVar(vtype=GRB.BINARY, name=f"alpha_{z}_{t}")
                self.beta_zt[z, t] = self.model.addVar(vtype=GRB.BINARY, name=f"beta_{z}_{t}")

                for r in range(0, self.R):
                    self.u_ztr[z, t, r] = self.model.addVar(vtype=GRB.BINARY,
                                                            name=f"u_{z}_{t}_{r}")
                    self.x_tilde_ztr[z, t, r] = self.model.addVar(vtype=GRB.BINARY,
                                                                  name=f"x_tilde_{z}_{t}_{r}")
                    self.f_ztr[z, t, r] = self.model.addVar(vtype=GRB.CONTINUOUS,
                                                            name=f"f_{z}_{t}_{r}",
                                                            lb=0,
                                                            ub=self.k_tr[t, r])
                    self.v_ztr[z, t, r] = self.model.addVar(vtype=GRB.INTEGER,   ##hier und folgend 1/20 für 5% Schritte von v_ztr --> CONTINUOUS
                                                            name=f"v_{z}_{t}_{r}",
                                                            lb=0,
                                                            ub=self.sigma) #20 wurde in Sigma geändert!
            for r in range(0, self.R):
                self.l_zr[z, r] = self.model.addVar(vtype=GRB.BINARY, name=f"l_{z}_{r}")
                self.s_zr[z, r] = self.model.addVar(vtype=GRB.INTEGER, lb=0, name=f"s_{z}_{r}")  # geaendert
                self.e_zr[z, r] = self.model.addVar(vtype=GRB.BINARY, name=f"e_{z}_{r}")  # geaendert

    # endregion

    # region Objective
    def __set_objective(self):
        exp = LinExpr()
        # Kosten für die Reinigung
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    exp += self.y_zt[z, t] * (self.c + self.f_ztr[z - 1, t, r] * self.gamma_hat_r[r])  # änderung
        # Kosten für das Auffüllen des Tanks
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp2 = LinExpr()
                for t in range(0, self.T):
                    exp2 += self.v_ztr[z, t, r] * (1/self.sigma) #hier und folgend 1/20 für 5% Schritte von v_ztr, self.sigma wurde durch 1/20 ersetzt
                exp += self.l_zr[z, r] * (self.b + exp2 * self.g_r[r])
        # Kosten für Versorgung mit Stückgut
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp += (self.gamma_r[r] * self.a_zr[z, r] +
                        (self.c_hat_r[r] + self.d) * self.s_zr[z, r]) * self.e_zr[z, r]

        self.model.setObjective(exp, GRB.MINIMIZE)

    # endregion

    # region Constraints
    def __add_constraint1(self):
        """
        (1) - Rohstoffmenge im Tank ist auf die Kapazität des Tanks begrenzt
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.f_ztr[z, t, r] <= self.k_tr[t, r], f"C1_{z}_{t}_{r}")

    def __add_constraint2(self):
        """
        (2) Der aktuelle Tankfüllstand berechnet sich aus dem vorherigem Füllstand minus dem Verbrauch plus dem Anteil,
         wenn aufgefüllt wird
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.f_ztr[z, t, r] == (
                            self.f_ztr[z - 1, t, r]
                            - self.a_zr[z, r] * self.u_ztr[z, t, r]
                            + self.v_ztr[z, t, r] * self.m_r[r]* (1/self.sigma)) * (1 - self.y_zt[z, t]), f"C2_{z}_{t}_{r}")
                                                                    #hier und folgend 1/20 für 5% Schritte von v_ztr

    def __add_constraint3(self):
        """
        (3) - Es kann nur ein Bahnkesselwagen mit einem Rohstoff kommen
        """
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp = LinExpr()
                for t in range(0, self.T):
                    exp += self.v_ztr[z, t, r] * (1/self.sigma) #hier und folgend 1/20 für 5% Schritte von v_ztr

                    self.model.addConstr(exp <= self.l_zr[z, r], f"C3_{z}_{r}")  # ab hier: geänderrt

    def __add_constraint4(self):
        """
        (4) - Reinigungsdauer der Tanks wird sichergestellt: sobald sich zu einem Zeitpunkt auf eine Reinigung
         festgelegt wurde, muss auch in den folgenden Zeitpunkten gereinigt werden bis die vorgegebene
         Reinigungsdauer beendet ist
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                exp = LinExpr()
                for n in range(max(z - self.p, 1), z): #geändert
                    exp += self.y_zt[n, t]
                self.model.addConstr(self.y_zt[z - 1, t] * (exp - self.p) + self.p * self.y_zt[z, t] >= 0,
                                     f"C4_{z}_{t}")

    def __add_constraint5(self):
        """
        (5) - Bahnkesselwagen kann nur zum Tank kommen, wenn die Rohstoffe in Tank und Bahnkesselwagen übereinstimmen
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.v_ztr[z, t, r] * (1/self.sigma) <= self.u_ztr[z, t, r], f"C5_{z}_{t}_{r}") #1/20 für 5% Schritte von v_ztr

    def __add_constraint6(self):
        """
        (6) - Gebinde und Bahnkesselwagen werden nicht zusammen verwendet
        """
        for z in range(0, self.Z):
            for r in range(0, self.R):
                self.model.addConstr(self.l_zr[z, r] + self.e_zr[z, r] <= 1, f"C6_{z}_{r}")

    def __add_constraint7(self):
        """
        (7) - Wenn ein Tank gereinigt wird, kann er nicht für Rohstoffaufbewahrung benutzt werden
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.y_zt[z, t] + self.u_ztr[z, t, r] <= 1, f"C7_{z}_{t}_{r}")


    def __add_constraint8(self):
        """
        (8) - Für einen Rohstoff kann nicht gleichzeitig der Tank und Stückgut verwendet werden
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.e_zr[z, r] + self.u_ztr[z, t, r] <= 1, f"C8_{z}_{t}_{r}")


    def __add_constraint9(self):
        """
        (9) - Tank nur mit einem Rohstoff pro Zeitintervall
        """
        for z in range(0, self.Z): #geaendert von 1 auf 0
            for t in range(0, self.T):
                exp = LinExpr()
                for r in range(0, self.R):
                    exp += self.u_ztr[z, t, r]
                self.model.addConstr(exp <= 1, f"C9_{z}_{t}")

    def __add_constraint10(self):
        """
        (10) - Bahnkesselwagen kann nur mit einem Rohstoff gleichzeitig kommen
        """
        for z in range(0, self.Z):
            exp = LinExpr()
            for r in range(0, self.R):
                exp += self.l_zr[z, r]
            self.model.addConstr(exp <= 1, f"C10_{z}")

    def __add_constraint11(self):
        """
        (11)- Anzahl an Gebinden berechnet sich aus Auftragsmenge und Behälterkapazität, wenn Stückgut verwendet wird
        """
        for z in range(0, self.Z):
            for r in range(0, self.R):
                self.model.addConstr(self.s_zr[z, r] >= self.e_zr[z, r] * (self.a_zr[z, r] / self.k_hat_r[r]),
                                     f"C11_{z}_{r}")

    def __add_constraint12(self):
        """
        (12) - Es muss immer genug Rohstoff vorhanden sein, um die Auftragsmenge zu bedienen
        """
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp = LinExpr()
                for t in range(0, self.T):
                    exp += self.f_ztr[z, t, r]
                self.model.addConstr((exp * (1 - self.e_zr[z, r])) + (self.a_zr[z, r] * self.e_zr[z, r]) >=
                                     self.a_zr[z, r], f"C12_{z}_{r}")


    def __add_constraint13(self):
        """
        (13) - Wenn ein Rohstoff zu einem Zeitpunkt im Tank ist, dann wird der Tank auch für den Rohstoff benutzt
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.u_ztr[z, t, r] >= self.f_ztr[z, t, r] / 1000000, f"C13_{z}_{t}_{r}")

    def __add_constraint14(self):
        """
        (14) - Nachdem ein Rohstoff im Tank war, muss gereinigt werden, bevor ein neuer Rohstoff in den Tank kann
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr((self.u_ztr[z, t, r]) <= self.u_ztr[z - 1, t, r] + self.y_zt[z - 1, t],
                                         f"C14_{z}_{t}_{r}")

    def __add_constraint15(self):
        """
        (15): Anfangsbestand in Tanks wird überschrieben auf Variable, die den Tankfüllstand angibt
        """
        for t in range(0, self.T):
            for r in range(0, self.R):
                self.model.addConstr(self.f_ztr[0, t, r] == self.f_0tr[t][r], f"C15_{t}_{r}")


    def __add_constraint16(self):
        """
        (16) - optional: Ein Rohstoff kann in maximal 5 (kann aber auch beliebig verändert werden) verschiedenen
        Tanks gleichzeitig sein
        """
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp = LinExpr()
                for t in range(0, self.T):
                    exp += self.u_ztr[z, t, r]
                self.model.addConstr(exp <= 1, f"C16_{z}_{r}")

    def __add_constraint17(self):
        """
        (17) - optional: Es sollen alle Tanks benutzt oder gerade gereinigt werden
        """
        for z in range(0, self.Z):
            exp = LinExpr()
            for t in range(0, self.T):
                exp += self.y_zt[z, t]
                for r in range(0, self.R):
                    exp += self.u_ztr[z, t, r]
            self.model.addConstr(exp >= self.T+1, f"C17_{z}") #Nur für die Optimierung, da == self.T nicht wechselt bzw. reinigt!


    def save_results(self):
        a_zr = np.ndarray(shape=[self.Z, self.R])
        y_zt = np.ndarray(shape=[self.Z, self.T])
        u_ztr = np.ndarray(shape=[self.Z, self.T, self.R])
        e_zr = np.ndarray(shape=[self.Z, self.R])
        l_zr = np.ndarray(shape=[self.Z, self.R])
        x_tilde_ztr = np.ndarray(shape=[self.Z, self.T, self.R])
        f_ztr = np.ndarray(shape=[self.Z, self.T, self.R])
        s_zr = np.ndarray(shape=[self.Z, self.R])

        for z in range(1, self.Z):
            for t in range(0, self.T):
                y_zt[z, t] = self.y_zt[z, t].X

                for r in range(0, self.R):
                    u_ztr[z, t, r] = self.u_ztr[z, t, r].X
                    x_tilde_ztr[z, t, r] = self.x_tilde_ztr[z, t, r].X
                    f_ztr[z, t, r] = self.f_ztr[z, t, r].X

            for r in range(0, self.R):
                l_zr[z, r] = self.l_zr[z, r].X
                s_zr[z, r] = self.s_zr[z, r].X
                e_zr[z, r] = self.e_zr[z, r].X
                a_zr[z, r] = self.a_zr[z, r].X
        # endregion


    def run(self, time_limit: int):
        """
        Runs the optimization.
        :param time_limit: Time limit in minutes.
        """
        try:
            self.model.setParam('TimeLimit', 60 * time_limit) # vielleicht mal hiermit arbeiten; setze das Timelimit auf eine Woche o.ä.
            self.model.setParam('NonConvex', 2) # passt
            self.model.optimize()
            # Hier fehlt die Speicherung der besten Lösung! --> Nein

            for i in range(self.model.SolCount): # passt das so zu machen: wenn man interrupted ist das, als würde ein TimeLimit erreicht, daher okay!
                self.model.Params.SolutionNumber = i # passt
                self.model.write(f"{i}.sol") # passt, aber irgendwie sinnlos?
            self.save_results() # passt

        except gp.GurobiError as e:
            # noinspection PyUnresolvedReferences
            print('Error code ' + str(e.errno) + ': ' + str(e))

        except AttributeError:
            print('Encountered an attribute error')