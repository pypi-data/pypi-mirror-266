import pandas as pd
import numpy as np



class DataProcessing:

    @staticmethod
    def add_qres(df_data: pd.DataFrame, df_info: pd.DataFrame, dict_add_new_qres: dict, is_add_oe_col: bool = False) -> (pd.DataFrame, pd.DataFrame):
        info_col_name = ['var_name', 'var_lbl', 'var_type', 'val_lbl']

        for key, val in dict_add_new_qres.items():

            if val[1] in ['MA']:
                qre_ma_name, max_col = str(key).rsplit('|', 1)

                for i in range(1, int(max_col) + 1):
                    df_info = pd.concat([df_info, pd.DataFrame(columns=info_col_name, data=[[f'{qre_ma_name}_{i}', val[0], val[1], val[2]]])], axis=0, ignore_index=True)

                    if '_OE' not in key or is_add_oe_col is True:
                        df_data = pd.concat([df_data, pd.DataFrame(columns=[f'{qre_ma_name}_{i}'], data=[val[-1]] * df_data.shape[0])], axis=1)

            else:
                df_info = pd.concat([df_info, pd.DataFrame(columns=info_col_name, data=[[key, val[0], val[1], val[2]]])], axis=0, ignore_index=True)

                if '_OE' not in key or is_add_oe_col is True:
                    df_data = pd.concat([df_data, pd.DataFrame(columns=[key], data=[val[-1]] * df_data.shape[0])], axis=1)

        
        df_data.reset_index(drop=True, inplace=True)
        df_info.reset_index(drop=True, inplace=True)


        return df_data, df_info



    @staticmethod
    def align_ma_values_to_left(df_data: pd.DataFrame, qre_name: str | list, fillna_val: float = None) -> pd.DataFrame:

        lst_qre_name = [qre_name] if isinstance(qre_name, str) else qre_name

        for qre_item in lst_qre_name:

            qre, max_col = qre_item.rsplit('|', 1)

            lst_qre = [f'{qre}_{i}' for i in range(1, int(max_col) + 1)]

            df_fil = df_data.loc[:, lst_qre].copy()
            df_fil = df_fil.T
            df_sort = pd.DataFrame(np.sort(df_fil.values, axis=0), index=df_fil.index, columns=df_fil.columns)
            df_sort = df_sort.T
            df_data[lst_qre] = df_sort[lst_qre]

            # for col in lst_qre:
            #     df_data[col] = df_sort[col]

            del df_fil, df_sort

            if fillna_val:
                df_data.loc[df_data.eval(f"{qre}_1.isnull()"), f'{qre}_1'] = fillna_val

        return df_data



    @staticmethod
    def delete_qres(df_data: pd.DataFrame, df_info: pd.DataFrame, lst_col: list) -> (pd.DataFrame, pd.DataFrame):

        df_data.drop(columns=lst_col, inplace=True)
        df_info = df_info.loc[df_info.eval(f"~var_name.isin({lst_col})"), :].copy()

        df_data.reset_index(drop=True, inplace=True)
        df_info.reset_index(drop=True, inplace=True)

        return df_data, df_info



