import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from IPython.display import display

data_df = pd.read_csv('data/churn.csv')
df = data_df.copy()
df.info()

# 1
# There are more non-exited clients than exited ones

exited = df.groupby('Exited').count()
fig = go.Figure()
fig.add_trace(go.Pie(values=exited['RowNumber'], labels=['Non-exited', 'Exited']))
fig.update_layout(title='Exited to non-exited clients diagram')
fig.show()

# 2
# Half of people have from 100 to 139 thousand dollars on balance, about 90% have from 41 to 198 thousand dollars

rich_people = df[df['Balance'] > 2500]
fig = go.Figure()
fig.add_trace(go.Box(y=rich_people['Balance']))
fig.update_layout(title='Balance distribution for people with over 2500$ on balance',
                  yaxis_title='Money in USD')
fig.show()

# 3
# Both loyal and unloyal clients with over 2500$ have about the same balance distribution, with unloyal clients having
# smaller upper and lower fence
# Considering similar median (and the fact that most clients had over 0 balance before exiting bank) it's quite
# possible that this is an effect of some major policy that affects clients regardless of their balance, or that
# it affects people with certain amount of funds in a way that makes them suspectible to leaving
# (can't exclude the possibility of competitorship)

loyal = rich_people[rich_people['Exited'] == 0]
unloyal = rich_people[rich_people['Exited'] == 1]
fig = go.Figure()
fig.add_trace(go.Box(y=loyal['Balance'], name='Non-exited'))
fig.add_trace(go.Box(y=unloyal['Balance'], name='Exited'))
fig.update_layout(title='Balance distribution in slice of exited and non-exited clients',
                  yaxis_title='Money in USD')
fig.show()

# 4
# Exiting people with balance over 2500$ are older, median is higher by 9 years, upper fence by 14 years
# Quite possible that it's an issue with the bank that's could be attractive to younger clients, or
# make people dissatisfied with bank services after enough time, which convinces them to quit

fig = go.Figure()
fig.add_trace(go.Box(y=loyal['Age'], name='Non-exited'))
fig.add_trace(go.Box(y=unloyal['Age'], name='Exited'))
fig.update_layout(title='Age distribution in slice of exited and non-exited clients',
                  yaxis_title='Age in Earth years')
fig.show()

# 5
# Clients who exited show larger distribution of credit score
# Both loyal and unloyal clients have mostly around 600-700 credit score

mapbox_data = [loyal, unloyal]
group_labels = ['Non-exited', 'Exited']

fig = px.density_contour(rich_people, x='CreditScore', y='EstimatedSalary', facet_col='Exited')
fig.update_traces(contours_coloring="fill", contours_showlabels=True)
fig.show()

# 6
# Almost 20% of men exit, and almost 30% of women do
# Bank unattractive to female clients?

men = rich_people[rich_people['Gender'] == 'Male'].groupby('Exited').count()
women = rich_people[rich_people['Gender'] == 'Female'].groupby('Exited').count()

fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])
fig.add_trace(go.Pie(labels=group_labels, values=men['RowNumber'], name='Men'),
              row=1, col=1)
fig.add_trace(go.Pie(labels=group_labels, values=women['RowNumber'], name='Women'),
              row=1, col=2)
fig.update_traces(hole=.4, hoverinfo='label+percent+name')
fig.show()

# 7
# As evident from the plot, the smallest ratio of leaving clients is for those who bought 2 products
# It's nocticeably higher for clients who bought 1 product
# The majority of clients who bought 3 products left
# All clients who bought 4 products left
# This goes to show that the clients are likely to leave after the first buy, and a lot more likely
# to leave after 3 products, almost certain to leave after 4

fig = px.histogram(rich_people, x='NumOfProducts', color='Exited',
                   color_discrete_sequence=[px.colors.qualitative.Plotly[0], px.colors.qualitative.Plotly[1]],
                   text_auto=True)
fig.show()

# 8
# Inactive members leave more frequently
# Presumably the bank needs to be useful to inactive clients to reduce their exiting rate

fig = px.histogram(rich_people, x='IsActiveMember', color='Exited',
                   color_discrete_sequence=[px.colors.qualitative.Plotly[0], px.colors.qualitative.Plotly[1]],
                   text_auto=True)
fig.show()

# 9
# Bigger percentage of people exit in Germany than in France or Spain

df_countries = rich_people.groupby('Geography')['Exited'].agg(
    ['sum', 'count']
).reset_index()
df_countries['ratio'] = df_countries['sum'] / df_countries['count']
display(df_countries)
display(df_countries.value_counts())
fig = px.choropleth(df_countries, locations='Geography', locationmode='country names',
                    color='ratio',
                    color_continuous_scale=px.colors.sequential.Plasma)
fig.show()

# 10
# It would appear that the highest ratio of exiting people belongs to clients with very poor and excellent
# credit score; most notably, a noticeable majority either leaves immediately, or leaves sporadically after some time.
# (with very sharp increases during some periods)
# The latter inconsistency could be explained by changes in policy (or course change? some global phenomenon?)
# while former could be attributed to failure of bank meeting the expectations of these categories of people.
# For the clients with Poor to Fair ratings, the leaving picture seems uniform and spread out among the years
# It's evident, that no matter how long they spend being clients at bank, that doesn't improve their odds staying
# in the bank the following year, which suggests a persisting problem.
# Lastly, the peak amount of leaving clients was for those with 0 Tenure and Very Poor credit score (almost 47%).


def get_credit_score_cat(credit_score):
    if credit_score >= 300 and credit_score < 500:
        return "Very_Poor"
    elif credit_score >= 500 and credit_score < 601:
        return "Poor"
    elif credit_score >= 601 and credit_score < 661:
        return "Fair"
    elif credit_score >= 661 and credit_score < 781:
        return "Good"
    elif credit_score >= 781 and credit_score < 851:
        return "Excellent"
    elif credit_score >= 851:
        return "Top"
    elif credit_score < 300:
        return "Deep"


rich_people['CreditScoreCat'] = rich_people['CreditScore'].map(get_credit_score_cat)
display(rich_people['CreditScoreCat'].value_counts())

table = pd.pivot_table(rich_people, values='Exited', index='CreditScoreCat', columns='Tenure',
                       aggfunc=np.mean)

display(table)

fig = px.imshow(table, x=table.columns, y=table.index, color_continuous_scale='Reds')
fig.show()
