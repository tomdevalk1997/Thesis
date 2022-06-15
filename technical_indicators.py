import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statistics import mean, stdev

def calculate_daily_relative_difference(df, column_open, column_close, varname):
    """
    Function that calculates the daily relative difference, or daily rate of change
    Input:  df - pandas dataframe to which the daily rate of change should be added
            column_open - column name (string) of the open price
            column_close - column name (string) of the close price
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    diffs = {}
    for index, row in df.iterrows():
        if row[column_open] == 0:
            diff = (row[column_close] - row[column_open]) / 0.0000001
        else:
            diff = (row[column_close] - row[column_open]) / row[column_open]
        diffs[row['Date']] = diff
    df[varname + '_relative_change_perc_1'] = df['Date'].map(diffs)
    return df

def calculate_average_relative_difference(df, column_open, column_close, days_list, varname):
    """
    Function that calculates the average relative difference, or average rate of change over a certain period
    Input:  df - pandas dataframe to which the average relative difference should be added
            column_open - column name (string) of the open price
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the average
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    for days in days_list:
        vals = []
        diffs = {}
        for index, row in df.iterrows():
            if row[column_open] == 0:
                vals.append((row[column_close] - row[column_open]) / 0.0000001)
            else:
                vals.append((row[column_close] - row[column_open]) / row[column_open])
            if index >= days - 1:
                diffs[row['Date']] = mean(vals)
                vals.pop(0)
        df[varname + '_relative_change_perc_' + str(days)] = df['Date'].map(diffs)
    return df

def calculate_exponential_moving_average(df, column_close, days_list, varname):
    """
    Function that calculates the exponential moving average over a certain period
    Input:  df - pandas dataframe to which the exponential moving average should be added
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the average
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    the most common smoothing choice is 2 - https://www.investopedia.com/terms/e/ema.asp
    a large drawback of this indicator is the warmup period. Analysis is required to determine when the warmup is completed

    Output validated
    """
    for days in days_list:
        vals = []
        emas = {}
        ema = 0 # placeholder
        for index, row in df.iterrows():
            if index + 1 == days:
                vals.append(row[column_close])
                ema = mean(vals) # placeholder
                emas[row['Date']] = ema
            elif index >= days:
                multiplier = 2 / (days + 1)
                ema = (row[column_close] - ema) * multiplier + ema
                emas[row['Date']] = ema
            else:
                vals.append(row[column_close])
        df[varname + '_EMA' + str(days)] = df['Date'].map(emas)
    return df

def calculate_moving_average(df, column_close, days_list, varname):
    """
    Function that calculates the moving average over a certain period
    Input:  df - pandas dataframe to which the moving average should be added
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the average
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    for days in days_list:
        vals = []
        mas = {}
        ma = 0 # placeholder
        for index, row in df.iterrows():
            if index + 1 >= days:
                vals.append(row[column_close])
                ma = mean(vals)
                mas[row['Date']] = ma
                vals.pop(0)
            else:
                vals.append(row[column_close])
        df[varname + '_MA' + str(days)] = df['Date'].map(mas)
    return df

def calculate_average_true_range(df, column_open, column_high, column_low, column_close, days_list, varname):
    """
    Function that calculates the average true range over a certain period
    Input:  df - pandas dataframe to which the average true range should be added
            column_open - column name (string) of the open price
            column_high - column name (string) of the high price
            column_low - column name (string) of the low price
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the average
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    calculation according to https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/average-true-range/#:~:text=The%20calculation%20of%20the%20average%20true%20range%20is,continuous%20line%20that%20shows%20the%20change%20in%20volatility
    a drawback of this technical indicator is a warmup period. Possiby requires an analysis to find out how long the warmup period actually is.

    The first value of the ATR5 is on day 6 as the first day is required for previous_close

    Output validated
    """
    for days in days_list:
        vals = []
        atrs = {}
        atr = 0 # placeholder
        prev_close = 0 # placeholder
        for index, row in df.iterrows():
            if index >= days:
                metric1 = row[column_high] - row[column_low]
                metric2 = row[column_low] - prev_close
                metric3 = row[column_high] - prev_close
                if index == days:
                    vals.append(max(metric1, metric2, metric3))
                atr = (mean(vals) * (days - 1) + max(metric1, metric2, metric3)) / days
                atrs[row['Date']] = atr
                vals.append(atr)
                if len(vals) > days:
                    vals.pop(0)
                prev_close = row[column_close]
            elif index > 0:
                metric1 = row[column_high] - row[column_low]
                metric2 = row[column_low] - prev_close
                metric3 = row[column_high] - prev_close
                vals.append(max(metric1, metric2, metric3))
                prev_close = row[column_close]
            else:
                prev_close = row[column_close]

        df[varname + '_ATR' + str(days)] = df['Date'].map(atrs)
    return df

def calculate_weeks_high(df, column_high, weeks_list, varname):
    """
    Function that calculates the highest high over a certain period
    Input:  df - pandas dataframe to which the highest high should be added
            column_high - column name (string) of the high price
            weeks_list - list of integers to describe the size of the period to consider for the average
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    for weeks in weeks_list:
        days = weeks * 5 # trading days
        vals = []
        highs = {}
        for index, row in df.iterrows():
            if index + 1 >= days:
                vals.append(row[column_high])
                high = max(vals)
                highs[row['Date']] = high
                vals.pop(0)
            else:
                vals.append(row[column_high])
        df[varname + '_week_high_' + str(weeks)] = df['Date'].map(highs)
    return df

