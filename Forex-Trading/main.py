# region imports
from System.Drawing import Color
from AlgorithmImports import *
# endregion

class SleepyRedZebra(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2022, 3, 4)
        self.SetCash(100000)
        self.pair=self.AddForex("EURUSD",Resolution.Daily,Market.Oanda).Symbol
        self.bb=self.BB(self.pair, 20, 2)#20 dni ,2 % odchylenia
        stockPlot=Chart("Trade Plot")
        stockPlot.AddSeries(Series("Buy",SeriesType.Scatter,"$",Color.Green,ScatterMarkerSymbol.Triangle))
        stockPlot.AddSeries(Series("Sell",SeriesType.Scatter,"$",Color.Red,ScatterMarkerSymbol.Triangle))
        stockPlot.AddSeries(Series("Liquidate",SeriesType.Scatter,"$",Color.Blue,ScatterMarkerSymbol.Triangle))
        self.AddChart(stockPlot)
    def OnData(self, data: Slice):
        if not self.bb.IsReady:
            return
        price=data[self.pair].Price
        self.Plot("TradePlot","Price",price)
        self.Plot("TradePlot","MiddleBand",self.bb.MiddleBand.Current.Value)
        self.Plot("TradePlot","UpperBand",self.bb.UpperBand.Current.Value)
        self.Plot("TradePlot","LowerBand",self.bb.MiddleBand.Current.Value)
        if not self.Portfolio.Invested:
            if self.bb.LowerBand.Current.Value>price:
                self.SetHoldings(self.pair,1)
                self.Plot("TradePlot", "Buy",price)
            elif self.bb.UpperBand.Current.Value<price:
                self.SetHoldings(self.pair,-1)
                self.Plot("TradePlot", "Sell",price)
        else:
            if self.Portfolio[self.pair].IsLong:
                if self.bb.MiddleBand.Current.Value<price:
                    self.Liquidate()
                    self.Plot("TradePlot", "Liquidate",price)
                elif self.bb.MiddleBand.Current.Value>price:
                 self.Liquidate()
                 self.Plot("TradePlot", "Liquidate",price)
