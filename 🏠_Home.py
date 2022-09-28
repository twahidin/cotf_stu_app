import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from math import pi
import pygsheets
from google.oauth2 import service_account
import json
from fpdf import FPDF
import base64


st.set_page_config(
	page_title="Home",
	page_icon="🏠",
)

REG = 1
NAME = 2
GENDER = 3
OEJTS = 5
SELF_TEST = 12
PEER_TEST = 13
INTEREST_TEST = 14
GROUP_TEST = 15
LINKS_NO = 17
PERSONALITY_ALPHA = 'F' 
INTEREST_ALPHA = 'O'
INTERESTS_LIST_ALPHA = 'E'
INTERESTS = 'Interests'
LINKS = 'Links'
CONFIRMED = 'Y'
CL_CODE = 'Class Code'
STU_CODE = 'CODE'
MASTER = 'Master'
SHEET_ID = 'Sheet ID'
INT_PRO_SHEET = 'Interests Profiler'
INT_PRO = 'Interests Profiling'
OEJTS_Q = 'OEJTS Questions'

# env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
# template = env.get_template("pdf.html")

#connecting to Google Sheet
scope = ['https://www.googleapis.com/auth/spreadsheets',
		 'https://www.googleapis.com/auth/drive']

interest_page_url = "http://localhost:8501/Interests_Profiler"	
competencies_page_url = "http://localhost:8501/Self_and_Peer_Feedback"






