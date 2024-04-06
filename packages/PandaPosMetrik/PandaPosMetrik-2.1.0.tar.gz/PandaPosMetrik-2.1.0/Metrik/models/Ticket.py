import datetime

from Metrik.models.ORMModel import Model


class Order(Model):
    Id: int
    TicketId: int
    WarehouseId: int
    DepartmentId: int
    TerminalId: int
    MenuItemId: int
    MenuItemName: str
    PortionName: str
    Price: float
    Quantity: float
    PortionCount: int
    Locked: bool
    CalculatePrice: bool
    DecreaseInventory: bool
    IncreaseInventory: bool
    OrderNumber: int
    CreatingUserName: str
    CreatedDateTime: datetime
    LastUpdateTime: datetime
    AccountTransactionTypeId: int
    ProductTimerValueId: int
    GroupTagName: str
    GroupTagFormat: str
    Separator: str
    PriceTag: str
    Tag: str
    DisablePortionSelection: bool
    OrderUid: str
    Taxes: str
    OrderTags: str
    OrderStates: str
    

class Ticket(Model):
    Id: int
    LastUpdateTime: datetime.datetime
    TicketVersion: datetime.datetime
    TicketUid: str
    TicketNumber: str
    Date: datetime.datetime
    LastOrderDate: datetime.datetime
    LastPaymentDate: datetime.datetime
    PreOrder: bool
    IsClosed: bool
    IsLocked: bool
    RemainingAmount: float
    TotalAmount: float
    DepartmentId: int
    TerminalId: int
    TicketTypeId: int
    Note: str
    LastModifiedUserName: str
    TicketTags: str
    TicketStates: str
    TicketLogs: str
    LineSeparators: str
    ExchangeRate: float
    TaxIncluded: bool
    Name: str
    TransactionDocument_Id: int
    IsOpened: bool
    TotalAmountPreTax: float
    orders: list[Order]
    payments: list['Payment']
    Status: int
    

class Payment(Model):
    Id: int
    TicketId: int
    PaymentTypeId: int
    DepartmentId: int
    Name: str
    Description: str
    Date: datetime.datetime
    AccountTransactionId: int
    Amount: float
    TenderedAmount: float
    UserId: int
    TerminalId: int
    ExchangeRate: float
    PaymentData: str
    CanAdjustTip: bool
    AccountTransactionId: int
    AccountTransaction_AccountTransactionDocumentId: int
    
    
    