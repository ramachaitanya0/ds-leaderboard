import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

pd.set_option('max_columns', None)
pd.set_option('max_rows', None)


def prepare_lb_data():
    awards_df = pd.read_csv('data/awards.csv')
    rewards_df = pd.read_csv('data/rewards.csv')
    weekly_demos_df = pd.read_csv('data/weekly_demos.csv')

    user_agg_df = weekly_demos_df.merge(rewards_df)
    user_agg_df = user_agg_df.merge(awards_df, how='left')

    user_agg_df.loc[:, "# Entires"] = user_agg_df.groupby('Name')['Presented On'].transform('count')
    user_agg_df.loc[:, "Total Reward Points"] = user_agg_df.groupby('Name')['Reward Points'].transform('sum')
    user_agg_df.loc[:, "Total Awards Won"] = user_agg_df.groupby('Name')['Awarded On'].transform('nunique')
    user_agg_df.loc[:, "Last Presented On"] = user_agg_df.groupby('Name')['Presented On'].transform('max')
    user_agg_df.loc[:, "Last Awarded On"] = user_agg_df.groupby('Name')['Awarded On'].transform('max')

    user_cat_df = user_agg_df.groupby('Name')['Category'].unique().reset_index(name='Work Category')
    user_cat_df.loc[:, "Work Category"] = user_cat_df["Work Category"].apply(lambda x: ", ".join(x))

    user_type_df = user_agg_df.groupby('Name')['Type'].unique().reset_index(name='Work Type')
    user_type_df.loc[:, "Work Type"] = user_type_df["Work Type"].apply(lambda x: ", ".join(x))

    lb_df = user_agg_df.drop(['Category', 'Type'], axis=1)
    lb_df = lb_df.merge(user_cat_df, on="Name", how='left')
    lb_df = lb_df.merge(user_type_df, on="Name", how='left')

    lb_df = lb_df[
        ['Name', 'Work Category', 'Work Type', '# Entires', 'Total Reward Points', 'Total Awards Won',
         'Last Presented On', 'Last Awarded On']]
    lb_df = lb_df.drop_duplicates()
    lb_df.sort_values(["Total Reward Points", "# Entires", "Last Presented On"], ascending=False, inplace=True)
    lb_df.insert(0, "Rank", [i + 1 for i in range(len(lb_df))])
    return lb_df


# Setting page config for App
st.set_page_config(  # Alternate names: setup_page, page, layout
    layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
    page_title='Data Science Leaderboard',  # String or None. Strings get appended with "• Streamlit".
    page_icon=None,  # String, anything supported by st.image, or None.
)

# hide_streamlit_style = """
# <style>
# #MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# </style>"""
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.title("Data Science Leaderboard")
st.write("\n")
st.write("\n")

grid_height = 350
rowMultiSelectWithClick = True
suppressRowDeselection = False
enable_selection = True
selection_mode = "multiple"
use_checkbox = False
enable_pagination = True
paginationPageSize = 5

# load leaderboard data
df = prepare_lb_data()

# Infer basic colDefs from dataframe types
gb = GridOptionsBuilder.from_dataframe(df)
# customize gridOptions
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False)
# configures last row to use custom styles based on cell's value, injecting JsCode on components front end
cellsytle_jscode = JsCode("""
function(params) {
    if (params.value == 'A') {
        return {
            'color': 'white',
            'backgroundColor': 'darkred'
        }
    } else {
        return {
            'color': 'black',
            'backgroundColor': 'white'
        }
    }
};
""")
# gb.configure_column("group", cellStyle=cellsytle_jscode)
if enable_selection:
    gb.configure_selection(selection_mode)
    if (selection_mode == 'multiple'):
        gb.configure_selection(selection_mode, use_checkbox=False,
                               rowMultiSelectWithClick=rowMultiSelectWithClick,
                               suppressRowDeselection=suppressRowDeselection)
if enable_pagination:
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=paginationPageSize)
gb.configure_grid_options(domLayout='normal')
gridOptions = gb.build()
grid_response = AgGrid(
    df,
    gridOptions=gridOptions,
    height=grid_height,
    width="100%",
    data_return_mode="AS_INPUT",
    update_mode="MODEL_CHANGED",
    allow_unsafe_jscode=True,  # Set it to True to allow jsfunction to be injected
    theme='material'
)
weekly_demos_df = pd.read_csv('data/weekly_demos.csv')

df = grid_response['data']
selected = grid_response['selected_rows']
selected_df = pd.DataFrame(selected)
if len(selected_df) > 0:
    st.subheader('Contribution History')
    filtered_weekly_demos_df = weekly_demos_df[
        weekly_demos_df["Name"].isin(selected_df['Name'].values.tolist())].reset_index(drop=True)
    st.table(filtered_weekly_demos_df)