def calculate_weeks_low(df, column_low, weeks_list, varname):
    """
    Function that calculates the lowest low over a certain period
    Input:  df - pandas dataframe to which the lowest low should be added
            column_low - column name (string) of the low price
            weeks_list - list of integers to describe the size of the period to consider for the average
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    for weeks in weeks_list:
        days = weeks * 5 # trading days
        vals = []
        lows = {}
        for index, row in df.iterrows():
            if index + 1 >= days:
                vals.append(row[column_low])
                low = min(vals)
                lows[row['Date']] = low
                vals.pop(0)
            else:
                vals.append(row[column_low])
        df[varname + '_week_low_' + str(weeks)] = df['Date'].map(lows)
    return df

def calculate_relative_strength_index(df, column_open, column_close, days_list, varname):
    """
    Function that calculates the relative strength index over a certain period
    Input:  df - pandas dataframe to which the relative strength index should be added
            column_open - column name (string) of the open price
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the average
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    deviates from normal calculation to avoid division through 0

    Output validated
    """
    for days in days_list:
        ups = []
        downs = []
        all_moves = []
        rsis = {}
        for index, row in df.iterrows():
            if row[column_open] <= row[column_close]:
                ups.append(row[column_close] - row[column_open])
                all_moves.append(row[column_close] - row[column_open])
            else:
                downs.append(row[column_open] - row[column_close])
                all_moves.append(row[column_open] - row[column_close])

            if index + 1 >= days:
                if len(all_moves) > days:
                    if all_moves[0] in ups:
                        all_moves.pop(0)
                        ups.pop(0)
                    elif all_moves[0] in downs:
                        all_moves.pop(0)
                        downs.pop(0)

                if len(downs) == 0:
                    downs = [0.0000001] # pseudozero
                if len(ups) == 0:
                    ups = [0]
                # if index + 1 == days:
                #     print(mean(ups), mean(downs))
                rsi = 100 - (100 / (1 + (mean(ups) / mean(downs))))
                rsis[row['Date']] = rsi
        df[varname + '_RSI_' + str(days)] = df['Date'].map(rsis)
    return df

def calculate_stochastic_k(df, column_high, column_low, column_close, days_list, varname):
    """
    Function that calculates the stochastic K% over a certain period
    Input:  df - pandas dataframe to which the stochastic K% should be added
            column_high - column name (string) of the high price
            column_low - column name (string) of the low price
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the metric
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    for days in days_list:
        highs = []
        lows = []
        stochs = {}
        for index, row in df.iterrows():
            highs.append(row[column_high])
            lows.append(row[column_low])
            if len(highs) > days:
                highs.pop(0)
            if len(lows) > days:
                lows.pop(0)
            if index + 1 >= days:
                stochs[row['Date']] = (row[column_close] - min(lows)) / (max(highs) - min(lows))
        df[varname + '_stochastic_K_' + str(days)] = df['Date'].map(stochs)
    return df

