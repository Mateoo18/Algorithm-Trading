# region imports
from AlgorithmImports import *
# endregion

class CalmFluorescentPinkSeahorse(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2021, 2, 7)
        self.SetEndDate(2022,2, 7)
        self.SetCash(100000)
        self.qqq=self.AddEquity("VOO",Resolution.Hour).Symbol#funkcja add equity przygotowuje algorytm do pracy z konkretnym aktywem, pozwalając na analizę i podejmowanie decyzji inwestycyjnych, Resolution mowi co ile dane beda aktualizowane
        self.entryTicket=None
        self.stopMarketTicket=None
        self.entryTime=datetime.min
        self.stopMarketOrderFillTime=datetime.min
        self.HighestPRice=0
    

    def OnData(self, data: Slice):
     # co robi algorytm
     # czekaj 30 dni po ostatniej sprzedazy
     if (self.Time - self.stopMarketOrderFillTime).days < 30:
         return
      
     price = self.Securities[self.qqq].Price
 
     # wyslij zlecenie limit order
     if not self.Portfolio.Invested and not self.Transactions.GetOpenOrders(self.qqq):
         quantity = self.CalculateOrderQuantity(self.qqq, 0.9)#sprawdzamy ile akcji bedzie za 90 % naszego portfela
         self.entryTicket = self.LimitOrder(self.qqq, quantity, price, "Entry Order")
         self.entryTime=self.Time
         self.Log("KUPIONE")
        # ustaw zlecenie limit order na wieksze jesli nie zostanie uzupelnione przez 1 dzien
     if(self.Time-self.entryTime).days>1 and self.entryTicket.Status!=OrderStatus.Filled:
            self.Log("robie update")
            self.entryTime=self.Time
            updateFields=UpdateOrderFields() 
            updateFields.LimitPrice=price
            self.entryTicket.Update(UpdateFields)
     # przesun do gory stop price
     if self.stopMarketTicket is not None and self.Portfolio.Invested:
         if price>self.HighestPRice:
             self.HighestPRice=price
             updateFields=UpdateOrderFields()
             updateFields.StopPrice=price*0.95
             self.stopMarketTicket.Update(updateFields)

     pass



    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status!=OrderStatus.Filled:
            return
    
        #ustaw stop loss zlecenie jesli limit order zostaw ustawiony
        if self.entryTicket is not None and self.entryTicket.OrderId==orderEvent.OrderId:
             self.stopMarketTicket=self.StopMarketOrder(self.qqq,-self.entryTicket.Quantity, 0.95*self.entryTicket.AverageFillPrice)
        #ustaw czas po zrobieniu stop loss(30 dni)
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId==orderEvent.OrderId:
             self.stopMarketOrderFillTime=self.Time
             self.HighestPRice=0
        pass
