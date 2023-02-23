import pandas as pd 
from pandas  import read_csv
from matplotlib import pyplot as plt
from matplotlib.pyplot import title
from datetime import datetime
import glob
import plotly.graph_objects as go
import os
import mplfinance as fplt 
from scipy.signal import find_peaks
import re


numOfBars = 0 # global variable - all candles in data set 
def makeDataFrame(path, dateBeginM, dateBeginY, dateEndM, dateEndY, filename): # later to control scope of data to be read


    # first 6 columns important for now, not deleting s1 - s6, may be useful in the future
    colnames=['time','o', 'h', 'l', 'c', 'volume', 's1', 's2', 's3', 's4', 's5', 's6']

    file_list = glob.glob(path + "/*.csv")

    excel_list = []

    fileList = []

    begin = path + filename + str(dateBeginY) + "-" + str(dateBeginM) + ".csv"
    end = str(dateEndY) + "-" + str(dateEndM) + ".csv"

    print(begin)

    whetherToAppend = False

    for file in file_list:
        if file == "/*" + begin:
            whetherToAppend = True
        
        if whetherToAppend:
            fileList.append(file)
            excel_list.append(pd.read_csv(file, names=colnames, header = None))

        if whetherToAppend == True and file == "/*" + end:
            whetherToAppend = False
        

    

    print(fileList)
    print("dsa")

    df_all = pd.concat(excel_list)


    df = df_all

    green = 0
    global numOfBars
    numOfBars = len(df.index)
    price = []

    for x in range(0, numOfBars):
        
        df.iloc[x, 0] = datetime.fromtimestamp(df.iloc[x, 0]/1000)
        price.append(df.iloc[x, 4])
        if df.iloc[x, 4] > df.iloc[x,1]:
            green = green + 1

    return df


# it is essential that multiple dataFrames have same length - same period of different trading pairs

df = makeDataFrame("C:\\Users\\fsami\\Desktop\\trejdor\\months\\ETHUSDT", "07", 2020, "01", 2023)
dfDown = makeDataFrame("C:\\Users\\fsami\\Desktop\\trejdor\\months\\ETHDOWNUSDT", "07", 2020, "01", 2023)


def open(index, dataFrame):
    df = dataFrame
    return df.iloc[index, 1]

def high(index, dataFrame):
    df = dataFrame
    return df.iloc[index, 2]

def low(index, dataFrame):
    df = dataFrame
    return df.iloc[index, 3]

def close(index, dataFrame):
    df = dataFrame
    return df.iloc[index, 4]

def time(index):
    return df.iloc[index, 0]

# df.to_excel('C:\\Users\\fsami\\Desktop\\trejdor\\output.xlsx', index=False, header=False)


# print(df)


# vwap calculation 

def vwap(dataFrame):
    df = dataFrame
    typicalPrice = []
    cumVol = []
    cumVol.append(df.iloc[0, 5])
    cumTypPrice = []
    vwap = []


    for x in range(0, numOfBars):
        typicalPrice.append((df.iloc[x, 2] + df.iloc[x, 3] + df.iloc[x, 4]) / 3)


    for x in range(0, numOfBars):
        typicalPrice[x] = typicalPrice[x] * df.iloc[x, 5] 
        


    cumTypPrice.append(typicalPrice[0])

    vwap.append(cumTypPrice[0] / cumVol[0])

    for x in range(1, numOfBars):
        if (df.iloc[x,0].hour == 1):
            cumVol.append(df.iloc[x, 5])
            cumTypPrice.append(typicalPrice[x])
        else:
            cumVol.append(cumVol[x-1] + df.iloc[x, 5])
            cumTypPrice.append(cumTypPrice[x - 1] + typicalPrice[x])
        vwap.append(cumTypPrice[x] / cumVol[x])

    return vwap

vwapDfDown = vwap(dfDown)
vwapDf = vwap(df)

df['vwap'] = vwap(df)




def highestHigh(length, dataFrame):
    df = dataFrame
    highestHigh = []
    highestHigh.append(df.iloc[0, 2])
    count = 1
    df = dataFrame
    for x in range(1, numOfBars):
        if count == length:
            highestHigh.append(df.iloc[x, 2])
            count = 0
        else:
            highestHigh.append(max(highestHigh[-1], df.iloc[x, 2]))
            if highestHigh[-2] < df.iloc[x, 2]:
                count = 0
        count = count + 1
    return highestHigh


