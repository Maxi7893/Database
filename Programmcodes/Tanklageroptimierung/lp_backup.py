import numpy as np
import gurobipy as gp
from gurobipy import GRB, LinExpr


# noinspection DuplicatedCode,SpellCheckingInspection
class LP:
    def __init__(self,
                 rohstoffkosten_r: np.ndarray,
                 abfallkosten_r: np.ndarray,
                 reinigungskosten_rohstoffgebinde_r: np.ndarray,
                 kosten_tankreinigung_tr: np.ndarray,
                 kapazitaet_bahnkesselwagen_r: np.ndarray,
                 auftraege_zr: np.ndarray,
                 kosten_bahnkesselwagen_r: np.ndarray,
                 maximale_fuellmengen_tr: np.ndarray,
                 gebindegroessen_r: np.ndarray,
                 initiale_tankfuellung_tr: np.ndarray,
                 anzahl_zeitpunkte: int,
                 anzahl_tanks: int,
                 anzahl_rohstoffe: int,
                 anzahl_zeitpunkte_tankfuellung_tr: np.ndarray,
                 anzahl_zeitpunkte_reinigung_tr: np.ndarray,
                 anteil_bahnkesselwagen_tr: np.ndarray):
        """
        Initialisierer für das LP. Alle ndarrays müssen in der Reihenfolge der Subscripts indiziert werden, d.h. z.B.
        initiale_tankfuellung_tr wird in der ersten Dimension mit dem Tank und in der zweiten Dimension mit dem
        Rohstoff indiziert. initiale_tankfuellung_tr[2,5] indiziert Tank 2 mit Rohstoff 5. Die größe des ndarrays
        ergibt sich als T x R bzw 'anzahl_tanks' x 'anzahl_rohstoffe'. Alle Indizees folgen derselben Reihenfolge
        z -> t -> r.


        :param rohstoffkosten_r: Kosten für Rohstoff r.
        :param abfallkosten_r: Kosten für Abfall r.
        :param reinigungskosten_rohstoffgebinde_r: Kosten für Rohstoffgebinde r bei Reinigung.
        :param kosten_tankreinigung_tr: Kosten für Reinigung von Tank t mit Rohstoff r.
        :param kapazitaet_bahnkesselwagen_r: Kapazität Bahnkesselwagen für Rohstoff r.
        :param auftraege_zr: Benötigte Menge von Rohstoff r zum Zeitpunkt z.
        :param kosten_bahnkesselwagen_r: Kosten pro Bahnkesselwagen für Rohstoff r.
        :param maximale_fuellmengen_tr: Maximale Füllmenge von Tank t mit Rohstoff r.
        :param gebindegroessen_r: Gebindegröße für Rohstoff r.
        :param initiale_tankfuellung_tr: Initialer Füllstand von Tank t mit Rohstoff r.
        :param anzahl_zeitpunkte: Anzahl Zeitpunkte.
        :param anzahl_tanks: Anzahl Tanks.
        :param anzahl_rohstoffe: Anzahl verschiedener Rohstoffe.
        :param anzahl_zeitpunkte_tankfuellung_tr: Anzahl Zeitpunkte zum Auffüllen von Tank t mit Rohstoff r.
        :param anzahl_zeitpunkte_reinigung_tr: Anzahl Zeitpunkte, benötigt für Reinigung von Tank t mit Rohstoff r.
        :param anteil_bahnkesselwagen_tr: Anteil der Bahnkesselwagen für Rohstoff r in Tank t zum Zeitpunkt z.
        """
        self.gamma_r = rohstoffkosten_r
        self.gamma_hat_r = abfallkosten_r
        self.c_hat_r = reinigungskosten_rohstoffgebinde_r
        self.c_tr = kosten_tankreinigung_tr
        self.m_r = kapazitaet_bahnkesselwagen_r
        self.a_zr = auftraege_zr
        self.g_r = kosten_bahnkesselwagen_r
        self.k_tr = maximale_fuellmengen_tr
        self.k_hat_r = gebindegroessen_r
        self.f_0tr = initiale_tankfuellung_tr
        self.Z = anzahl_zeitpunkte
        self.T = anzahl_tanks
        self.R = anzahl_rohstoffe
        self.p_tilde_tr = anzahl_zeitpunkte_tankfuellung_tr
        self.p_tr = anzahl_zeitpunkte_reinigung_tr
        self.v_ztr = anteil_bahnkesselwagen_tr

        # initialize model
        self.model = gp.Model("chemie")

        # initialize variables
        self.y_zt = np.ndarray(shape=[self.Z, self.T])
        self.u_ztr = np.ndarray(shape=[self.Z, self.T, self.R])
        self.l_zr = np.ndarray(shape=[self.Z, self.R])
        self.x_tilde_ztr = np.ndarray(shape=[self.Z, self.T, self.R])
        self.f_ztr = np.ndarray(shape=[self.Z, self.T, self.R])
        self.s_zr = np.ndarray(shape=[self.Z, self.R])

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
        self.__add_constraint10()

    # region Variables
    # noinspection PyArgumentList
    def __add_vars(self):
        for z in range(1, self.Z + 1):
            for t in range(1, self.T + 1):
                self.y_zt = self.model.addVar(vtype=GRB.BINARY, name=f"y_{z}_{t}")

                for r in range(1, self.R + 1):
                    self.u_ztr = self.model.addVar(vtype=GRB.BINARY,
                                                   name=f"u_{z}_{t}_{r}")
                    self.x_tilde_ztr = self.model.addVar(vtype=GRB.BINARY,
                                                         name=f"x_tilde_{z}_{t}_{r}")
                    self.f_ztr = self.model.addVar(vtype=GRB.CONTINUOUS,
                                                   name=f"f_{z}_{t}_{r}",
                                                   lb=0,
                                                   ub=self.k_tr[t, r])
            for r in range(1, self.R + 1):
                self.l_zr = self.model.addVar(vtype=GRB.BINARY, name=f"l_{z}_{r}")
                self.s_zr = self.model.addVar(vtype=GRB.BINARY, name=f"s_{z}_{r}")
    # endregion

    # region Objective
    def __set_objective(self):
        """
        (23)
        """
        exp = LinExpr()

        for z in range(1, self.Z + 1):
            for t in range(1, self.T + 1):
                for r in range(1, self.R + 1):
                    exp += self.y_zt[z, t] * (self.c_tr[t, r] + self.f_ztr[z, t, r] * self.gamma_hat_r[r])

        for z in range(1, self.Z + 1):
            for r in range(1, self.R + 1):
                exp += self.l_zr[z, r] * self.g_r[r]

        for z in range(1, self.Z + 1):
            for r in range(1, self.R + 1):
                exp += self.gamma_r[r] * self.s_zr[z, r]
                exp += self.c_hat_r[r]
                for t in range(1, self.T + 1):
                    exp += self.u_ztr[z, t, r] * self.c_hat_r[r]

        self.model.setObjective(exp, GRB.MINIMIZE)
    # endregion

    # region Constraints
    def __add_constraint1(self):
        """
        (24)
        """
        for z in range(1, self.Z + 1):
            for t in range(1, self.T + 1):
                for r in range(1, self.R + 1):
                    self.model.addConstr(self.f_ztr[z, t, r] <= self.k_tr[t, r], f"C1_{z}_{t}_{r}")

    def __add_constraint2(self):
        """
        (25)
        """
        for z in range(1, self.Z + 1):
            for t in range(1, self.T + 1):
                for r in range(1, self.R + 1):
                    self.model.addConstr(self.f_ztr[z, t, r] == (
                            self.f_ztr[z - 1, t, r]
                            - (self.a_zr[z, r] * self.u_ztr[z, t, r])
                            + self.v_ztr[z, t, r] * self.l_zr[z, r])
                                         * (1 - self.y_zt[z, t]),
                                         f"C2_{z}_{t}_{r}")

    def __add_constraint3(self):
        """
        (26)
        """
        for z in range(1, self.Z + 1):
            for r in range(1, self.R + 1):
                exp = LinExpr()
                for t in range(1, self.T + 1):
                    exp += self.v_ztr[z, t, r]

                self.model.addConstr(exp <= self.l_zr[z, r] * self.m_r[r], f"C3_{z}_{r}")

    def __add_constraint4(self):
        """
        (27)
        """
        for z in range(1, self.Z + 1):
            for t in range(1, self.T + 1):
                for r in range(1, self.R + 1):
                    exp1 = LinExpr()
                    for k in range(z - self.p_tr[t, r], z + 1):
                        exp1 += self.y_zt[k, t]

                    exp2 = LinExpr()
                    for k in range(z - self.p_tilde_tr[t, r], z + 1):
                        exp2 += self.v_ztr[k, t, r]

                    self.model.addConstr(self.u_ztr[z, t, r] + exp1 + exp2 <= 1, f"C4_{z}_{t}_{r}")

    def __add_constraint5(self):
        """
        (28)
        """
        for z in range(1, self.Z + 1):
            for t in range(1, self.T + 1):
                for r in range(1, self.R + 1):
                    self.model.addConstr(self.v_ztr[z, t, r] <= self.x_tilde_ztr[z, t, r], f"C5_{z}_{t}_{r}")

    def __add_constraint6(self):
        """
        (29)
        """
        for z in range(1, self.Z + 1):
            for t in range(1, self.T + 1):
                for r in range(1, self.R + 1):
                    exp = LinExpr()
                    for k in range(z - self.p_tr[t, r] + 1, z + 1):
                        exp += self.y_zt[k, t]

                    self.model.addConstr(self.x_tilde_ztr[z, t, r] <=
                                         self.x_tilde_ztr[z-1, t, r] - exp + self.y_zt[z, t-self.p_tr[t, r]],
                                         f"C6_{z}_{t}_{r}")

    def __add_constraint7(self):
        """
        (30)
        """
        for z in range(1, self.Z + 1):
            for t in range(1, self.T + 1):
                exp = LinExpr()
                for r in range(1, self.R + 1):
                    exp += self.x_tilde_ztr[z, t, r]

                self.model.addConstr(exp <= 1, f"C7_{z}_{t}")

    def __add_constraint8(self):
        """
        (31)
        """
        for z in range(1, self.Z + 1):
            exp = LinExpr()
            for r in range(1, self.R + 1):
                exp += self.l_zr[z, r]

            self.model.addConstr(exp <= 1, f"C8_{z}")

    def __add_constraint9(self):
        """
        (32)
        """
        for z in range(1, self.Z + 1):
            for r in range(1, self.R + 1):
                exp = LinExpr()
                for t in range(1, self.T + 1):
                    exp += self.u_ztr[z, t, r]

                self.model.addConstr(exp <= 1, f"C9_{z}_{r}")

    def __add_constraint10(self):
        """
        (33)
        """
        for z in range(1, self.Z + 1):
            for r in range(1, self.R + 1):
                exp = LinExpr()
                for t in range(1, self.T + 1):
                    exp += self.u_ztr[z, t, r]

                self.model.addConstr(1 - exp <= self.s_zr[z, r], f"C10_{z}_{r}")
    # endregion

    def run(self):
        try:
            self.model.optimize()

        except gp.GurobiError as e:
            # noinspection PyUnresolvedReferences
            print('Error code ' + str(e.errno) + ': ' + str(e))

        except AttributeError:
            print('Encountered an attribute error')
