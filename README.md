# QuantConnect-Base-Code
Base code for dealing with futures and specific candle sizes on Quant connect 

### How to:
Please follow steps here: https://github.com/FlatFaceCat/QuantConnect-Local-Setup-Guide to follow steps on working with Quant connect and Lean. 

### Notes
- This is base code that works with Future contracts (in this case ES) and takes into count the contract expiring and roll overs 
- This base code has pre set consolidators that trigger at one, five, fifteen and thirty minute intervals. (OHLC for each candle range is defined)
- This is purely base code that has no triggers and will just cycle through all available data feeds. 