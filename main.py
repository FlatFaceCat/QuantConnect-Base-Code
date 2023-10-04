# region imports
from AlgorithmImports import *
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta, time
import collections
from order_codes import (OrderTypeCodes, OrderDirectionCodes, OrderStatusCodes)
from decimal import *
# endregion


# Globals                  
PT = 0.005 # percent
SL = 0.005 # percent


class Trialcode(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 10, 6)
        self.SetEndDate(2023, 10, 11)
        self.SetCash(100000)  # Set Strategy Cash

        self.new_day = True
        self.contract = None

        # Subscribe and set our expiry filter for the futures chain
        # Find more symbols here: http://quantconnect.com/data
        futureES = self.AddFuture(Futures.Indices.SP500EMini, Resolution.Minute)
        futureES.SetFilter(TimeSpan.Zero, TimeSpan.FromDays(185))         

    def OnData(self, slice):
        self.InitUpdateContract(slice)

    def InitUpdateContract(self, slice):
        # Reset daily - everyday we check whether futures need to be rolled
        if not self.new_day:
            return
        # rolling 3 days before expiry
        if self.contract != None and (self.contract.Expiry - self.Time).days >= 3:
            return

        for chain in slice.FutureChains.Values:
            # If we trading a contract, send to log how many days until the contract's expiry
            if self.contract != None:
                self.Log('Expiry days away {} - {}'.format((self.contract.Expiry -
                         self.Time).days, self.contract.Expiry))

                # Reset any open positions based on a contract rollover.
                self.Log('RESET: closing all positions')
                self.Liquidate()

            # get list of contracts
            contracts = list(chain.Contracts.Values)
            # [contract for contract in chain]
            chain_contracts = list(contracts)
            # order list of contracts by expiry date: newest --> oldest
            chain_contracts = sorted(chain_contracts, key=lambda x: x.Expiry)

            # pick out contract and log contract name
            self.contract = chain_contracts[1]
            self.Log("Setting contract to: {}".format(
                self.contract.Symbol.Value))

            # Set up consolidators.
            one_min = TradeBarConsolidator(TimeSpan.FromMinutes(1))
            one_min.DataConsolidated += self.OnOneMin
            self.SubscriptionManager.AddConsolidator(
                self.contract.Symbol, one_min)
            five_min = TradeBarConsolidator(TimeSpan.FromMinutes(5))
            five_min.DataConsolidated += self.OnFiveMin
            self.SubscriptionManager.AddConsolidator(
                self.contract.Symbol, five_min)
            fifteen_min = TradeBarConsolidator(TimeSpan.FromMinutes(15))
            fifteen_min.DataConsolidated += self.OnFifteenMin
            self.SubscriptionManager.AddConsolidator(
                self.contract.Symbol, fifteen_min)
            thirty_min = TradeBarConsolidator(TimeSpan.FromMinutes(30))
            thirty_min.DataConsolidated += self.OnThirtyMin
            self.SubscriptionManager.AddConsolidator(
                self.contract.Symbol, thirty_min)

            # reset the new day flag
            self.new_day = False
            self.Liquidate()

    def OnOneMin(self, sender, bar):
        if bar.Symbol == self.contract.Symbol:
            openPrice = bar.Open
            highPrice = bar.High
            lowPrice = bar.Low
            closePrice = bar.Close
        pass

    def OnFiveMin(self, sender, bar):
        if bar.Symbol == self.contract.Symbol:
            openPrice = bar.Open
            highPrice = bar.High
            lowPrice = bar.Low
            closePrice = bar.Close
        pass

    def OnFifteenMin(self, sender, bar):
        if bar.Symbol == self.contract.Symbol:
            openPrice = bar.Open
            highPrice = bar.High
            lowPrice = bar.Low
            closePrice = bar.Close
        pass

    def OnThirtyMin(self, sender, bar):
        if bar.Symbol == self.contract.Symbol:
            openPrice = bar.Open
            highPrice = bar.High
            lowPrice = bar.Low
            closePrice = bar.Close
        pass

    def OnEndOfDay(self):
        self.new_day = True

    def OnOrderEvent(self, orderEvent):
        """
        This function is triggered automatically every time an order event occurs.
        """
        
        self.Log(str(orderEvent))  
        
        if OrderStatusCodes[orderEvent.Status] == 'Submitted':
            return

        k = str(orderEvent.Symbol.Value)
        symbol = str(orderEvent.Symbol)
        
        if (not k in self.order_tickets.keys()): 
            self.Log('missing key in order tickets: {}'.format(k))
            self.Log('order tickets keys: {}'.format(self.order_tickets.keys()))
            return
        
        elif (k in self.order_tickets.keys()):
        
            orderData = self.order_tickets[k]
            orig_order_id = orderData.ticket.OrderId
            order = self.Transactions.GetOrderTicket(orig_order_id)
            
            # sometimes order is nonetype due to security price
            # is equal to zero
            #------------------------------------------------------#
            if not order: 
                self.Log('order is nonetype: {}'.format(k))
                del self.order_tickets[k] # delete order ticket data  
                return
                
            # if order is filled but bracket order not submitted,
            # submit bracket order
            #------------------------------------------------------#
            if (OrderStatusCodes[order.Status]=='Filled') and \
                (not orderData.bracket_submit):
                    
                if (orderEvent.OrderId == orig_order_id):
            
                    price = orderEvent.FillPrice
                    qty = orderEvent.FillQuantity
                    #qty = self.CalculateOrderQuantity(k, 0.0)
                    
                    profit_target = price * d.Decimal(1+PT)
                    limitTicket = self.LimitOrder(symbol, -1*qty, profit_target)
                    self.order_tickets[k].add_limit_order(limitTicket)
                    
                    stop_loss = price * d.Decimal(1-SL)
                    stopTicket = self.StopMarketOrder(symbol, -1*qty, stop_loss)
                    self.order_tickets[k].add_stop_market_order(stopTicket)
                    
                    self.order_tickets[k].is_bracket()
                    
                    self.Log('bracket order submitted: {}'.format(self.Time, k))
                    
            # Otherwise, one of the exit orders was filled,
            # so cancel the open orders
            #------------------------------------------------------#
            elif (orderData.bracket_submit) and \
                (OrderStatusCodes[orderEvent.Status]=='Filled'):
                self.Log('cancelling bracket orders for: {}'.format(self.Time, k))
                self.Transactions.CancelOpenOrders(symbol)
                self.order_tickets[k].bracket_submit=False
                del self.order_tickets[k]    
