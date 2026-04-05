
# Знайти дублікати за order_id, видалити їх, 
# а потім оцінити, як змінилася сумарна 
# виручка по кожному city (до/після).

import pandas as pd


FILE_NAME = "sales_data.csv"

df = pd.read_csv(FILE_NAME)
df = df.drop(columns=['Order Date', 'Product_ean', 'catégorie', 
                     'Quantity Ordered', 'Price Each', 'Cost price',
                     'margin', 'Product'])

df = df.rename(columns={"Order ID": "order_id", "Purchase Address": "address"})

df['city'] = df['address'].str.split(',').str[1].str.strip()
df = df.drop(columns=['address'])

# before
sum_before = df.groupby('city')['turnover'].sum()
sum_before = (sum_before / 1000).astype(int)
sum_before.name = "turnover in 1k usd"
print("Before deleting the duplicates:")
print(sum_before)

# after
df_no_duplicates = df.drop_duplicates(subset='order_id', keep='first')
sum_after = df_no_duplicates.groupby('city')['turnover'].sum()
sum_after = (sum_after / 1000).astype(int)
sum_after.name = "turnover in 1k usd"
print("\nAfter deleting the duplicates:")
print(sum_after)

# diff
diff = sum_before - sum_after
print("\nDifference:")
print(diff)


