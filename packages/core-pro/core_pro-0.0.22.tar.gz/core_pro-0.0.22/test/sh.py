from src.core_pro import Sheet
from src.core_pro.ultilities import update_df
import pandas as pd


sh = '1PdpE_ilQZdEp9fGG6McReP1fUEwfZNmskahBBOBItp0'
Sheet(sh).update_value_single_axis('aaa', 'test', 'A1')

d = {'col1': [1, 2], 'col2': [3, 4]}
df = pd.DataFrame(data=d)
update_df(df, 'test', sh)
