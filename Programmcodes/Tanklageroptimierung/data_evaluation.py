import csv

import numpy as np
import pandas as pd
from Tanklageroptimierung.data_reader import DataReader


class DataEvaluation:
    def __init__(self, raster_zeitschritte):
        self.solution = self._read_solution()
        self.raster_zeitschritte = raster_zeitschritte
        self.data = DataReader(self.raster_zeitschritte)
        self.rohstoff_mapping = self.data.rohstoff_mapping
        self.rohstoff_mapping['r'] = self.rohstoff_mapping['r'].astype(str)
        self.time_mapping = self.data.time_mapping
        self.e = self.__read_e()
        self.x_tilde = self.__read_x_tilde()
        self.u = self.__read_u()
        self.v = self.__read_v()
        self.y = self.__read_y()
        self.l = self.__read_l()
        self.s = self.__read_s()
        self.f = self.__read_f()
        self.__write_excel()


    def _read_solution(self) -> pd.DataFrame:
        solution = pd.read_csv(r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\0.sol')
        solution = pd.DataFrame(solution)
        solution.drop([0], inplace=True)
        solution.reset_index(drop=True,inplace=True)
        solution.rename(columns={"# Solution for model chemie": 'type'}, inplace=True)
        return solution

    def __read_e(self) -> pd.DataFrame:
        e = self.solution[self.solution["type"].str[0] == "e"]
        e = e.type.str.split(pat=" ", expand=True)
        e.rename(columns={0: 'type', 1 : "value"}, inplace=True)
        e[['type', 'Time', 'Material']] = e.type.str.split(pat="_", expand=True)
        e = pd.merge(e, self.rohstoff_mapping, left_on='Material', right_on='r', how="inner")
        e['Time'] = e['Time'].astype(float)
        e = pd.merge(e, self.time_mapping, left_on='Time', right_on='Model Time', how="inner")
        e.drop(columns=['r', 'Time'], inplace=True)
        return e

    def __read_x_tilde(self) -> pd.DataFrame:
        x_tilde = self.solution[self.solution["type"].str.contains('x_tilde') == True]
        x_tilde = x_tilde.type.str.split(pat=" ", expand=True)
        x_tilde.rename(columns={0: 'reset', 1 : "value"}, inplace=True)
        x_tilde['type'] = x_tilde['reset'].str[0:7]
        x_tilde['temp'] = x_tilde['reset'].str[8:]
        x_tilde[['Time', 'Tank', 'Material']] = x_tilde.temp.str.rsplit(pat="_", expand=True)
        x_tilde = pd.merge(x_tilde, self.rohstoff_mapping, left_on='Material', right_on='r', how="inner")
        x_tilde.drop(columns=['reset', 'temp', 'r'], inplace=True)
        return x_tilde

    def __read_f(self) -> pd.DataFrame:
        f = self.solution[self.solution["type"].str[0] == "f"]
        f = f.type.str.split(pat=" ", expand=True)
        f.rename(columns={0: 'type', 1 : "value"}, inplace=True)
        f[['type', 'Time','Tank', 'Material']] = f.type.str.split(pat="_", expand=True)
        f = pd.merge(f, self.rohstoff_mapping, left_on='Material', right_on='r', how="inner")
        f.drop(columns=['r'], inplace=True)
        return f

    def __read_u(self) -> pd.DataFrame:
        u = self.solution[self.solution["type"].str[0] == "u"]
        u = u.type.str.split(pat=" ", expand=True)
        u.rename(columns={0: 'type', 1 : "value"}, inplace=True)
        u[['type', 'Time','Tank', 'Material']] = u.type.str.split(pat="_", expand=True)
        u = pd.merge(u, self.rohstoff_mapping, left_on='Material', right_on='r', how="inner")
        u.drop(columns=['r'], inplace=True)
        return u

    def __read_v(self) -> pd.DataFrame:
        v = self.solution[self.solution["type"].str[0] == "v"]
        v = v.type.str.split(pat=" ", expand=True)
        v.rename(columns={0: 'type', 1 : "value"}, inplace=True)
        v[['type', 'Time','Tank', 'Material']] = v.type.str.split(pat="_", expand=True)
        v = pd.merge(v, self.rohstoff_mapping, left_on='Material', right_on='r', how="inner")
        v.drop(columns=['r'], inplace=True)
        return v

    def __read_y(self) -> pd.DataFrame:
        y = self.solution[self.solution["type"].str[0] == "y"]
        y = y.type.str.split(pat=" ", expand=True)
        y.rename(columns={0: 'type', 1 : "value"}, inplace=True)
        y[['type', 'Time','Tank']] = y.type.str.split(pat="_", expand=True)
        return y

    def __read_l(self) -> pd.DataFrame:
        l = self.solution[self.solution["type"].str[0] == "l"]
        l = l.type.str.split(pat=" ", expand=True)
        l.rename(columns={0: 'type', 1 : "value"}, inplace=True)
        l[['type', 'Time', 'Material']] = l.type.str.split(pat="_", expand=True)
        l = pd.merge(l, self.rohstoff_mapping, left_on='Material', right_on='r', how="inner")
        l.drop(columns=['r'], inplace=True)
        return l

    def __read_s(self) -> pd.DataFrame:
        s = self.solution[self.solution["type"].str[0] == "s"]
        s = s.type.str.split(pat=" ", expand=True)
        s.rename(columns={0: 'type', 1 : "value"}, inplace=True)
        s[['type', 'Time', 'Material']] = s.type.str.split(pat="_", expand=True)
        s = pd.merge(s, self.rohstoff_mapping, left_on='Material', right_on='r', how="inner")
        s.drop(columns=['r'], inplace=True)
        return s

    def __write_excel(self):
        self.e.to_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\e_zr.xlsx')
        self.x_tilde.to_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\x_tilde_ztr.xlsx')
        self.f.to_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\f_ztr.xlsx')
        self.u.to_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\u_ztr.xlsx')
        self.v.to_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\v_ztr.xlsx')
        self.y.to_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\y_zt.xlsx')
        self.l.to_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\l_zr.xlsx')
        self.s.to_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\s_zr.xlsx')