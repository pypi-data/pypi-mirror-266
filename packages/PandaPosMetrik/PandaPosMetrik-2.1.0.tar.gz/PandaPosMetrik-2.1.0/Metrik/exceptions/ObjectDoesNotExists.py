
class ObjectDoesNotExists(Exception):
    
    def __init__(self, model, **filter_kwargs) -> None:
        self.model = model.__name__
        self.filter_kwargs = filter_kwargs
        
        super().__init__(self.__str__())
        
        
    def __str__(self) -> str:
        return f"{self.model} By {self.filter_kwargs} does not exists"