//+------------------------------------------------------------------+
//| Dashboard Connector EA                                           |
//| Sends account data to dashboard backend every 60 seconds          |
//+------------------------------------------------------------------+
#property copyright "MT5 Dashboard"
#property link      ""
#property version   "1.00"
#property strict

// Input parameters
input string   DashboardURL = "http://localhost:5000";  // Dashboard Server URL
input int      UpdateInterval = 60;                     // Update interval (seconds)
input string   AccountNickname = "";                    // Optional account nickname
input bool     LogDebug = false;                        // Enable debug logging

// Global variables
int      httpRequestHandle;
datetime lastUpdateTime;
string   endpoint;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Check if URL is valid
   if(StringLen(DashboardURL) == 0)
   {
      Print("Error: DashboardURL not set");
      return(INIT_PARAMETERS_INCORRECT);
   }
   
   // Build endpoint
   endpoint = DashboardURL + "/socket.io/";
   
   Print("Dashboard Connector EA initialized");
   Print("Server: ", DashboardURL);
   Print("Update interval: ", UpdateInterval, " seconds");
   
   // Send initial data
   SendAccountData();
   lastUpdateTime = TimeCurrent();
   
   // Create timer for periodic updates
   EventSetTimer(UpdateInterval);
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   Print("Dashboard Connector EA stopped");
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
   SendAccountData();
}

//+------------------------------------------------------------------+
//| Send account data to dashboard                                   |
//+------------------------------------------------------------------+
void SendAccountData()
{
   // Get account info
   long accountLogin = AccountInfoInteger(ACCOUNT_LOGIN);
   double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double accountEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   double accountProfit = AccountInfoDouble(ACCOUNT_PROFIT);
   double accountMargin = AccountInfoDouble(ACCOUNT_MARGIN);
   double accountMarginFree = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   
   // Get floating PnL from open positions
   double floatingPnL = 0;
   int totalPositions = PositionsTotal();
   
   for(int i = 0; i < totalPositions; i++)
   {
      string symbol = PositionGetSymbol(i);
      if(symbol != "")
      {
         double posProfit = PositionGetDouble(POSITION_PROFIT);
         floatingPnL += posProfit;
      }
   }
   
   // Build JSON payload
   string jsonPayload = "{";
   jsonPayload += "\"timestamp\":\"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\",";
   jsonPayload += "\"accounts\":[";
   jsonPayload += "{";
   jsonPayload += "\"account_id\":\"" + IntegerToString(accountLogin) + "\",";
   jsonPayload += "\"login\":\"" + IntegerToString(accountLogin) + "\",";
   jsonPayload += "\"balance\":" + DoubleToString(accountBalance, 2) + ",";
   jsonPayload += "\"equity\":" + DoubleToString(accountEquity, 2) + ",";
   jsonPayload += "\"floating_pnl\":" + DoubleToString(floatingPnL, 2) + ",";
   jsonPayload += "\"margin\":" + DoubleToString(accountMargin, 2) + ",";
   jsonPayload += "\"margin_free\":" + DoubleToString(accountMarginFree, 2) + ",";
   jsonPayload += "\"positions_count\":" + IntegerToString(totalPositions) + ",";
   jsonPayload += "\"source\":\"mt5_ea\"";
   jsonPayload += "}";
   jsonPayload += "],";
   jsonPayload += "\"source\":\"mt5_ea\"";
   jsonPayload += "}";
   
   if(LogDebug)
   {
      Print("Sending data: ", jsonPayload);
   }
   
   // Send HTTP POST request
   char data[], result[];
   string headers;
   int res;
   
   // Convert string to char array
   StringToCharArray(jsonPayload, data);
   
   // Create HTTP request
   httpRequestHandle = WebRequest(
      "POST",
      endpoint,
      "Content-Type: application/json\r\n",
      5000,  // Timeout in milliseconds
      data,
      result,
      headers
   );
   
   // Check result
   if(httpRequestHandle == -1)
   {
      Print("Error sending data. Error code: ", GetLastError());
   }
   else
   {
      string response = CharArrayToString(result);
      if(LogDebug)
      {
         Print("Server response: ", response);
      }
      else
      {
         Print("Data sent successfully. Account: ", accountLogin, 
               " Equity: $", accountEquity, 
               " PnL: $", floatingPnL);
      }
   }
}

//+------------------------------------------------------------------+
//| Trade event handler                                              |
//+------------------------------------------------------------------+
void OnTrade()
{
   // Send update immediately on trade events
   SendAccountData();
   lastUpdateTime = TimeCurrent();
}