Библиотека для сравнивания ФД из ФН и ОФД
## Установка библиотеки
```cmd
pip install ofdcomparer
```


## Примеры использования

#### Импорт и инициализация объектов
```python
from ofdcomparer.dto10 import DTO10Helper
from ofdcomparer.compare_ffd import ComparerOfd

dto10 = DTO10Helper()
comparer_ofd = ComparerOfd(dto10=dto10)
```

#### Сравнивание документов
```python
# получаем РНМ
rnm = dto10.get_rnm_number()
# получаем номер ФН 
fn_number = dto10.get_fn_number()
# получаем последний фискальный документ по номеру 
fd_from_fn = dto10.get_fd_from_fn(fd=dto10.get_last_fiscal_document_number)
# получаем ФД с ОФД по номеру ФН и РНМ и сравниваем с ФД с ФН
comparer_ofd.compare_last_fd_in_fn_and_ofd(rnm=rnm, fn=fn, fd=fd_from_fn)
```