@st.experimental_memo
def connect_sheets():
	key_dict = json.loads(st.secrets["textkey"])
	credentials = service_account.Credentials.from_service_account_info(key_dict, scopes = scope)
	gc = pygsheets.authorize(custom_credentials=credentials)
	return gc

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Adds a UI on top of a dataframe to let viewers filter columns

	Args:
		df (pd.DataFrame): Original dataframe

	Returns:
		pd.DataFrame: Filtered dataframe
	"""
	modify = st.checkbox("Add filters")

	if not modify:
		return df

	df = df.copy()

	# Try to convert datetimes into a standard format (datetime, no timezone)
	for col in df.columns:
		if is_object_dtype(df[col]):
			try:
				df[col] = pd.to_datetime(df[col])
			except Exception:
				pass

		if is_datetime64_any_dtype(df[col]):
			df[col] = df[col].dt.tz_localize(None)

	modification_container = st.container()

	with modification_container:
		to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
		for column in to_filter_columns:
			left, right = st.columns((1, 20))
			# Treat columns with < 10 unique values as categorical
			if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
				user_cat_input = right.multiselect(
					f"Values for {column}",
					df[column].unique(),
					default=list(df[column].unique()),
				)
				df = df[df[column].isin(user_cat_input)]
			elif is_numeric_dtype(df[column]):
				_min = float(df[column].min())
				_max = float(df[column].max())
				step = (_max - _min) / 100
				user_num_input = right.slider(
					f"Values for {column}",
					min_value=_min,
					max_value=_max,
					value=(_min, _max),
					step=step,
				)
				df = df[df[column].between(*user_num_input)]
			elif is_datetime64_any_dtype(df[column]):
				user_date_input = right.date_input(
					f"Values for {column}",
					value=(
						df[column].min(),
						df[column].max(),
					),
				)
				if len(user_date_input) == 2:
					user_date_input = tuple(map(pd.to_datetime, user_date_input))
					start_date, end_date = user_date_input
					df = df.loc[df[column].between(start_date, end_date)]
			else:
				user_text_input = right.text_input(
					f"Substring or regex in {column}",
				)
				if user_text_input:
					df = df[df[column].astype(str).str.contains(user_text_input)]

	return df

	
@st.experimental_memo
def extract_df(url,sh_name, _gc_local): #Successful testing
	sh_sch = _gc_local.open_by_url(url)
	#wk1 = sh_sch[sh_name] #open first worksheet
	wk1 = sh_sch.worksheet_by_title(sh_name)
	df_sh = wk1.get_as_df()
	return df_sh, wk1
#question function

def pdf_generator(name, act_list, links_list):
	with st.form("pdf generator"):
		name = st.text_input("Name: ", value=name)
		if name == "":
			st.warning('The PDF file does not contain a name', icon="⚠️")
		submit = st.form_submit_button("Generate PDF")

	if submit:
		pdf = FPDF()
		pdf.add_page()
		pdf.set_font('Arial','B', 14)
		pdf.cell(40, 10, "Interests Profiler Results", ln = 1)
		pdf.set_font('Arial','', 12)
		pdf.cell(40, 10, "Name: " + name, ln = 2)
		#pdf.set_text_color(255,0,0)
		pdf.set_font('Arial', 'U', 12)
		pdf.cell(40, 10, "Based one the Interest Profiler, you can consider the following hobbies:", ln = 3)
		pdf.set_text_color(0,0,0)
		pdf.set_font('Arial', '', 12)
		pdf.cell(40, 10, act_list, ln = 4)
		pdf.set_font('Arial', 'U', 12)
		pdf.cell(40, 10, "The following are some links you can click on in Tract.app:", ln = 5)
		pdf.set_text_color(0,0,255)
		pdf.set_font('Arial', 'U', 12)

		for i in range(len(links_list[0])):
			pdf.cell(40,10,txt = links_list[0][i], ln = 6 + i, link = links_list[1][i] )

		# i = 0
		# while i < len(links_list):
		#     pdf.cell(40,10,txt = links_list[i], ln = 5 + i, link = list_url[i + 1])
		#     i += 1 
		#st.write("Test")

		html = create_download_link(pdf.output(dest="S").encode("latin-1"), "Interests Profiler Results")
		st.markdown(html, unsafe_allow_html=True)

	# if submit:
	#     html = template.render(
	#         name=name,
	#         interests=act_list,
	#         links=links_list,
	#     )

	#     pdf = pdfkit.from_string(html, False)
	#     st.balloons()

	#     st.success("Your PDF file is ready for downloading")
	#     # st.write(html, unsafe_allow_html=True)
	#     # st.write("")
	#     st.download_button(
	#         "⬇️ Download PDF",
	#         data=pdf,
	#         file_name="interests_list.pdf",
	#         mime="application/octet-stream",
	#     )


def create_download_link(val, filename):
				b64 = base64.b64encode(val)  # val looks like b'...'
				return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

def retrieve_student_data(stu_list):
	p_list = []
	for i in range(len(stu_list[0])):
		#st.write(stu_list[0][i])
		p_list.append(stu_list[0][i])

	return(p_list)

def retrieve_interests_profile( col_list, col_name, df):
	links_list = []
	act_list = []
	ls = []
	#st.write(col_name)
	for i in col_list:
		if i == col_name:
			ls = df[col_name].values.tolist()

	if ls == []:
		return False


	for j in range(len(ls)):
		if ls[j] == 'Y':
			links_list.append(df[INTERESTS][j])
			act_list.append(df[LINKS][j])	

	#st.write(links_list)
	#st.write(act_list)

	return links_list, act_list, 	

def update_cell(row, col, wk_sh, val):
	update_value = col + str(row.index[0] + 2)
	# wk_sh = extract_df(class_url,0,gc)[1]
	#st.write(wk_sh)
	wk_sh.cell(update_value).set_text_format("bold", True).value = val


def update_hobbies(row, col, wk_sh, val):
	update_value = col + str(row.index[0] + 2)
	#st.write(wk_sh)
	# wk_sh = extract_df(class_url,0,gc)[1]
	#wk_sh.cell(update_value).set_text_format("bold", True).value = val
	wk_sh.update_values(update_value, [val])


def update_mass_hobbies(row, col, wk_sh, val):
	update_value = col + str(row + 2)
	#st.write(wk_sh)
	# wk_sh = extract_df(class_url,0,gc)[1]
	#wk_sh.cell(update_value).set_text_format("bold", True).value = val
	wk_sh.update_values(update_value, [val])


# <p>Based one the Interest Profiler, you can consider the following hobbies:<a href="https://www.w3schools.com/">Visit W3Schools.com!</a></p>

def print_interests_list(inputlist): #test
	#st.write(inputlist)
	lst = ""
	#st.write(inputlist)
	act_str = inputlist[0][0]

	st.write("Based on the Interest Profiler, you can consider the following hobbies:")
	for i in range(len(inputlist[0])):
		if i != 0:
			act_str += ', ' + inputlist[0][i]
	st.write(act_str)
	st.markdown('#')
	st.write("The following are some links you can click on in Tract.app")
	st.write("Please login to Tract.app before clicking the links")
	for (j,k) in zip(inputlist[0], inputlist[1]):
		st.write("Please click on this activity: [",j,"](%s)" % k)
		#lst += "<p>Please click on this activity : <a href=" +k+">"+j+"</a></p>" 

	return act_str


def main():
	st.title("COTF - Students Application")
	#personality_code = ['A','B','C','D']
	placeholder1 = st.empty()
	
	#placeholder4 = st.empty()
	login_flag = False
	guest_flag = False
	student_info = []
	#cache
	gc = connect_sheets()
	sheet_url = st.secrets["private_gsheets_url"]
	interests_url = st.secrets["interests_profile_url"]
	df_sh_sch = extract_df(sheet_url,SHEET_ID,gc)[0]

	if 'pc_key' not in st.session_state:
		st.session_state.pc_key = 'None'
	if 'c_code_key' not in st.session_state:
		st.session_state.c_code_key = 'None'
	if 's_code_key' not in st.session_state:
		st.session_state.s_code_key = 'None'
	if 's_val_key' not in st.session_state:
		st.session_state.s_val_key = 'None'
	if 's_row_key' not in st.session_state:
		st.session_state.s_row_key = 'None'
	if 'df_key' not in st.session_state:
		st.session_state.df_key = 'None'
	if 'g_key' not in st.session_state:
		st.session_state.g_key = 'None'
	if 'i_key' not in st.session_state:
		st.session_state.i_key = 'None'
	


	#st_row value must be updated here 


	logout = st.sidebar.button("Logout")
	if logout:
		for key in st.session_state.keys():
			del st.session_state[key]
		st.experimental_rerun()	




	if st.session_state.s_code_key != 'None' and st.session_state.c_code_key != 'None':
		#previously used by a valid user
		class_code = st.session_state.c_code_key
		stu_code = st.session_state.s_code_key
		student_values = st.session_state.s_val_key
		val_df = st.session_state.df_key
		st_row = st.session_state.s_row_key
		int_df = st.session_state.i_key

		login_flag = True

		# name_stu = df_sh_cl.loc[df_sh_cl['CODE'] == stu_code].values[0][2]
		# MBTI_test = df_sh_cl.loc[df_sh_cl['CODE'] == stu_code].values[0][14]

		#st.write("The student ID and class code has been input  ", return_student_row(df_sh_sch, class_code, stu_code))
		#placeholder1.empty()

	elif st.session_state.g_key == 'None':
		with placeholder1.form(key='authenticate'):
			st.write("Please enter 'Guest' in the Student code if you do not have any class or student codes")
			stu_code = st.text_input('Student code:')
			class_code = st.text_input('Class code: ')
			submit_button = st.form_submit_button(label='Login')
			if submit_button:
				if stu_code == 'Guest' or stu_code == 'guest':
					placeholder1.empty()
					guest_flag = True
					st.session_state.g_key = True

				elif class_code not in df_sh_sch[CL_CODE].values:
					st.warning("Please enter a valid class code (Note: Class Code is case sensitive)", icon='⚠️')
				else:
					cl_row = df_sh_sch.loc[df_sh_sch[CL_CODE] == class_code]
					#st.write(cl_row)
					class_url = cl_row['Sheet ID'][0]
					#st.write(class_url)
					val_df = extract_df(class_url,MASTER,gc)
					int_df = extract_df(class_url,INT_PRO_SHEET,gc)
					st.session_state.df_key = val_df
					st.session_state.i_key = int_df

					df_sh_cl = val_df[0]
					if stu_code not in df_sh_cl[STU_CODE].values:
						st.warning("Please enter a valid student code (Note: Student Code is case sensitive)", icon='⚠️')
					else:
						placeholder1.empty()
										#redo this part again and keep all in the list and retrieve the necessary 
						st.session_state.c_code_key = class_code
						st.session_state.s_code_key = stu_code
						st_row = df_sh_cl.loc[df_sh_cl['CODE'] == stu_code]
						st.session_state.s_row_key = st_row 
						student_values = df_sh_cl.loc[df_sh_cl['CODE'] == stu_code].values
						st.session_state.s_val_key = student_values
						#st.write("Hello")
						login_flag = True


	#retrieve student information
	if login_flag == True:
		#retrieve data
		student_info = retrieve_student_data(student_values)
		#st.write(student_info)			
	
	if st.session_state.g_key == True or login_flag == True:	
		st.write("###")
		st.write("🗂️ Please click on the tabs below to access your information")
		#interests_profiler_tab, group_acts_tab, competencies_strategies_tab = st.tabs(["🤾 Interests & Profile", "👥 Groups & Activities", "📊 Competencies & Strategies"])
		interests_profiler_tab = st.tabs(["🤾 Interests & Profile"])
	# SELF_TEST = 12
	# PEER_TEST = 13
	# INTEREST_TEST = 14


		with interests_profiler_tab:
			placeholder2 = st.empty()
			placeholder3 = st.empty()
			placeholder4 = st.empty()
			if login_flag == True: #the profiling is complete
				st.subheader("Student Information")
				st.write("Name: ", student_info[NAME])
				name = student_info[NAME]
				st.write("Register Number: ", student_info[REG])
				#st.write("Gender: ", student_info[GENDER])
				st.write("##")
				st.subheader("✋Tasks to be completed")
				if student_info[INTEREST_TEST] == 'N' and st.session_state.pc_key == 'None':
					st.write("🤾 Interests Profiler")
				# if student_info[PEER_TEST] == 'N' or student_info[SELF_TEST] == 'N':
				# 	st.write("🗣️ Self and Peer Feedback")
				# if student_info[GROUP_TEST] == 'N':
				# 	st.write("👥 Group Requests Page")

				st.write("##")
				with st.expander("Interest Profiler Results"):
					if st.session_state.pc_key != 'None':
						pc = st.session_state.pc_key
						df_interests = extract_df(interests_url,INT_PRO,gc)[0]
						col_list = df_interests.columns.values.tolist()
						int_list = retrieve_interests_profile( col_list, pc, df_interests)
						if int_list != False:
							i_list = print_interests_list(int_list)
							pdf_generator(name, i_list, int_list)
							update_cell(st_row, PERSONALITY_ALPHA , val_df[1], pc)
							update_cell(st_row, INTEREST_ALPHA , val_df[1], CONFIRMED)
							#int_df = extract_df(class_url,INT_PRO_SHEET,gc)
							#st.write(int_df[1])
							#st.write(int_list[0])
							update_hobbies(st_row, INTERESTS_LIST_ALPHA, int_df[1], int_list[0])
							#Mass update codes
							# for i in range(len(int_df[0])):
							# 	st.write(int_df[0]['OEJTS'][i])
							# 	#st.write(df_interests)
							# 	#st.write(col_list)
							# 	u_list = retrieve_interests_profile( col_list, str(int_df[0]['OEJTS'][i]), df_interests)
							# 	#st.write(u_list)
							# 	st.write(u_list)
							# 	update_mass_hobbies(i, INTERESTS_LIST_ALPHA, int_df[1], u_list[0])

						else:
							st.write("Personality Code not found: ", pc)
						 #updating the personality code 
					elif student_info[INTEREST_TEST] == CONFIRMED: #the profiling is complete
						pc = student_info[OEJTS]
						df_interests = extract_df(interests_url,INT_PRO,gc)[0]
						col_list = df_interests.columns.values.tolist()
						int_list = retrieve_interests_profile( col_list, pc, df_interests)
						if int_list != False:
							i_list = print_interests_list(int_list)
							pdf_generator(name, i_list, int_list)
						else:
							st.write("Personality Code not found: ", pc)
					else:
						st.write("Please complete the Interest Profiler (side bar) to generate the list of interests")
			elif st.session_state.g_key == True:
				#if st.session_state.pc_key == 'None': 
					#placeholder2.write("You may use the Interest Profiler (side bar) to assess yourself")
					#placeholder3.write("Please click on the 🏠 Home page after you have submitted your answers to access your results")
		
				with st.expander("Interest Profiler Results"):
					if st.session_state.pc_key != 'None': #the profiling is complete
						#st.write("Interest Profiler results")
						df_interests = extract_df(interests_url,INT_PRO,gc)[0]
						col_list = df_interests.columns.values.tolist()
						pc = st.session_state.pc_key
						int_list = retrieve_interests_profile( col_list, pc, df_interests)
						if int_list != False:
							i_list = print_interests_list(int_list)
							pdf_generator("", i_list, int_list)
						else:
							st.write("Personality Code not found: ", pc)
					else:
						st.write("Please complete the Interest Profiler (side bar) to generate the list of interests")

			
	#show complete
	
	# if MBTI_test == "N":
	# 	#Start MBTI Profile
	# 	#upgrade this to form
	# 	placeholder2.subheader("Tasks to be completed - MBTI Profiling" )
	# 	placeholder3.write("Please click on the Personality and Interest Profiler](%s) to start the assessment" % interest_page_url)
					
					#

if __name__ == "__main__":
	main()

# MBTI_EI = questions_print(questions_EI, 1, 'E', 'I', placeholder3, placeholder4)
					# MBTI_SN = questions_print(questions_SN, 3, 'S', 'N', placeholder3, placeholder4)
					# MBTI_TF = questions_print(questions_TF, 7, 'T', 'F', placeholder3, placeholder4)	
					# MBTI_JP = questions_print(questions_JP, 11, 'J', 'P', placeholder3, placeholder4)
					# #st.write(value.index)
					# update_value = 'F' + str(st_row.index[0] + 2)
					# update_test_flag = 'O' + str(st_row.index[0] + 2)
					# if MBTI_EI[1] == True and MBTI_SN[1] == True and MBTI_TF[1] == True and MBTI_JP[1] == True:
					# 	personality_code[0] = MBTI_EI[0]
					# 	personality_code[1] = MBTI_SN[0]
					# 	personality_code[2] = MBTI_TF[0]
					# 	personality_code[3] = MBTI_JP[0]
						# st.write(update_value)
						# MBTI_Profile = ''.join(personality_code)
						# st.write(MBTI_Profile)
						# wk_sh = extract_df(class_url,0,gc)[1]
						# wk_sh.cell(update_value).set_text_format("bold", True).value = MBTI_Profile
						# wk_sh.cell(update_test_flag).set_text_format("bold", True).value = "Y"
						# st.write("Updated")
				# elif friend_test == "N":
				# 	st.write("Friend test")
				# 	with st.form("Friends Grouping"):
				# 		st.write("Sociogram Survey")
				# 		slider_val = st.slider("Form slider")
				# 		checkbox_val = st.checkbox("Form checkbox")

				# 	    # Every form must have a submit button.
				# 		submitted = st.form_submit_button("Submit")
				# 		if submitted:
				# 			st.write("slider", slider_val, "checkbox", checkbox_val)
				#check if there is outstanding task
				#update the sociogram
				#perform the peer evaluation
				#perform the self evalutat
				#st.subheader("Groupwork Competency Chart")

# def questions_print(question_list, key_counter, p1, p2, pb1, pb2):
# 	counter_a = 0 
# 	counter_b = 0
# 	ans_counter = 0
# 	complete = False
# 	for question in question_list:
# 		pb1 = st.empty()
# 		pb2 = st.empty()
# 		pb1.text(question[0] + "\n" + "(A) " + question[1] + "\n" + "(B) " + question[2])
# 		answer = pb2.selectbox('Choose one', ['Select','A', 'B'], key = key_counter)
# 		if answer == "A":
# 			counter_a+= 1
# 			ans_counter += 1
# 		elif answer == "B":
# 			counter_b+= 1
# 			ans_counter += 1    
# 		key_counter += 1    
# 		if answer != 'Select':
# 			pb1.empty()
# 			pb2.empty()
# 		#end of for loops
# 	if counter_a > counter_b:
# 		#st.text('Your first personality code is: E')
# 		p_code = p1
# 	else:
# 		#st.text('Your first personality code is: I')
# 		p_code = p2
# 	if len(question_list) == ans_counter:
# 		complete = True

# 	return p_code ,complete
