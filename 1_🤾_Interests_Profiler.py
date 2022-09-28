import streamlit as st
import time
import numpy as np
from OEJTS import OEJTS_list, reveal_questions, personality_generator 
from google.oauth2 import service_account
import json


OEJTS_Q = "OEJTS Questions"

@st.experimental_memo
def extract_df(url,sh_name, _gc_local): #Successful testing
	sh_sch = _gc_local.open_by_url(url)
	#wk1 = sh_sch[sh_name] #open first worksheet
	wk1 = sh_sch.worksheet_by_title(sh_name)
	df_sh = wk1.get_as_df()
	return df_sh, wk1

@st.experimental_memo
def connect_sheets():
	key_dict = json.loads(st.secrets["textkey"])
	credentials = service_account.Credentials.from_service_account_info(key_dict, scopes = scope)
	gc = pygsheets.authorize(custom_credentials=credentials)
	return gc


st.set_page_config(page_title="Interest Profiler", page_icon="🤾")


gc = connect_sheets()
sheet_url = st.secrets["private_gsheets_url"]
interests_url = st.secrets["interests_profile_url"]


st.markdown("# Interests Profiler")
st.sidebar.header("Interests Profiler")
placeholder1 = st.empty()
placeholder1.write("This Interests Profiler test will take about 3-5 minutes to complete")

submit_flag = False
 
# def form_callback():
#     st.write(st.session_state.qn_1)
#     st.write(st.session_state.my_checkbox)

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty() 

if 'pc_key' not in st.session_state:
	st.session_state.pc_key = 'None'

df_oejts = extract_df(interests_url,OEJTS_Q,gc)[0]
#st.write(df_oejts.values.tolist())
q_list = df_oejts.values.tolist()
#st.write(q_list)



with st.form(key='interest_profiler'):
	#q1 = st.slider('Q1', 0, 5, 3, key='qn_1')
	#slider_input = st.slider('My slider', 0, 10, 5, key='my_slider')
	st.write("Please choose the statement that you agree with by moving the slider.")
	a_list = reveal_questions(q_list)
	ans_list = a_list[0]
	submit_button = st.form_submit_button(label='Submit')
	
	if submit_button and a_list[1] == False:
		pc = personality_generator(ans_list)

		# #last_rows = np.random.randn(1, 1)
		# #chart = st.line_chart(last_rows)

		for i in range(1, 101):
			#new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
			status_text.text("%i%% Processing" % i)
			#chart.add_rows(new_rows)
			progress_bar.progress(i)
			#last_rows = new_rows
			time.sleep(0.05)

		status_text.text("Profiling complete!")
		submit_flag = True   
		progress_bar.empty()
	elif submit_button and a_list[1] == True:
		st.warning('You have to make a choice for all statements to generate your report', icon="⚠️")


if submit_flag == True:
	st.write("##")
	st.session_state.pc_key = pc
	#expander = st.expander("Personality and Interest Profiler Report")
if st.session_state.pc_key != 'None':
	placeholder1.write("You have completed the Interests Profiler assessment ")
	st.write("Please click on the Home Page 🏠 to access the 🤾 Interests & Profile tab for the results, your results will be stored in your profile if you have a student code")
	

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
#st.button("Re-run")