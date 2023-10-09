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
                 kosten_gebinde_personal: int,
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
        self.g_r = kosten_bahnkesselwagen_r
        self.k_tr = maximale_fuellmengen_tr
        self.k_hat_r = gebindegroessen_r
        self.f_0tr = initiale_tankfuellung_tr
        self.Z = anzahl_zeitpunkte
        self.T = anzahl_tanks
        self.R = anzahl_rohstoffe
        self.p_tilde = anzahl_zeitpunkte_tankfuellung
        self.p = anzahl_zeitpunkte_reinigung

        self.__check_vars()
        self.__init_model()


    def __init_model(self):
        # initialize model
        self.model = gp.Model("chemie")

        # initialize variables
        self.y_zt = np.ndarray(shape=[self.Z, self.T], dtype=object)
        self.u_ztr = np.ndarray(shape=[self.Z, self.T, self.R], dtype=object)
        self.l_zr = np.ndarray(shape=[self.Z, self.R], dtype=object)
        self.x_tilde_ztr = np.ndarray(shape=[self.Z, self.T, self.R], dtype=object)
        self.f_ztr = np.ndarray(shape=[self.Z, self.T, self.R], dtype=object)
        self.v_ztr = np.ndarray(shape=[self.Z, self.T, self.R], dtype=object)
        self.s_zr = np.ndarray(shape=[self.Z, self.R], dtype=object)
        self.e_zr = np.ndarray(shape=[self.Z, self.R], dtype=object)
        self.lambda_zt = np.ndarray(shape=[self.Z, self.T], dtype=object)
        self.alpha_zt = np.ndarray(shape=[self.Z, self.T], dtype=object)
        self.beta_zt = np.ndarray(shape=[self.Z, self.T], dtype=object)

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
        print("Adding constraint 10")
        self.__add_constraint10()
        print("Adding constraint 12")
        self.__add_constraint12()
        print("Adding constraint 13")
        self.__add_constraint13()
        print("Adding constraint 14")
        self.__add_constraint14()
        print("Adding constraint 15")
        self.__add_constraint15()
        print("Adding constraint 21")
        self.__add_constraint21()
        print("Adding constraint 22")
        self.__add_constraint22()
        print("Adding constraint 24")
        self.__add_constraint24()
        print("Adding constraint 25")
        self.__add_constraint25()

        """print("gamma_r = ", self.gamma_r, ", gamma_hat_r = ", self.gamma_hat_r,
              self.c_hat_r, " = reinigungskosten_rohstoffgebinde_r, ",
              self.c_hat_r, "= reinigungskosten_rohstoffgebinde_r, ",
              self.c, "= kosten_tankreinigung, ",
              self.b, "= kosten_bahnkesselwagen, ",
              self.d, "= kosten_gebinde_personal, ",
              self.m_r, "= kapazitaet_bahnkesselwagen_r, ",
              self.g_r, "= kosten_bahnkesselwagen_r, ",
              self.k_tr, "= maximale_fuellmengen_tr, ",
              self.k_hat_r, "= gebindegroessen_r, ",
              self.f_0tr, "= initiale_tankfuellung_tr, ",
              self.Z, "= anzahl_zeitpunkte, ",
              self.T, "= anzahl_tanks, ",
              self.R, "= anzahl_rohstoffe, ",
              self.p_tilde, "= anzahl_zeitpunkte_tankfuellung, ",
              self.p, "= anzahl_zeitpunkte_reinigung",)
        for i in range(3):
            print(self.f_0tr[0][i])
            print(self.f_0tr[1][i])"""


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
            assert self.gamma_r[r] > 0
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
                    self.v_ztr[z, t, r] = self.model.addVar(vtype=GRB.CONTINUOUS,
                                                            name=f"v_{z}_{t}_{r}",
                                                            lb=0,
                                                            ub=1)
            for r in range(0, self.R):
                self.l_zr[z, r] = self.model.addVar(vtype=GRB.BINARY, name=f"l_{z}_{r}")
                self.s_zr[z, r] = self.model.addVar(vtype=GRB.INTEGER, lb=0, name=f"s_{z}_{r}")  # geaendert
                self.e_zr[z, r] = self.model.addVar(vtype=GRB.BINARY, name=f"e_{z}_{r}")  # geaendert

    # endregion

    # region Objective
    def __set_objective(self):
        """
        (26)
        """
        exp = LinExpr()
        # Kosten für die Reinigung, hier überall von 0 auf 1 geändert bei z
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    exp += self.y_zt[z, t] * (self.c + self.f_ztr[z - 1, t, r] * self.gamma_hat_r[r])  # änderung
        # Kosten für das Auffüllen des Tanks
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp2 = LinExpr()
                for t in range(0, self.T):
                    exp2 += self.v_ztr[z, t, r]
                exp += self.l_zr[z, r] * (self.b + exp2 * self.g_r[r])
        # Kosten für Versorgung mit Stückgut
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp += (self.gamma_r[r] * self.a_zr[z, r] +
                        (self.c_hat_r[r] + self.d) * self.s_zr[z, r]) * self.e_zr[z, r]

        #        for z in range(0, self.Z):
        #            for r in range(0, self.R):
        #                exp += self.gamma_r[r] * self.s_zr[z, r]
        #                exp += self.c_hat_r[r] * self.s_zr[z, r]
        #                for t in range(0, self.T):
        #                    exp -= self.u_ztr[z, t, r] * self.c_hat_r[r] * self.s_zr[z, r]
        self.model.setObjective(exp, GRB.MINIMIZE)

    # endregion

    # region Constraints
    def __add_constraint1(self):
        """
        (27)
        """
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.f_ztr[z, t, r] <= self.k_tr[t, r], f"C1_{z}_{t}_{r}")

    def __add_constraint2(self):
        """
        (28)
        """
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.f_ztr[z, t, r] == (
                            self.f_ztr[z - 1, t, r]
                            - self.a_zr[z, r] * self.u_ztr[z, t, r]
                            + self.v_ztr[z, t, r] * self.m_r[r])
                                         * (1 - self.y_zt[z, t]),
                                         f"C2_{z}_{t}_{r}")

    def __add_constraint3(self):
        """
        (29)
        """
        for z in range(1, self.Z):
            for r in range(0, self.R):
                exp = LinExpr()
                for t in range(0, self.T):
                    exp += self.v_ztr[z, t, r]

                    self.model.addConstr(exp <= self.l_zr[z, r], f"C3_{z}_{r}")  # ab hier: geänderrt

    def __add_constraint4(self):
        """
        (30)
        """
        for z in range(1, self.Z):
            for t in range(0, self.T):
                exp = LinExpr()
                for n in range(max(z - self.p, 1), z): #geändert
                    exp += self.y_zt[n, t]

                self.model.addConstr(self.y_zt[z - 1, t] * (exp - self.p) + self.p * self.y_zt[z, t] >= 0,
                                     f"C4_{z}_{t}")

    def __add_constraint5(self):

        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    #self.model.addConstr(self.v_ztr[z, t, r] <= self.x_tilde_ztr[z, t, r], f"C5_{z}_{t}_{r}")
                    self.model.addConstr(self.v_ztr[z, t, r] <= self.u_ztr[z, t, r], f"C5_{z}_{t}_{r}")

    def __add_constraint6(self):
        for z in range(1, self.Z):
            for r in range(0, self.R):
                self.model.addConstr(self.l_zr[z, r] + self.e_zr[z, r] <= 1, f"C6_{z}_{r}")

    def __add_constraint7(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.y_zt[z, t] + self.u_ztr[z, t, r] <= 1, f"C7_{z}_{t}_{r}")

    """def __add_constraint8(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.y_zt[z, t] + self.x_tilde_ztr[z, t, r] <= 1, f"C8_{z}_{t}_{r}")

    def __add_constraint9(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.e_zr[z, r] + self.x_tilde_ztr[z, t, r] <= 1, f"C9_{z}_{t}_{r}")"""

    def __add_constraint10(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.e_zr[z, r] + self.u_ztr[z, t, r] <= 1, f"C10_{z}_{t}_{r}")

    """def __add_constraint11(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                exp = LinExpr()
                for r in range(0, self.R):
                    exp += self.x_tilde_ztr[z, t, r]

                self.model.addConstr(exp <= 1, f"C11_{z}_{t}")"""

    def __add_constraint12(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                exp = LinExpr()
                for r in range(0, self.R):
                    exp += self.u_ztr[z, t, r]

                self.model.addConstr(exp <= 1, f"C12_{z}_{t}")

    def __add_constraint13(self):
        for z in range(1, self.Z):
            exp = LinExpr()
            for r in range(0, self.R):
                exp += self.l_zr[z, r]

            self.model.addConstr(exp <= 1, f"C13_{z}")

    def __add_constraint14(self):
        """
        (36)
        """
        for z in range(1, self.Z):
            for r in range(0, self.R):
                self.model.addConstr(self.s_zr[z, r] >= self.e_zr[z, r] * (self.a_zr[z, r] / self.k_hat_r[r]), f"C14_{z}_{r}")

    def __add_constraint15(self):
        """
        (41)
        """
        for z in range(1, self.Z):
            for r in range(0, self.R):
                exp = LinExpr()
                for t in range(0, self.T):
                    exp += self.f_ztr[z, t, r]
                self.model.addConstr((exp * (1 - self.e_zr[z, r])) + (self.a_zr[z, r] * self.e_zr[z, r]) >=
                                     self.a_zr[z, r], f"C15_{z}_{r}")

    """def __add_constraint16(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.x_tilde_ztr[z, t, r] <= self.u_ztr[z, t, r], f"C16_{z}_{t}_{r}")"""

    def __add_constraint17(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                self.model.addConstr(self.alpha_zt[z, t] ==
                                     max_(self.lambda_zt[z - 1, t], self.y_zt[z - 1, t]), f"C17_{z}_{t}")

    def __add_constraint18(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                exp = LinExpr()
                for r in range(0, self.R):
                    #exp += self.x_tilde_ztr[z - 1, t, r]
                    exp += self.u_ztr[z - 1, t, r] #hier -1 weg
                self.model.addConstr(self.beta_zt[z, t] == self.alpha_zt[z, t] - exp, f"C18_{z}_{t}")

    def __add_constraint19(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.lambda_zt[z, t] == max_(self.beta_zt[z, t], 0), f"C19_{z}_{t}")

    def __add_constraint20(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    #self.model.addConstr(self.x_tilde_ztr[z, t, r] <=
                    #                     self.x_tilde_ztr[z - 1, t, r] + self.g_zt[z - 1, t], f"C20_{z}_{t}")
                    self.model.addConstr(self.u_ztr[z, t, r] <=
                                         self.u_ztr[z - 1, t, r] + self.lambda_zt[z, t], f"C20_{z}_{t}")

    def __add_constraint21(self):
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    #self.model.addConstr(self.x_tilde_ztr[z, t, r] >= self.f_ztr[z, t, r]/1000000, f"C21_{z}_{t}_{r}")
                    self.model.addConstr(self.u_ztr[z, t, r] >= self.f_ztr[z, t, r] / 1000000, f"C21_{z}_{t}_{r}")

    def __add_constraint22(self):
        for z in range(1, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr((self.u_ztr[z, t, r]) <= self.u_ztr[z - 1, t, r] + self.y_zt[z - 1, t], f"C22_{z}_{t}_{r}")

    def __add_constraint24(self):
        for t in range(0, self.T):
            for r in range(0, self.R):
                self.model.addConstr(self.f_ztr[0, t, r] == self.f_0tr[t][r], f"C24_{t}_{r}")

    def __add_constraint25(self):
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp = LinExpr()
                for t in range(0, self.T):
                    exp += self.u_ztr[z, t, r]
                self.model.addConstr(exp <= 5, f"C25_{z}_{r}")


    """def __add_constraint22(self):
        for t in range(0, self.T):
            self.model.addConstr(self.g_zt[0, t] == 0, f"C22_{t}")

    def __add_constraint23(self):
        for t in range(0, self.T):
            self.model.addConstr(self.y_zt[0, t] == 0, f"C23_{t}")

    def __add_constraint24(self):
        for t in range(0, self.T):
            for r in range(0, self.R):
                self.model.addConstr(self.f_ztr[0, t, r] == self.f_0tr[t, r], f"C24_{t}_{r}")

    def __add_constraint25(self):
        for t in range(0, self.T):
            for r in range(0, self.R):
                self.model.addConstr(self.x_tilde_ztr[0, t, r] >= self.f_ztr[0, t, r]/10000000, f"C25_{t}_{r}")
        self.g_zt[0, 0] = 0
        self.g_zt[0, 1] = 0
        self.y_zt[0, 1] = 0
        self.y_zt[0, 0] = 0
        self.x_tilde_ztr[0, 0, 0] = 0
        self.x_tilde_ztr[0, 1, 0] = 0
        self.x_tilde_ztr[0, 0, 1] = 1
        self.x_tilde_ztr[0, 1, 1] = 0
        self.x_tilde_ztr[0, 0, 2] = 0
        self.x_tilde_ztr[0, 1, 2] = 1"""


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
            self.model.setParam('TimeLimit', 60 * time_limit)
            self.model.setParam('NonConvex', 2)
            self.model.optimize()
            for i in range(self.model.SolCount):
                self.model.Params.SolutionNumber = i
                self.model.write(f"{i}.sol")
            self.save_results()

        except gp.GurobiError as e:
            # noinspection PyUnresolvedReferences
            print('Error code ' + str(e.errno) + ': ' + str(e))

        except AttributeError:
            print('Encountered an attribute error')