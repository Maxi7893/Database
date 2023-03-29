import numpy as np
import gurobipy as gp
import pandas as pd
from gurobipy import GRB, LinExpr


# noinspection DuplicatedCode,SpellCheckingInspection
class LP:
    def __init__(self,
                 rohstoffkosten_r: np.ndarray,
                 abfallkosten_r: np.ndarray,
                 reinigungskosten_rohstoffgebinde_r: np.ndarray,
                 kosten_tankreinigung: int,
                 kosten_bahnkesselwagen: int,
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
        Rohstoff indiziert. initiale_tankfuellung_tr[2,5] indiziert Tank 2 mit Rohstoff 5. Die größe des ndarrays
        ergibt sich als T x R bzw 'anzahl_tanks' x 'anzahl_rohstoffe'. Alle Indizees folgen derselben Reihenfolge
        z -> t -> r.


        :param rohstoffkosten_r: Kosten für Rohstoffe.
        :param abfallkosten_r: Kosten für Abfall.
        :param reinigungskosten_rohstoffgebinde_r: Kosten für Rohstoffgebinde r bei Reinigung.
        :param kosten_tankreinigung: Kosten für Reinigung.
        :param kosten_bahnkesselwagen: Kosten pro Bahnkesselwagen (Fixkosten).
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
        self.gamma_r = rohstoffkosten_r  # TODO: r
        self.gamma_hat_r = abfallkosten_r  # TODO: r
        self.c_hat_r = reinigungskosten_rohstoffgebinde_r
        self.c = kosten_tankreinigung
        self.b = kosten_bahnkesselwagen
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

        # set up variables, objective and constraints
        self.__add_vars()
        self.__set_objective()
        self.__add_constraint1()
        self.__add_constraint2()
        self.__add_constraint3()
        self.__add_constraint4()
        self.__add_constraint5()
        self.__add_constraint6()
        self.__add_constraint7()
        self.__add_constraint8()
        self.__add_constraint9()
        # self.__add_constraint10()

    # region Variables
    def __check_vars(self):
        assert self.Z > 0
        assert self.T > 0
        assert self.R > 0
        assert self.c >= 0
        assert self.b >= 0
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
        for z in range(0, self.Z):
            for t in range(0, self.T):
                self.y_zt[z, t] = self.model.addVar(vtype=GRB.BINARY, name=f"y_{z}_{t}")

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
                self.s_zr[z, r] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"s_{z}_{r}")

    # endregion

    # region Objective
    def __set_objective(self):
        """
        (23)
        """
        exp = LinExpr()

        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    exp += self.y_zt[z, t] * (self.c + self.f_ztr[z, t, r] * self.gamma_hat_r[r])

        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp += self.l_zr[z, r] * self.b
                for t in range(0, self.T):
                    exp += self.l_zr[z, r] * self.v_ztr[z, t, r] * self.g_r[r]

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
        (24) 26
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.f_ztr[z, t, r] <= self.k_tr[t, r], f"C1_{z}_{t}_{r}")

    def __add_constraint2(self):
        """
        (25)
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.f_ztr[z, t, r] == (
                            self.f_ztr[z - 1, t, r]
                            - (self.a_zr[z, r] * self.u_ztr[z, t, r])
                            + self.v_ztr[z, t, r] * self.m_r[r])
                                         * (1 - self.y_zt[z, t]),
                                         f"C2_{z}_{t}_{r}")

    def __add_constraint3(self):
        """
        (26)
        """
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp = LinExpr()
                for t in range(0, self.T):
                    exp += self.v_ztr[z, t, r]

                self.model.addConstr(exp <= self.l_zr[z, r], f"C3_{z}_{r}")

    def __add_constraint4(self):
        """
        (27)
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    exp1 = LinExpr()
                    for k in range(max(z - self.p, 1), z + 1):
                        exp1 += self.y_zt[k, t]
                    exp2 = LinExpr()
                    for k in range(max(z - self.p_tilde, 1), z + 1):
                        exp2 += self.v_ztr[k, t, r]

                    self.model.addConstr(self.u_ztr[z, t, r] + exp1 + exp2 <= 1, f"C4_{z}_{t}_{r}")

    def __add_constraint5(self):
        """
        (28)
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    self.model.addConstr(self.v_ztr[z, t, r] <= self.x_tilde_ztr[z, t, r], f"C5_{z}_{t}_{r}")

    def __add_constraint6(self):
        """
        (29)
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                for r in range(0, self.R):
                    exp = LinExpr()
                    for k in range(max(z - self.p + 1, 1), z + 1):
                        exp += self.y_zt[k, t]

                    self.model.addConstr(self.x_tilde_ztr[z, t, r] <=
                                         self.x_tilde_ztr[z - 1, t, r] - exp + self.y_zt[z, max(t - self.p, 1)],
                                         f"C6_{z}_{t}_{r}")

    def __add_constraint7(self):
        """
        (30)
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                exp = LinExpr()
                for r in range(0, self.R):
                    exp += self.x_tilde_ztr[z, t, r]

                self.model.addConstr(exp <= 1, f"C7_{z}_{t}")

    def __add_constraint8(self):
        """
        (31)
        """
        for z in range(0, self.Z):
            exp = LinExpr()
            for r in range(0, self.R):
                exp += self.l_zr[z, r]

            self.model.addConstr(exp <= 1, f"C8_{z}")

    def __add_constraint9(self):
        """
        (32)
        """
        for z in range(0, self.Z):
            for t in range(0, self.T):
                exp = LinExpr()
                for r in range(0, self.R):
                    exp += self.u_ztr[z, t, r]

                self.model.addConstr(exp <= 1, f"C9_{z}_{t}")

    def __add_constraint10(self):
        """
        (33)
        """
        for z in range(0, self.Z):
            for r in range(0, self.R):
                exp = LinExpr()
                for t in range(0, self.T):
                    exp += self.u_ztr[z, t, r]

                self.model.addConstr(1 - exp <= self.s_zr[z, r], f"C10_{z}_{r}")

    def save_results(self):
        y_zt = np.ndarray(shape=[self.Z, self.T])
        u_ztr = np.ndarray(shape=[self.Z, self.T, self.R])
        l_zr = np.ndarray(shape=[self.Z, self.R])
        x_tilde_ztr = np.ndarray(shape=[self.Z, self.T, self.R])
        f_ztr = np.ndarray(shape=[self.Z, self.T, self.R])
        s_zr = np.ndarray(shape=[self.Z, self.R])

        for z in range(0, self.Z):
            for t in range(0, self.T):
                y_zt[z, t] = self.y_zt[z, t].X

                for r in range(0, self.R):
                    u_ztr[z, t, r] = self.u_ztr[z, t, r].X
                    x_tilde_ztr[z, t, r] = self.x_tilde_ztr[z, t, r].X
                    f_ztr[z, t, r] = self.f_ztr[z, t, r].X

            for r in range(0, self.R):
                l_zr[z, r] = self.l_zr[z, r].X
                s_zr[z, r] = self.s_zr[z, r].X

        pd.DataFrame(y_zt).to_csv("y_zt.csv")
        pd.DataFrame(u_ztr).to_csv("u_ztr.csv")
        pd.DataFrame(l_zr).to_csv("l_zr.csv")
        pd.DataFrame(x_tilde_ztr).to_csv("x_tilde_ztr.csv")
        pd.DataFrame(f_ztr).to_csv("f_ztr.csv")
        pd.DataFrame(s_zr).to_csv("s_zr.csv")

    # endregion

    def run(self):
        try:
            self.model.setParam('TimeLimit', 20 * 60)
            self.model.optimize()
            self.save_results()

        except gp.GurobiError as e:
            # noinspection PyUnresolvedReferences
            print('Error code ' + str(e.errno) + ': ' + str(e))

        except AttributeError:
            print('Encountered an attribute error')
