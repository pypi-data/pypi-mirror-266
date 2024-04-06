from utils.sql_helper import SQLHelper

sqlHelper = SQLHelper("127.0.0.1", 1433, "PandaBOS", "SQL Server")

tickets = sqlHelper.get_tickets()


total_amount_by_date = {}
for ticket in tickets:
    total_amount_by_date[ticket.Date.strftime("%Y-%m-%d")] = total_amount_by_date.get(ticket.Date.strftime("%Y-%m-%d"), 0) + ticket.TotalAmount
    
for ticket in tickets:
    print(ticket.orders)