def calculate_stochastic_d(df, column_high, column_low, column_close, days_list, varname):
    """
    Function that calculates the stochastic D% over a certain period
    Input:  df - pandas dataframe to which the stochastic D% should be added
            column_high - column name (string) of the high price
            column_low - column name (string) of the low price
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the metric
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    for days in days_list:
        vals = []
        stochs = {}
        if varname + "_stochastic_K_" + str(days) not in df.columns.tolist():
            df_temp = calculate_stochastic_k(df, column_high, column_low, column_close, days_list, varname)
        else:
            df_temp = df.copy()
        for index, row in df_temp.iterrows():
            if index + 1 >= days:
                vals.append(row[varname + "_stochastic_K_" + str(days)]) # replace days with k_days
                if len(vals) > days:
                    vals.pop(0)
                if len(vals) == days:
                    stochs[row['Date']] = mean(vals)
        df[varname + '_stochastic_D_' + str(days) + "_" + str(days)] = df['Date'].map(stochs)
    return df

def calculate_momentum(df, column_close, days_list, varname):
    """
    Function that calculates the momentum over a certain period
    Input:  df - pandas dataframe to which the momentum should be added
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the metric
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    default value for days is 4

    Output validated
    """
    for days in days_list:
        vals = []
        momentums = {}
        for index, row in df.iterrows():
            if index >= days:
                momentums[row['Date']] = row[column_close] - vals[0]
            vals.append(row[column_close])
            if len(vals) > days:
                vals.pop(0)
        df[varname + '_momentum_' + str(days)] = df['Date'].map(momentums)
    return df

def calculate_williams_r(df, column_high, column_low, column_close, days_list, varname):
    """
    Function that calculates the Williams R% over a certain period
    Input:  df - pandas dataframe to which the Williams R% should be added
            column_high - column name (string) of the high price
            column_low - column name (string) of the low price
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the metric
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    for days in days_list:
        wills = {}
        highs = []
        lows = []
        for index, row in df.iterrows():
            if index + 1 >= days:
                diff = (highs[0] - lows[0])
                if diff == 0:
                    diff = 0.0000001
                wills[row['Date']] = (highs[0] - row[column_close]) / diff
            highs.append(row[column_high])
            lows.append(row[column_low])
            if len(highs) > days:
                highs.pop(0)
            if len(lows) > days:
                lows.pop(0)
        df[varname + '_williams_R_' + str(days)] = df['Date'].map(wills)
    return df