def lowestLow(length, dataFrame):
    df = dataFrame
    lowestLow = []
    lowestLow.append(df.iloc[0, 3])
    count = 1
    for x in range(1, numOfBars):
        if count == length:
            lowestLow.append(df.iloc[x, 3])
            count = 0
        else:
            lowestLow.append(min(lowestLow[-1], df.iloc[x, 3]))
            if lowestLow[-2] > df.iloc[x, 3]:
                count = 0
        count = count + 1
    return lowestLow


# highlight_inds = [1, 3]

ll = lowestLow(7, df)
hh = highestHigh(7, df)

trace = go.Candlestick(
    x=df['time'],
    open=df['o'],
    high=df['h'],
    low=df['l'],
    close=df['c'],
    name='all data'
)

trace1 = go.Candlestick(  ## chart for DOWN token
    x=dfDown['time'],
    open=dfDown['o'],
    high=dfDown['h'],
    low=dfDown['l'],
    close=dfDown['c'],
    name='all data'
)

fig = go.Figure(data = trace)
# fig.update_layout(template="plotly_dark")
fig1 = go.Figure(data = trace1)

fig.update_layout(xaxis_rangeslider_visible=False)
fig1.update_layout(xaxis_rangeslider_visible=False)


fig.update_yaxes(fixedrange=False)
fig1.update_yaxes(fixedrange=False)

# fig.add_trace(go.Scatter(x=df['time'],
#                          y=ll,
#                          opacity=0.7,
#                          line=dict(color='purple', width=2),
#                          name='lowestLow'))

# fig.add_trace(go.Scatter(x=df['time'],
#                          y=hh,
#                          opacity=0.7,
#                          line=dict(color='black', width=2),
#                          name='lowestLow'))

fig.add_trace(go.Scatter(x=df['time'],
                         y=vwapDf,
                         opacity=0.7,
                         line=dict(color='blue', width=2),
                         name='vwap'))

fig1.add_trace(go.Scatter(x=df['time'],
                         y=vwapDfDown,
                         opacity=0.7,
                         line=dict(color='blue', width=2),
                         name='vwap'))


## peak finding using built in function from plotly disabled for faster calculaitons

# indices = find_peaks(df['h'], distance = 20)[0]


# fig.add_trace(go.Scatter(
#     x = [df.iloc[j, 0] for j in indices],
#     y = [df.iloc[j, 2] for j in indices] ,
#     mode='markers',
#     marker=dict(
#         size=12,
#         color='red',
#         symbol='cross'
#     ),
#     name='Detected Peaks'
# ))


### position handling 

## is down token says if position is being open on down token dataframe, used for shorting

