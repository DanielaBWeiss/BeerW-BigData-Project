{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "34"
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import numpy as np\n",
    "import pandas as pd\n",
    "\n",
    "\n",
    "data = pd.read_csv(\"../data/df_2_text_processed.csv\")\n",
    "\n",
    "data[~(data.guest_count == 0)]\n",
    "\n",
    "bars = data.bar_id.unique()\n",
    "\n",
    "data['total_sales_before_tax'] = data.groupby('order_id')['sales_before_tax'].transform('sum')\n",
    "data['total_sales_inc_tax'] = data.groupby('order_id')['sales_inc_tax'].transform('sum')\n",
    "data['total_orders'] = data.groupby('order_id')['order_id'].transform('size')\n",
    "\n",
    "features = ['bar_id', 'guest_count']\n",
    "tables = data.drop_duplicates(subset='order_id', keep='first')\n",
    "tables.set_index('order_id', inplace=True)\n",
    "tables = tables[features]\n",
    "\n",
    "desc = tables.groupby('bar_id').guest_count.describe()\n",
    "desc_columns = ['guest_count_count', 'guest_count_mean', 'guest_count_std', 'guest_count_min', \\\n",
    "                'guest_count_25%', 'guest_count_50%', 'guest_count_75%', 'guest_count_max']\n",
    "desc.columns = desc_columns\n",
    "tables = tables.reset_index().merge(desc, on='bar_id').set_index(tables.index).drop(['order_id'], axis=1)\n",
    "\n",
    "bars_data = tables.drop_duplicates(subset='bar_id', keep='first')[['bar_id'] + desc_columns]\n",
    "bars_data.set_index('bar_id', inplace=True)\n",
    "\n",
    "assert(len(bars) == len(bars_data))\n",
    "\n",
    "bars_data = bars_data[(bars_data.guest_count_max != 0) & (bars_data.guest_count_max != 1)]\n",
    "\n",
    "'''\n",
    "def filter_sales(row):\n",
    "    if row[\"guest_count\"] > row[\"total_sales_before_tax\"] and row[\"total_sales_before_tax\"] != 0.0:\n",
    "        return True\n",
    "    return False\n",
    "\n",
    "drops = data[data.apply(lambda x: filter_sales(x), axis=1)]\n",
    "bad_bars = drops.groupby(\"bar_id\").count()\n",
    "bad_bars = bad_bars[bad_bars[\"order_id\"] > 20]\n",
    "bars_data = bars_data[~bars_data.index.isin(list(bad_bars.index))]\n",
    "\n",
    "bad_data = bars_data[(bars_data[\"guest_count_75%\"] <= 1) | ( bars_data['guest_count_25%'] == 0)]\n",
    "bars_data2 = bars_data[~bars_data.index.isin(list(bad_data.index))]\n",
    "best_bars = bars_data2[(bars_data2['guest_count_50%'] >= 1 ) &(bars_data2.guest_count_std <= 1.5)]\n",
    "'''\n",
    "#last_bars = best_bars[best_bars[\"guest_count_min\"] != 0]\n",
    "\n",
    "#last_bars.to_csv(\"df_3_text_processed.csv\", index=False)\n",
    "\n",
    "best_bars = data[data.bar_id.isin(bars_data.index)]\n",
    "best_bars.to_csv(\"../data/df_3_text_processed.csv\", index=False)\n",
    "print(\"There are \", best_bars.bar_id.nunique(), \" Bars left\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}