def calculate_ad_oscillator(df, column_high, column_low, column_close, varname):
    """
    Function that calculates the accummulation distribution oscillator
    Input:  df - pandas dataframe to which the accummulation distribution oscillator should be added
            column_high - column name (string) of the high price
            column_low - column name (string) of the low price
            column_close - column name (string) of the close price
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    ads = {}
    vals = []
    for index, row in df.iterrows():
        if index > 0:
            diff = (row[column_high] - row[column_low])
            if diff == 0:
                diff = 0.0000001
            ads[row['Date']] = (row[column_high] - vals[-1]) / diff
        vals.append(row[column_close])
    df[varname + '_AD_oscillator'] = df['Date'].map(ads)
    return df


def calculate_disparity(df, column_close, days_list, varname):
    """
    Function that calculates the disparity
    Input:  df - pandas dataframe to which the disparity should be added
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the metric
            varname - stock/index name (string) to name the column
    Output: original dataframe with additional column

    Output validated
    """
    for days in days_list:
        disps = {}
        if varname + "_MA" + str(days) not in df.columns.tolist():
            df_temp = calculate_moving_average(df, column_close, [days], varname)
        else:
            df_temp = df.copy()
        for index, row in df_temp.iterrows():
            if index + 1 >= days:
                disps[row['Date']] = row[column_close] / row[varname + "_MA" + str(days)]
        df[varname + '_disparity_' + str(days)] = df['Date'].map(disps)
    return df

def calculate_moving_average_convergence_divergence(df, column_close, days_pairs_list, varname):
    """
    Function that calculates the moving average convergence divergence
    Input:  df - pandas dataframe to which the moving average convergence divergence should be added
            column_close - column name (string) of the close price
            varname - stock/index name (string) to name the column
            days_pairs_list - list of pairs of integers to describe the two sizes of the periods required to determine the moving average convergence divergence
    Output: original dataframe with additional column

    Output validated
    """
    for days_pairs in days_pairs_list:
        days1 = days_pairs[0]
        days2 = days_pairs[1]
        df_temp = calculate_exponential_moving_average(df.copy(), column_close, [days1, days2], varname)
        macds = {}
        for index, row in df_temp.iterrows():
            if index + 1 >= max(days1, days2):
                macds[row['Date']] = row[varname + '_EMA' + str(days1)] - row[varname + '_EMA' + str(days2)]
        df[varname + '_AD_MACD_' +  str(days1) + "_" + str(days2)] = df['Date'].map(macds)
    return df

def calculate_bollinger_bands(df, column_close, days_list, varname):
    """
    Function that calculates the high, mid and low bollinger bands
    Input:  df - pandas dataframe to which the bollinger bands should be added
            column_close - column name (string) of the close price
            days_list - list of integers to describe the size of the period to consider for the metric
    Output: original dataframe with additional column

    Output validated
    """
    for days in days_list:
        highs = {}
        mids = {}
        lows = {}
        vals = []
        if varname + "_MA" + str(days) not in df.columns.tolist():
            df_temp = calculate_moving_average(df.copy(), column_close, [days], varname)
        else:
            df_temp = df.copy()
        for index, row in df_temp.iterrows():
            vals.append(row[column_close])
            if len(vals) > days:
                vals.pop(0)
            if index + 1 >= days:
                highs[row['Date']] = row[varname + "_MA" + str(days)] + 2 * stdev(vals)
                mids[row['Date']] = row[varname + "_MA" + str(days)]
                lows[row['Date']] = row[varname + "_MA" + str(days)] - 2 * stdev(vals)
        df[varname + '_bollinger_high_' + str(days)] = df['Date'].map(highs)
        df[varname + '_bollinger_middle_' + str(days)] = df['Date'].map(mids)
        df[varname + '_bollinger_low_' + str(days)] = df['Date'].map(lows)
    return df

def calculate_on_balance_volume(df, column_open, column_close, column_volume, varname):
    """
    Function that calculates the on-balance volume
    Input:  df - pandas dataframe to which the on-balance volume should be added
            column_open - column name (string) of the open price
            column_close - column name (string) of the close price
            column_volume - column name (string) of the trading volume
    Output: original dataframe with additional column

    a drawback of this technical indicator is a warmup period. Possiby requires an analysis to find out how long the warmup period actually is.

    Output validated
    """
    if column_volume in df.columns.tolist():
        obvs = {}
        obv = 0
        for index, row in df.iterrows():
            if row[column_open] <= row[column_close]:
                obv = obv + row[column_volume]
            else:
                obv = obv - row[column_volume]
            obvs[row['Date']] = obv
        df[varname + '_OBV'] = df['Date'].map(obvs)
    return df

def calculate_stdev_on_balance_volume(df, column_open, column_close, column_volume, days_list, varname):
    """
    Function that calculates the standard deviation in on-balance volume
    Input:  df - pandas dataframe to which the standard deviation of the on-balance volume should be added
            column_open - column name (string) of the open price
            column_close - column name (string) of the close price
            column_volume - column name (string) of the trading volume
            days_list - list of integers to describe the size of the period to consider for the metric
    Output: original dataframe with additional column(s)

    Output validated
    """
    if column_volume in df.columns.tolist():
        df_temp = calculate_on_balance_volume(df, column_open, column_close, column_volume, varname)
        for days in days_list:
            vars = {}
            vals = []
            for index, row in df_temp.iterrows():
                vals.append(row[varname + "_OBV"])
                if len(vals) > days:
                    vals.pop(0)
                if len(vals) >= days:
                    vars[row['Date']] = stdev(vals)
            df[varname + '_OBV_stdev_' + str(days)] = df['Date'].map(vars)
    return df
