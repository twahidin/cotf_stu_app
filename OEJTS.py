import streamlit as st

U = 'Choose statement'

OEJTS_list = [("q1","Makes lists", "Relies on memory"),("q2","Sceptical","Wants to believe"),("q3","Bored by time alone","Needs time alone"),
("q4","Accepts things as they are","unsatisfied with the ways things are"),("q5","Keeps a clean room","Just puts stuff where ever"),
 ("q6","Thinks robotic is an insult","Strives to have a mechanical mind"),("q7","Energetic","Mellow"),("q8","Prefer to take multiple choice test","Prefer essay answers"),
 ("q9","Chaotic","Organized"),("q10","Easily hurt","Thick-skinned"),("q11","Works best in groups","Works best alone"),
 ("q12","Focused on the present","Focused on the future"),("q13","Plans far ahead","Plans at the last minute"),("q14","Wants people's respect","Wants their love"),
 ("q15","Gets worn out by parties","Gets fired up by parties"),("q16","Fits in","Stands out"),("q17","Keeps options open","Commits"),
 ("q18","Wants to be good at fixing things","Wants to be good at fixing people"),("q19","Talks more","Listens more"),
 ("q20","Will tell what happened in an event","Will tell what the event meant"),
 ("q21","Gets work done right away","Procrastinates"),("q22","Follows the heart","Follows the head"),("q23","Stays at home","Goes out on the town"),
 ("q24","Wants the big picture","Wants the details"),("q25","Improvises","Prepares"),("q26","Bases morality on justice","Bases morality on compassion"),
 ("q27","Difficult to yell to others","Yelling to others comes naturally"),("q28","Theoretical","Observable"),("q29","Works hard","Plays hard"),
 ("q30","Uncomfortable with emotions","Values emotions"),("q31","Likes to perform in public","Avoids public speaking"),("q32","Likes to know who?, what?, when?","Likes to know Why?")]



def reveal_questions(question_list):
	ans_pair = []
	val = 0
	answer_list = []
	undecided = True
	for i in question_list:
		ans = st.select_slider( '', options=[i[1], U, i[2]], value=U, key=i[0])
		if ans == i[1]:
			val = 1
			undecided = False
		elif ans == U:
			val = 3
			undecided = True
		elif ans == i[2]:
			val = 5
			undecided = False
		
		answer_list.append(val)
		
	return answer_list, undecided


def personality_generator(ans_list):

	#Open Extended Jungian Type Scales 1.2


	A  = 30 - ans_list[2] - ans_list[6] - ans_list[10] +  ans_list[14] - ans_list[18] + ans_list[22] + ans_list[26] - ans_list[30]
	B  = 12 + ans_list[3] + ans_list[7] + ans_list[11] +  ans_list[15] + ans_list[19] - ans_list[23] - ans_list[27] + ans_list[31]
	C  = 30 - ans_list[1] + ans_list[5] + ans_list[9] -  ans_list[13] - ans_list[17] + ans_list[21] - ans_list[25] - ans_list[29]
	D  = 18 + ans_list[0] + ans_list[4] - ans_list[8] +  ans_list[12] - ans_list[16] + ans_list[20] - ans_list[24] + ans_list[28]

	if A > 24:
		A = 'E'
	else:
		A = 'I'

	if B > 24:
		B = 'N'
	else:
		B = 'S'

	if C > 24:
		C = 'T'
	else:
		C = 'F'

	if D > 24:
		D = 'P'
	else:
		D = 'J'

	personality_code = A + B + C + D    

	return personality_code

def interests_personality_generator(pc):

	



	return True
