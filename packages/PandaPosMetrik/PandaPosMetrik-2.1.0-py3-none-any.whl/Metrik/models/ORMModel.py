from Metrik.models.OrmManager import OrmManager
from typing import ClassVar, List, TypeVar, get_args, get_type_hints
import datetime
from typing_extensions import Self
T = TypeVar('T', bound='Model')


class ModelMeta(type):
    """Model sınıfları için metaclass."""
    
    def __new__(cls, name, bases, dct):
        # Sınıf adını kullanarak tablo adını oluştur ve sınıf sözlüğüne ekleyin
        dct['__tablename__'] = name.lower()
        dct['__tablename_plural__'] = name.lower() + "s"
        # type.__new__ çağrısıyla yeni sınıfı oluşturun
        return type.__new__(cls, name, bases, dct)





class Model(metaclass=ModelMeta):
    objects: ClassVar[OrmManager[Self]] = OrmManager()
    
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)
        
        hints = get_type_hints(self)
        # Sonra tarih tipindekileri dönüştürün
        for key, hint_type in hints.items():
            if hint_type == datetime.datetime:
                attr_value = getattr(self, key, None)  # Varsayılan olarak None dön
                if attr_value and isinstance(attr_value, str):  # Değer string ve atanmışsa
                    try:
                        # Tarih formatı kontrolü ve dönüştürme
                        setattr(self, key, datetime.datetime.fromisoformat(attr_value))
                    except ValueError:
                        # Geçersiz tarih formatı, uygun bir hata yönetimi ekleyin
                        pass