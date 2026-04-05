Суть завдання полягає в очищенні даних від дуплікатів та порівнянні результатів "до" та "після". <br>
Чому виникають дублікати? Це може бути зумовлено відсутністю унікальних індексів в базі даних.
<br>Для видалення дуплікатів у pandas використовується наступний <a href="https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html#pandas.DataFrame.drop_duplicates">метод</a>:

``` DataFrame.drop_duplicates(subset=None, *, keep='first') ```

subset column label or iterable of labels, optional
Only consider certain columns for identifying duplicates, by default use all of the columns.

keep{‘first’, ‘last’, False}, default ‘first’
Determines which duplicates (if any) to keep.

+ ‘first’ : Drop duplicates except for the first occurrence.
+ ‘last’ : Drop duplicates except for the last occurrence.
+ False : Drop all duplicates.



