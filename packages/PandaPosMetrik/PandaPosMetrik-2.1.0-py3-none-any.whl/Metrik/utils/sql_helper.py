import pyodbc

from Metrik.models.Ticket import Orders, Tickets

class SQLHelper:
    def __init__(self, server: str, port: str, db_name: str, driver: str, user: str = "", password: str = ""):
        self.server = server
        self.port = port
        self.db_name = db_name
        self.driver = driver
        self.user = user
        self.password = password
        
        self.connection = pyodbc.connect(
            driver=self.driver,
            database=self.db_name,
            server=self.server,
            user=user,
            password=self.password,
        )
    
    
    def get_orders(self):
        orders = Orders.objects.all()
        
        return orders
    
    def get_orders_by_ticket_id(self, ticket_id):
        orders = Orders.objects.filter(TicketId=ticket_id)
        
        return orders
    
    
    def get_tickets(self) -> list[Tickets]:
        tickets: list[Tickets] = Tickets.objects.all()
        for ticket in tickets:
            ticket.orders = self.get_orders_by_ticket_id(ticket.Id)
            
        return tickets
    
    def get_tickets_by_status(self, status: int) -> list[Tickets]:
        tickets: list[Tickets] = Tickets.objects.filter(Status=status)
        for ticket in tickets:
            ticket.orders = self.get_orders_by_ticket_id(ticket.Id)
        return tickets
    
    
        
        
