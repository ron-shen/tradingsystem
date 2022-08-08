import pandas as pd
from Event.event import Direction
from datetime import datetime, timezone


class Portfolio:
    """        
    Portfolio consumes BarEvent and FillEvent to update the portfolio
    """
    def __init__(self, initial_cash, db_client=None):
        self.cash = initial_cash
        self.init_cash = initial_cash
        self.market_value = 0 #market value excluding cash
        """
        RLZD_P : Realized profit
        UNRLZD_P: Unrealized profit
        """
        self.fin_instruments = pd.DataFrame(columns=['POS', 'AVG_PRICE', 
                                                     'MKT_VAL', 'RLZD_P',
                                                     'UNRLZD_P'])
        self.db_client = db_client
    
    
    def on_bar(self, bar_event):
        """
        consumes BarEvent to update the portfolio value
        """
        if self._ticker_exist(bar_event.ticker):
            fin_instr = self.fin_instruments.loc[bar_event.ticker]
            old_market_value = fin_instr.MKT_VAL
            fin_instr.MKT_VAL = bar_event.close_price * fin_instr.POS
            fin_instr.UNRLZD_P = (bar_event.close_price - fin_instr.AVG_PRICE) \
                                 * fin_instr.POS
                                 
            self.market_value += fin_instr.MKT_VAL - old_market_value

            
    def on_fill(self, fill_event):
        #consumes FillEvent to update the portfolio
        if not self._ticker_exist(fill_event.ticker):
            #print("create a new fin instr")
            self._create_fin_instr(fill_event)      
                        
        else:
            #print("modify a new fin instr")
            self._modify_fin_instr(fill_event)


    def _create_fin_instr(self, fill_event):
        #create new entry for the ticker symbol and store it in fin_instruments
        market_value = fill_event.quantity * fill_event.price
        
        if fill_event.direction == Direction.SHORT:
            market_value *= -1
            fill_event.quantity *= -1

        fin_instr = [fill_event.quantity, fill_event.price, market_value, 0, 0]
        self.fin_instruments.loc[fill_event.ticker] = fin_instr
        self.market_value += market_value
        self.cash -= market_value


    def _modify_fin_instr(self, fill_event):
        fin_instr = self.fin_instruments.loc[fill_event.ticker]
        old_market_value = fin_instr.MKT_VAL

        if fill_event.direction == Direction.LONG:
            #add POS for a long position
            if fin_instr.POS > 0:
                total_cost = fin_instr.POS * fin_instr.AVG_PRICE + fill_event.quantity * fill_event.price 
                fin_instr.AVG_PRICE = total_cost / (fin_instr.POS + fill_event.quantity)

            #buy back a short position
            elif fin_instr.POS < 0:
                fin_instr.RLZD_P += (fin_instr.AVG_PRICE - fill_event.price) * fill_event.quantity                                   

            fin_instr.POS += fill_event.quantity                        
            self.cash -= fill_event.quantity * fill_event.price

        #fill_event.direction == Direction.SHORT:    
        else:
            #sell POS for a long position
            if fin_instr.POS > 0:       
                fin_instr.RLZD_P += (fill_event.price - fin_instr.AVG_PRICE) * fill_event.quantity                                        

            #add POS for a short position
            elif fin_instr.POS < 0:
                total_cost = -fin_instr.POS * fin_instr.AVG_PRICE + fill_event.quantity * fill_event.price                  
                fin_instr.AVG_PRICE = total_cost / (-fin_instr.POS + fill_event.quantity)

            fin_instr.POS -= fill_event.quantity
            self.cash += fill_event.quantity * fill_event.price

        fin_instr.UNRLZD_P = (fill_event.price - fin_instr.AVG_PRICE) * fin_instr.POS
        fin_instr.MKT_VAL = fin_instr.POS * fill_event.price
        self.market_value += fin_instr.MKT_VAL - old_market_value

        #clear the instrument if all pos was sold/bought back
        if fin_instr.POS == 0:
            self.fin_instruments.drop(labels=fill_event.ticker, axis=0, inplace=True)

    
    def get_asset_val(self):
        return self.cash + self.market_value

    
    def get_fin_instrument(self, ticker):
        """
        return the whole instrucment information of specific ticker.
        return None if the ticker symbol does not exist
        """
        if not self._ticker_exist(ticker):
            return None
        
        return self.fin_instruments.loc[ticker]

    
    def _ticker_exist(self, ticker):
        if ticker in self.fin_instruments.index:
            return True   
        
        return False
        
    def save_to_db(self, time):
        if self.db_client is not None:
            query = ("INSERT INTO Portfolio (Datetime, Cash, MarketValue, AssetValue)"
                    "VALUES (%s, %s, %s, %s)"
            )
            data = (time, self.cash, float(self.market_value), float(self.get_asset_val()))
            cursor = self.db_client.cursor()
            cursor.execute(query, data)
            self.db_client.commit()         
