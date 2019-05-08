import datetime


def set_df(df_):
    global last_updatetime
    global df

    df = df_
    last_updatetime = datetime.datetime.now()


def get_df(self):
    return self.df


def get_update_datetime():
    return last_updatetime