class Position:
    def __init__(self, index, equity, maxLossPerTrade, direction, dateOfEntry, stopLoss,  riskRewardRatio, fee, dataFrame, isDownToken): 
        self.index = index
        self.direction = direction
        self.dateOfEntry = dateOfEntry
        self.stopLoss = stopLoss
        self.riskRewardRatio = riskRewardRatio
        self.fee = fee
        x = index
        self.dataFrame = dataFrame
        df = dataFrame
        # while x < numOfBars - 1 and df.iloc[x, 0] != self.dateOfEntry :
        #     x = x + 1
        self.entryPrice = df.iloc[x, 4]

        if self.direction == 'long':
            self.takeProfit = riskRewardRatio * (self.entryPrice - self.stopLoss) + self.entryPrice
        else:
            self.takeProfit = self.entryPrice - riskRewardRatio * (self.stopLoss - self.entryPrice)



        self.positionSize = equity * maxLossPerTrade / (abs(self.entryPrice - self.stopLoss) / self.entryPrice) # position size in dollars

        self.positionSize = min(self.positionSize, equity)

        while  x < numOfBars and x < index + 24 and not((df.iloc[x, 3] < self.stopLoss and df.iloc[x, 2] > self.stopLoss) 
        or (df.iloc[x, 3] < self.takeProfit and df.iloc[x, 2] > self.takeProfit)):
            x = x + 1
        
        if x == numOfBars:
            x = x - 1

        self.endIndex = x

        global fig
        global  fig1
        if isDownToken:
            f = fig1
        else:
            f = fig

        ## profit rectangle
        f.add_shape(
            type="rect",
            x0=dateOfEntry, y0=self.entryPrice, x1=df.iloc[x, 0], y1=self.takeProfit,
            line=dict(
                color="grey",
                width=0.5,
            ),
            opacity=0.2,
            fillcolor="green",
        )

        ## loss rectangle
        f.add_shape(
            type="rect",
            x0=dateOfEntry, y0=self.entryPrice, x1=df.iloc[x, 0], y1=self.stopLoss,
            line=dict(
                color="grey",
                width=0.5,
            ),
            opacity=0.2,
            fillcolor="red",
        )

        ## profit line
        f.add_shape(type="line",
            x0=dateOfEntry, y0=self.takeProfit, x1=df.iloc[x, 0], y1=self.takeProfit,
            line=dict(
                color="green",
                width=1.5,
                dash="solid",
            )
        )
        
        ## stop los line 
        f.add_shape(type="line",
            x0=dateOfEntry, y0=self.stopLoss, x1=df.iloc[x, 0], y1=self.stopLoss,
            line=dict(
                color="red",
                width=1.5,
                dash="solid",
            )
        )
        
        ## entry line
        f.add_shape(type="line",
            x0=dateOfEntry, y0=self.entryPrice, x1=df.iloc[x, 0], y1=self.entryPrice,
            line=dict(
                color="grey",
                width=1.5,
                dash="dash",
            )
        )



    # def close(currentPrice):

    
    # execute returns amount earned or lost on closure of position, if lost then its negative

    def execute(self):
        # x = self.index
        # while x < numOfBars and df.iloc[x, 0] != self.dateOfEntry:
        #     x = x + 1

        # while x < numOfBars and not((df.iloc[x, 3] < self.stopLoss and df.iloc[x, 2] > self.stopLoss) or (df.iloc[x, 3] < self.takeProfit and df.iloc[x, 2] > self.takeProfit)):
        #     x = x + 1
        x = self.endIndex
        df = self.dataFrame

        if self.endIndex == self.index:
            return 0

        
        afterFee = 1 - self.fee
        position = self.positionSize * afterFee /self.entryPrice

        if self.direction == 'long':
            
            # point of finalization
            if df.iloc[x, 2] >= self.takeProfit:
                return (afterFee * self.takeProfit - self.entryPrice) * position
            elif df.iloc[x, 3] <= self.stopLoss:
                return (afterFee * self.stopLoss - self.entryPrice) * position
            else:
                return (afterFee * df.iloc[x, 4] - self.entryPrice) * position
        else: # short

            # point of finalization
            if df.iloc[x, 3] <= self.takeProfit:
                return (self.entryPrice - afterFee * self.takeProfit) * position
            elif df.iloc[x, 2] >= self.stopLoss:
                return (self.entryPrice - afterFee * self.stopLoss) * position
            else: 
                return (self.entryPrice - afterFee * df.iloc[x, 4]) * position



#### strategy testing




def shortCond(x): # condition to open trade x = index of candle from df dataframe
    
    if time(x).hour == 2 and vwapDf[x-2] < vwapDf[x-1] and close(x, df) < open(x, df) and close(x, df) < vwapDf[x]:
        return True
    else:
        return False

def longCond(x):
    if time(x).hour == 2 and vwapDf[x-2] > vwapDf[x-1] and close(x, df) > open(x, df) and close(x, df) > vwapDf[x]:
        return True
    else:
        return False

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


def testStrat(maxLossPerTrade = 0.02, equity = 100000, fee = 0.00075):  # binance taker fee 0.075% 

    equityHist = []
    equityHist.append(equity)

    

    for x in range(0, numOfBars):
        # print(str(round(x*100/numOfBars)) + '%')
        printProgressBar(x, numOfBars)
        
        if shortCond(x): ## equals making long on DOWN token
            # pos = Position(x, equity, maxLossPerTrade, 'short', time(x), hh[x], 2, 0.00075)
            pos = Position(x, equity, maxLossPerTrade, 'long', time(x), lowestLow(7, dfDown)[x], 2, 0.00075, dfDown, True)
            equityHist.append(equityHist[-1] + pos.execute())
        
        if longCond(x): 
            pos = Position(x, equity, maxLossPerTrade, 'long', time(x), lowestLow(7, df)[x], 2, 0.00075, df, False)
            equityHist.append(equityHist[-1] + pos.execute())


    
    plt.plot(equityHist, marker = 'o')
    fig.show(config = dict({'scrollZoom': True}))
    fig1.show(config = dict({'scrollZoom': True}))
    # fig3.show(config = dict({'scrollZoom': True}))

    plt.show()

    



testStrat()

    




# short = Position(100, 'short', datetime(2022, 10, 5, 2), 20468, 2)

        


