# nasdaq_stock
nasdaq stock pull down

# How to use
```
>>>from nasdaq_stock import nasdaq_stock as ns
```
or
```
>>>from nasdaq_stock import nasdaq_stock   
>>>nasdaq_stock.stock(‘spyd’)              
```
or
```
>>>spyd = nasdaq_stock.stock(‘spyd’)       
```

This will return string data and a dictionary of that data.
Current data fields are:                   
ticker: The stock or id of that ticker.    
date: The date when the stock was queried. 
time: The time when the stock was taken. This can be helpful if you are trying to do minute-by-minute data gathering
price: The current price or bid price      
ask: The current ask price                 
high: The high of the day                  
low: The low of the day                    
previous_close: The previous closing form the last day. Not to be confused with last ask price
volume: Volume of shares for the current day. 