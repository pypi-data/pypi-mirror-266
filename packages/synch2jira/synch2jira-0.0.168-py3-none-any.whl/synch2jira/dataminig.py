import pandas as pd
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt


def csv_to_dataframe(file_path):
    df = pd.read_csv(file_path)
    return df

def genarate_creation_resolution_figure(dataframe):
    dataframe['created'] = pd.to_datetime(dataframe['created'])
    dataframe['resolutiondate'] = pd.to_datetime(dataframe['resolutiondate'])

    # Trier les données par date de création
    dataframe.sort_values(by='created', inplace=True)

    df_filtered = dataframe.dropna(subset=['resolutiondate'])

    print(df_filtered)


    # Définition de  'issue_key' commeindex du DataFrame
    #df_filtered.set_index('issue_key', inplace=True)

    plt.figure(figsize=(12, 6))
    plt.plot(df_filtered.index, df_filtered['created'], label='Date de création', color='blue')
    plt.plot(df_filtered.index, df_filtered['resolutiondate'], label='Date de résolution', color='green')
    plt.xlabel('ticket')
    plt.ylabel('dates creation_resolution')
    plt.title('Tendances creation_resolution des tickets ')
    plt.xticks(rotation=45)  
    plt.legend()
    plt.tight_layout()  
    plt.savefig('creation_resolution.png')
    plt.show()


def get_creation_resolution_time_statistics(dataframe):
    dataframe['created'] = pd.to_datetime(dataframe['created'])
    dataframe['resolutiondate'] = pd.to_datetime(dataframe['resolutiondate'])
    dataframe = dataframe.dropna(subset=['resolutiondate','created'])
    dataframe['creation_resolution_time'] = dataframe.apply(lambda row: row['resolutiondate'] - row['created'], axis=1)

    average_resolution_time = dataframe['creation_resolution_time'].mean()
    min_resolition_time = dataframe['creation_resolution_time'].min()
    max_resolution_time = dataframe['creation_resolution_time'].max()
    print("Différence de temps moyenne entre création et résolution : ", average_resolution_time)
    print("difference max de temps de resolution",dataframe['creation_resolution_time'].max(),dataframe['creation_resolution_time'].min())
    print(dataframe['creation_resolution_time'].describe())
    return dataframe['creation_resolution_time'].describe()
 
def get_month_statistics(dataframe ):
    dataframe['created'] = pd.to_datetime(dataframe['created'])#
    dataframe['resolutiondate'] = pd.to_datetime(dataframe['resolutiondate'])#
    dataframe['created_month'] = dataframe['created'].dt.month
    dataframe['resolution_time'] = dataframe['resolutiondate'] - dataframe['created'] #
    dataframe = dataframe.dropna(subset=['resolutiondate','created'])#
    dataframe = dataframe[['created_month','resolution_time']]
    # statistiques groupées par mois
    statistics_by_month = dataframe.groupby('created_month')['resolution_time'].describe()
    print(statistics_by_month)


    #statistics_by_resolution_month = dataframe.groupby('created_month')['resolution_time'].agg(['mean', 'median', 'std', 'min', 'max'])
    #print(statistics_by_resolution_month)
    return statistics_by_month

def get_period_statistics(dataframe, period):
    dataframe['created'] = pd.to_datetime(dataframe['created'])
    dataframe['resolutiondate'] = pd.to_datetime(dataframe['resolutiondate'])
    
    if period == 'week':
        dataframe['period'] = dataframe['created'].dt.isocalendar().week
    elif period == 'month':
        dataframe['period'] = dataframe['created'].dt.month
    elif period == 'year':
        dataframe['period'] = dataframe['created'].dt.year
    else:
        raise ValueError("Période non valide. Veuillez spécifier 'day', 'month' ou 'year'.")
    
    dataframe['resolution_time'] = dataframe['resolutiondate'] - dataframe['created']
    
    dataframe = dataframe.dropna(subset=['resolutiondate', 'created'])
    
    dataframe = dataframe[['period', 'resolution_time']]
    
    statistics_by_period = dataframe.groupby('period')['resolution_time'].describe()
    
    return statistics_by_period

file_path = 'issue.csv'  
dataframe = csv_to_dataframe(file_path)
# df_created_solved = dataframe[['issue_key','created','resolutiondate']]
# #print(df_created_solved)
# #print(type(get_creation_resolution_time_statistics(dataframe)))
# print(get_month_statistics(dataframe))

print(get_month_statistics(dataframe))

