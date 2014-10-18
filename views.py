# Create your views here.

from django.shortcuts import render_to_response
from django.template import RequestContext
from DBManagement.models import *
from django.db.models import Count
from collections import Counter
from itertools import combinations, groupby
from django.db.models import Sum
import string
from operator import itemgetter
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

import urllib2
import urllib
import json
import re

#for clustering
import math
import random

#for paper details
import datetime

#set Additional Maths folder
add_math_img='/static/image/'

#Add Maths question page settings
addMaths_q_per_page=10

#Solution format
sol_format={'v':'Values','r':'Ratio','c':'Coordinates','m':'Matrix','i':'Inequality','e':'Equation','n':'Not_Equal','p':'Proving','d':'Diagram'}

def topics(request):
	param={}
	
	eduLevel=list(education_level.objects.only('id','title').values())
	tp=topic.objects.all()
	param['topic_count']=len(tp)
	
	param['subject']=subject.objects.all()
	for sb in param['subject']:
		#set education level
		for ed in eduLevel:
			if ed['id']==sb.edu_level:
				sb.educ=ed['title']
				break
		sb.topics=tp.filter(subject_id=sb.id)
		for t in sb.topics:
			t.subtopics=subtopic.objects.filter(topic_id=t.id)
			t.subtopics_count=len(t.subtopics)		
			
	return render_to_response('topic.html',param)

def questions(request, main_id='-1', sub_id='-1'):
	param={}
	
	#default input
	if(main_id=='-1' or sub_id=='-1'):
		param['questions']=question.objects.all()
	else:
		param['questions']=question.objects.filter(topic_id=main_id,subtopic_id=sub_id)
	#add sub questions
	for q in param['questions']:
		q.sub_questions=subquestion.objects.filter(qid=q.id)
		q.solutions=answer.objects.filter(question_id=q.id)
	
	param['question_count']=len(param['questions'])
	param['main_topic']=topic.objects.get(id=main_id)
	param['sub_topic']=subtopic.objects.get(id=sub_id)
	
	return render_to_response('display_question_list.html',param)
	
def count_wSubQues(quesList,subQues,ans):
	result={}
	result['sub_ques_count']=0	#questions with subquestions
	result['ans_count']=0		#questions with answers
	result['sol_count']=0		#questions with solutions
	result['total_sub']=0		#total number of subquestions
	result['total_sub_ans']=0	#total number of subquestions with answer
	#subQues=list(subquestion.objects.only('qid','std_answer').values())
	#ans=list(answer.objects.only('id','question_id').values())
	q_hasSub=False
	for q in quesList:
		if q['std_answer']!=None and q['std_answer']!='' :		#if question has answer
			result['ans_count']+=1
		for sol in ans:
			if sol['question_id_id']==q['id']:
				result['sol_count']+=1
				break;
		for s in subQues:
			if s['qid_id']==q['id']:	#if subquestion belongs to question
				q_hasSub=True
				result['total_sub']+=1
				if s['std_answer']!=None and s['std_answer']!='':	#if subquestion has answer
					result['total_sub_ans']+=1
		if q_hasSub==True:
			result['sub_ques_count']+=1
		q_hasSub=False
	return result

#@login_required(redirect_field_name='/admin/')	
def delete_record(request, type='Nil', id='-1', sub_id='-1'):
	if (type=='Nil') or (id=='-1'):
		return HttpResponseRedirect("/home/")
	
	if(type=='sub_topic'):
		s_topic=	subtopic.objects.get(id=id)
		img=		image.objects.filter(subtopic_id=id)
		res=		resource.objects.filter(subtopic_id=id)
		ques=		question.objects.filter(subtopic_id=id)
		for q in ques:
			s_ques=subquestion.objects.filter(qid=q.id)
			for sq in s_ques:
				sq_id=""
				if(sq.qid is not None):
					sq_id+=str(sq.qid)
				if(sq.question_no is not None):
					sq_id+=str(squestion_no)
				if(sq.question_part is not None):
					sq_id+=str(sq.question_part)
				ans=answer.objects.filter(question_id=sq_id)
				ans.delete()			
			ans=answer.objects.filter(question_id=q.id)
			ans.delete()
			s_ques.delete()
		ques.delete()
		res.delete()
		img.delete()
		s_topic.delete()
		return HttpResponseRedirect("/topics/")
		
	return HttpResponseRedirect("/home/")

"""	Temporary not using
def statistics(request):
	param={}
	
	total_questions=0
	questions=0
	sub_question=0
	sub_answer=0
	sub_solution=0
	
	#helper for query
	subj=list(subject.objects.values())
	eduLevel=list(education_level.objects.defer('description').values())
	s_topic=subtopic.objects.all()
	subQues=list(subquestion.objects.only('qid','std_answer').values())
	ans=list(answer.objects.only('id','question_id').values())
	qqq=question.objects.defer('q_category','question_no','marks','content','q_type','duration','ans_correct','ans_wrong','difficulty_level','num_views','source','input','std_answer_latex').all()
	
	#basic parmameters
	param['topics']=topic.objects.all()
	param['topic_count']=len(param['topics'])
	param['db_question_count']=qqq.count()
	
	for t in param['topics']:
	
		# subjects and educational levels are few, so direct check
		t.subj='Not Found'
		t.educ='Not Found'
		for sb in subj:
			if sb['id']==t.subject_id_id:
				t.subj=sb['title']
				for ed in eduLevel:
					if ed['id']==sb['edu_level']:
						t.educ=ed['title']
						break
		
		t.subtopics=s_topic.filter(topic_id=t.id)
		t.subtopics_count=0
		questions=0
		allQuest=qqq.filter(topic_id=t.id)
		t.dbCount_Quest=allQuest.count()
		for st in t.subtopics:
			t.subtopics_count+=1	#reduces query
			st_question=list(allQuest.filter(subtopic_id=st.id).values())
			st.question_count=len(st_question)
			
			result=count_wSubQues(st_question,subQues,ans)
			st.non_question=result['sub_ques_count']
			st.answer_count=result['ans_count']
			st.subquestion_count=result['total_sub']
			st.subanswer_count=result['total_sub_ans']
			st.solution_count=result['sol_count']
			questions+=st.question_count
			total_questions+=st.question_count
		t.total_questions=questions
	param['total_questions']=total_questions

	return render_to_response('statistic.html',param)
	
def select_paper_topics(request):
	param={}
	
	eduLevel=list(education_level.objects.only('id','title').values())
	tp=topic.objects.all()
	param['topic_count']=len(tp)
	
	param['subject']=subject.objects.all()
	for sb in param['subject']:
		#set education level
		for ed in eduLevel:
			if ed['id']==sb.edu_level:
				sb.educ=ed['title']				
				break
		sb.topics=tp.filter(subject_id=sb.id)
		for t in sb.topics:
			t.subtopics=subtopic.objects.filter(topic_id=t.id)
			t.subtopics_count=len(t.subtopics)		
			
	return render_to_response('select_paper_topic.html',param)
	
def select_questions(request, main_id='-1', sub_id='-1'):
	param={}
	
	#default input
	if(main_id=='-1'):
		param['questions']=question.objects.all()
	elif(sub_id=='-1'):
		param['questions']=question.objects.filter(topic_id=main_id)
		param['sub_topic']='All subtopics'
	else:
		param['questions']=question.objects.filter(topic_id=main_id,subtopic_id=sub_id)
		param['sub_topic']=subtopic.objects.get(id=sub_id).title
	#add sub questions
	for q in param['questions']:
		q.sub_questions=subquestion.objects.filter(qid=q.id)
		q.solutions=answer.objects.filter(question_id=q.id)
	
	param['question_count']=len(param['questions'])
	param['main_topic']=topic.objects.get(id=main_id)	
	
	return render_to_response('select_question.html',param,RequestContext(request))
	
def answer_question(request, question_ID):
	param={}
	
	q=question.objects.get(id=question_ID)
	param['question']=q.content
	param['question_id']=question_ID
	param['subTopic']=q.subtopic_id.title
	param['topic']=q.topic_id.title
	param['subj']=q.topic_id.subject_id.title
	return render_to_response('answer_question.html',param,RequestContext(request))

#a tester page for the solution checking
def test_solution_checker(request):
		return render_to_response('sol_check_test.html',{},RequestContext(request))
"""	

#Skeletal Modules

#menu page to select topic or paper
def AMaths_Menu(request,subj_id):
	param={}
	
	#query list of papers
	param['papers']=list(paper.objects.filter(subject_id=subj_id,number__gt=0).only('id','year','month','number').order_by('id').values())	
	
	# query list of topics
	topics=list(topic.objects.filter(subject_id=subj_id).order_by('id').values())
	param['topics']=topics
	#for links
	param['subject']=subject.objects.all()
	param['cur_subj']=subject.objects.get(id=subj_id)
	
	return render_to_response('add_math.html',param)

#method to process question into display format
def process_question(q):
	#query for all images for this question
	img_sel=list(image.objects.filter(qa_id=q['id'],qa='Question').only('id','imagepath').order_by('id').values())
	
	#split the content of question using ';' as separator
	token=q['content'].split(';')	
	display=[]
	item={}
	img_iterator=0
	#for each question part
	for t in token:
		#if is not image, add as text
		if t.strip()!="img":
			item['type']=1
			item['value']=t.strip()
		else:
			#if image, substitude the image path
			item['type']=2
			if len(img_sel)>img_iterator:
				#add path to where image folder is
				item['value']=add_math_img + img_sel[img_iterator]['imagepath']
			else:
				item['value']='missing image'
			img_iterator=img_iterator+1
		#The processed part is added into a list representing the content
		display.append(item)
		item={}
	
	#The 'type' helps identify images (1 for text, 2 for image)
	#In cases where image is not found, 'missing image' text is used
	return display
	
#display the list of question for Paper or Topic selected
def add_math_question(request,list_type,subj_id,page_no):
    
	param={}
	
	#get id of paper or topic
	list_id = request.GET.get("list_id")
	topic_id = 0 #default
	paperset_id = 0 #default
	if (request.GET.get("topic_id") != None):
		topic_id = int(request.GET.get("topic_id"))
	if (request.GET.get("paperset_id") != None):
		paperset_id = int(request.GET.get("paperset_id"))
	
	#from the type (paper or topic) passed, query for questions
	sel=[]
	page_title=[] #for storing paper title / topic title
	
	if list_type=='paper': #view by paper	
		sel=list(question.objects.select_related().filter(paper_id=list_id).only('id','content','question_no','marks').order_by('id').values())
		param['cur_subj']=paper.objects.get(id=list_id).subject_id_id
		page_title=subject.objects.get(id=subj_id).title + ' ' + paper.objects.get(id=list_id).year + ' ' +  paper.objects.get(id=list_id).month + ' Paper ' + str(paper.objects.get(id=list_id).number)
	elif list_type=='topic': #view by topic
		if (paperset_id > 0): #optional of having paperset filtered
			paper_ids = paper.objects.filter(paperset_id=paperset_id)
			sel = list(question.objects.filter(paper_id__in=paper_ids, topic_id=list_id).only('id','content','question_no','marks').order_by('id').values())
		else: #no paperset by default
			sel = list(question.objects.filter(topic_id=list_id).only('id','content','question_no','marks').order_by('id').values())
		param['cur_subj']=topic.objects.get(id=list_id).subject_id.id
		page_title=subject.objects.get(id=subj_id).title + ' - ' + str(topic.objects.get(id=list_id).title)
	elif list_type == 'tag': #view by tag
		#get questions
		qnlist=[]
		if (topic_id > 0): #topic filter
			qnlist = question.objects.filter(topic_id=topic_id)
		elif (paperset_id > 0): #paperset filter
			paper_ids = paper.objects.filter(paperset_id=paperset_id)
			qnlist = question.objects.filter(paper_id__in=paper_ids)
		else: #clean, no filtering
			qnlist = question.objects.all()
		#further filter questions with tags
		tags = list_id.split('|')
		tag_list=list(tag.objects.filter(tag__id__in=tags, question_id__in=qnlist).order_by('question_id').values('question_id').annotate(q_count=Count('question_id')).filter(q_count__gte=len(tags)))
		qid_set=[]
		for tagitem in tag_list:
			qid_set.append(tagitem['question_id'])
		#show questions
		sel = list(question.objects.filter(pk__in=qid_set).only('id','content','question_no','marks').order_by('id').values())
		param['cur_subj'] = 1
		title=''
		#pack a list for description of formula and concept being used
		formula=[]
		concept=[]
		for t in tags:
			tag_def=tag_definitions.objects.get(id=t)
			title+= tag_def.title + ', '
			if tag_def.type == 'F':
				formula.append(tag_def.content)
			elif tag_def.type == 'C':
				concept.append(tag_def.content)
		title=title[0:len(title)-2]
		param['formula']=formula
		param['concept']=concept
		page_title='Tags (' + title + ')'
	elif list_type == 'single': #view as single question
		sel=list(question.objects.filter(id=list_id).only('id','content','question_no','marks').order_by('id').values())
		param['cur_subj']=question.objects.get(id=list_id).topic_id.subject_id_id
		page_title = "Question ID: " + list_id
	
	#to display number of questions (and assist in other operations)
	no_of_qn=len(sel)
	
	#addMaths_q_per_page is the number of questions per page
	#from the list and page number, display current page's questions
	page_items=[]
	for i in range(0,addMaths_q_per_page):
		if( (i + addMaths_q_per_page * (int(page_no) - 1))<no_of_qn):
			page_items.append(sel[i + addMaths_q_per_page * (int(page_no)-1)])
	
	#create links of pages (determine number of pages)
	no_pages=no_of_qn/addMaths_q_per_page
	if((no_of_qn % addMaths_q_per_page)!=0):
		no_pages=no_pages+1
	page_links=[]
	for i in range(1,no_pages+1):
		page_links.append(i)
	
	#call helper method to process content of each question
	for q in page_items:
		#pack in related content
		q['taglist']=[]
		q['topic']=topic.objects.get(id=q['topic_id_id']).title
		q['subtopic']=subtopic.objects.get(id=q['subtopic_id_id']).title
		p=paper.objects.get(id=q['paper_id_id'])
		q['paper']=str(p.year) + ' ' + p.month + ' Paper ' + str(p.number)
		
		#the main question display
		q['display']=process_question(q) 
		
		if list_type == "tag":
			#list keywords involved. ONLY keywords
			keywordTags = ''
			tags = list_id.split('|')
			for t in tags:
				tagdef = tag_definitions.objects.get(id=t)
				if tagdef.type == "K":
					keywordTags += tagdef.content + '|'
			keywordTags = keywordTags[0:len(keywordTags)]
			#track down the keyword and BOLD it
			for qitem in q['display']:
				if qitem['type'] == 1:
					for keyword in keywordTags.split('|'):
						p = re.compile('^' + keyword + '$')
						newstring=''
						for word in qitem['value'].split():
							if word[-1:] == ',':
								word = word[0:len(word)-1]
								if p.match(word) != None:
									newstring += '<b>' + word + '</b>' + ', '
								else:
									newstring += word + ', '
							else:
								if p.match(word) != None:
									newstring += '<b>' + word + '</b>' + ' '
								else:
									newstring += word + ' '
						qitem['value']=newstring
		
		#pack the answer
		q['displayans']=''
		if len(answer.objects.filter(question_id=q['id'])) > 0:
			ans=list(answer.objects.filter(question_id=q['id']).values())[0]
			q['displayans']=process_solution(ans)
		taglist = tag.objects.filter(question_id=q['id']).order_by('tag__title')
		if len(taglist) != 0:
			for t in taglist:
				q['taglist'].append(t)
	
	param['questions']=page_items
	param['page_links']=page_links
	param['page_no']=int(page_no)
	param['num_q']=no_of_qn
	param['title']=page_title
	param['subj_id']=subj_id
	#parameters to open next page (call back to this function)
	param['list_id']=list_id
	param['paperset_id']=paperset_id
	param['topic_id']=topic_id
	param['list_type']=list_type
	#for links
	param['subject']=subject.objects.all()
			
	return render_to_response('add_math_question.html',param)

#page displays concept and formula tags based on topics	
def add_math_concept(request,subj_id):
	param={}
	#for topic dropdown
	param['topics'] = topic.objects.filter(subject_id_id=subj_id)
	param['cur_subj']=subject.objects.get(id=subj_id)
	
	tpc_id = 0 #default
	#retrieve topic_id if found
	if request.GET.get('topic_id') != None:
		tpc_id = request.GET.get('topic_id')
	param['topic_id'] = int(tpc_id)
	 
	if tpc_id != None: #if topic_id found, display the concepts and formulae only
		taglist = tag_definitions.objects.filter(topic_id=tpc_id, type__in='C,F').order_by('type')
		param['taglist'] = taglist
	
	
	return render_to_response('add_math_concept.html',param)
	
#Display question selected from question list
"""
def display_add_math_question(request,question_id):

	#get question and save into a list
	q=list(question.objects.filter(id=question_id).values())[0]
	q['display']=process_question(q)
	
	sol=[]
	count=1
	l=-1	#number of answer groups (in field types)
	if q['input']!=None:
		#split the input and type fields into answer groups
		prompt=q['input'].split(';')
		if(q['type']!=None):
			qType=q['type'].split(';')
			l=len(qType)
		else:
			qType=''
			l=0
		#create item for each question group and add to list
		for p in prompt:
			item={}
			item['input']=p
			item['p_name']='Part'+str(count)
			item['part']=count-1
			#if no type specified set as type value
			if(qType=='' or (count-1)>=l):
				item['type']=[]
				item['type'].append({'type':'v','count':0,'unit':''})				
			else:
				#call helper method to split the question group into questions
				item['type']=get_qType(qType[count-1])
			count=count+1
			sol.append(item)
	else:
		#default display if input is None
		sol.append({'input':'','p_name':'','part':0})

	param={'question':q,'sol':sol}
	#for links
	param['subject']=subject.objects.all()
	param['cur_subj']=question.objects.get(id=question_id).topic_id.subject_id.id
	
	#for csrf of dajax
	return render_to_response('display_add_math_question.html',param,RequestContext(request))
"""
#helper method to split question group
def get_qType(field_value):
	#questions in question group is separated by '|'
	parts=field_value.strip(' ').split('|')
	itemlist=[]
	val_count=0
	#set variables to display for each type of question
	for p in parts:
		i=p.split(',')
		item={}
		item['type']=i[0] #first character represents type
		item['count']=val_count
		if(i[0]=='v'):	#value
			item['unit']=i[1]			
		elif(i[0]=='c'):	#coordinates
			item['num']=range(0,int(i[1]))
			item['unit']=i[2]			
		elif(i[0]=='m'):	#matrix
			item['num']=range(0,int(i[1])*int(i[2]))
			item['col']=int(i[2])
		elif(i[0]=='e' or i[0]=='n'):	#equation or not
			item['val']=i[1]
			item['unit']=i[2]			
		elif(i[0]=='i'):	#inequality
			item['val']=i[1]
			item['unit']=i[2]
			item['lower']=i[3][0]
			item['upper']=i[3][1]
		#ratio has no extra settings
			
		itemlist.append(item)
		val_count=val_count+1		
	return itemlist

#display solution (Standard Answers with steps and diagrams)
def process_solution(q):
	#query images
	img_sel=list(image.objects.filter(qa_id=q['question_id_id'],qa='Solution').only('id','imagepath').order_by('id').values())
	img_iterator=0
	limit=len(img_sel)
	#split question's content using ';' as separator
	token=q['content'].split(';')	
	display=[]
	#for each part of content, determine if text or image
	for t in token:
		item={}
		if t.strip()!="img":
			item['type']=1
			item['value']=t.strip()
		else:
			item['type']=2
			if img_iterator<limit:
				item['value']=add_math_img + img_sel[img_iterator]['imagepath']
			else:
				item['value']='no_image'
			img_iterator=img_iterator+1
		display.append(item)
	return display
	
#____________________#
#start admin code for Additional Maths (For modifying questions)


#a menu to select by paper, topic or solution type

def AddMaths_Admin(request,subj_id):
	param={}
	
	param['papers']=list(paper.objects.filter(subject_id=subj_id,number__gt=0).only('id','year','month','number').order_by('id').values())	
	
	topics=list(topic.objects.filter(subject_id=subj_id).order_by('id').values())
	param['topics']=topics
	
	param['sol_type']=[]
	for k in sol_format.keys():
		param['sol_type'].append({'id':k,'name':sol_format[k]})
		
	param['subj_id']=subj_id
	
	#for links
	param['subject']=subject.objects.all()
	
	return render_to_response('add_math_admin.html',param)

#list questions to modify
def AddMaths_Admin_ModifyQuestion(request,list_type,subj_id,page_no):
    
	param={}
	
	#query paper and subtopics for display in each question
	paperlist=list(paper.objects.filter(subject_id=subj_id,number__gt=0).only('id','year','month','number').order_by('id').values())
	sel=list(topic.objects.filter(subject_id=subj_id).only('id').order_by('id').values())
	stopic=[]
	for sel_topic in sel:
		stopic[0:0]=list(subtopic.objects.filter(topic_id=sel_topic['id']).only('id','title').order_by('id').values())
	
	#get id of type/topic/sol_type
	list_id = request.GET.get("list_id")
	#query questions based on paper, topic,all or solution type
	sel=[]
	if list_type=='paper':
		sel=list(question.objects.filter(paper_id=list_id).only('id','paper_id_id','content','subtopic_id_id','type').order_by('id').values())
		page_title=subject.objects.get(id=paper.objects.get(id=list_id).subject_id_id).title + ' ' + paper.objects.get(id=list_id).year + ' ' +  paper.objects.get(id=list_id).month + ' Paper ' + str(paper.objects.get(id=list_id).number)
	elif list_type=='topic':		
		sel=list(question.objects.filter(topic_id=list_id).only('id','paper_id_id','content','subtopic_id_id','type').order_by('id').values())
		page_title=topic.objects.get(id=list_id).title
	elif list_type=='tag':
		tag_list=list(tag.objects.filter(tag=list_id).order_by('question_id').values('question_id'))
		qid_set=[]
		for tagitem in tag_list:
			qid_set.append(tagitem['question_id'])
		sel = list(question.objects.filter(pk__in=qid_set).only('id','paper_id_id','content','subtopic_id_id','type').order_by('id').values())
		page_title='Tags: ' + list_id
	else:		
		for sel_topic in stopic:
			sel[0:0]=list(question.objects.filter(subtopic_id=sel_topic['id']).only('id','paper_id_id','content','subtopic_id_id','type').order_by('id').values())
		#if is question type and not all	
		if list_type=='question_type':
			temp=[]			
			for q in sel:
				if ((';'+q['type']).find(';'+list_id)>= 0):
					temp.append(q)
				elif (('|'+q['type']).find('|'+list_id)>= 0):
					temp.append(q)
			sel=temp
			for k in sol_format.keys():
				if (k==list_id):
					page_title=subject.objects.get(id=sub_id).title + ' - ' + sol_format[k]	
		
	no_of_qn=len(sel)
	
	#select questions for page
	page_items=[]
	for i in range(0,addMaths_q_per_page):
		if( (i + addMaths_q_per_page * (int(page_no) - 1))<no_of_qn):
			page_items.append(sel[i + addMaths_q_per_page * (int(page_no) - 1)])
	
	#For each question in page, insert required values
	for i in range(0,len(page_items)):
		page_items[i]['display']=page_items[i]['content'][:100]+'\\]'
		page_items[i]['paper']='_'
		page_items[i]['subtopic']='_'
		page_items[i]['sol_type']=''
		for p in paperlist:
			if(p['id']==page_items[i]['paper_id_id']):
				page_items[i]['paper']=p['month']+' '+p['year']+' Paper'+str(p['number'])
				break
		for temp in stopic:
			if(temp['id']==page_items[i]['subtopic_id_id']):
				page_items[i]['subtopic']=temp['title']
				break		
		for k in sol_format.keys():
			if ((';'+page_items[i]['type']).find(';'+k)>= 0):
				page_items[i]['sol_type']=page_items[i]['sol_type']+sol_format[k]+', '
			elif (('|'+page_items[i]['type']).find('|'+k)>= 0):
				page_items[i]['sol_type']=page_items[i]['sol_type']+sol_format[k]+', '
				
	#create links of pages
	no_pages=no_of_qn/addMaths_q_per_page
	if((no_of_qn % addMaths_q_per_page)!=0):
		no_pages=no_pages+1
	page_links=[]
	for i in range(1,no_pages+1):
		page_links.append(i)
		
	param['questions']=page_items
	param['page_links']=page_links
	param['num_q']=no_of_qn
	param['list_id']=list_id
	param['list_type']=list_type
	param['page_no']=int(page_no)
	param['page_title']='Modifying ' + page_title
	
	param['subj_id']=subj_id
	    
	#for links
	param['subject']=subject.objects.all()
	
	return render_to_response('add_math_admin_qList.html',param)
	
#a form to add and modify questions
def AddMaths_Admin_QuestionForm(request,list_type,page_no,list_id,subj_id,question_id):
	param={}
	
	#if less than 0, insert new question
	param['question']=None
	if(int(question_id)>=0):
		param['question']=question.objects.get(id=question_id)
		param['topic']=param['question'].topic_id.title
		param['subtopic']=param['question'].subtopic_id.title
		param['paper']=paper.objects.get(id=param['question'].paper_id)
		
		param['display']='\n'+param['question'].content.replace(';','\n')
		if len(answer.objects.filter(question_id=question_id)) == 1:
			param['answer']='\n'+answer.objects.get(question_id=question_id).content.replace(';','\n')
		param['tags']=tag.objects.select_related().filter(question_id=question_id)
		param['tagdefs']=tag_definitions.objects.all()
		
		#split the solution into groups then into individual answers
		sol=param['question'].input.split(';')
		sol_type=param['question'].type.split(';')
		sol_val=param['question'].type_answer.split(';')
		param['sol']=[]
		
		for i in range(0,len(sol)):
			temp={}
			temp['prompt']=sol[i]
			s_type=sol_type[i].split('|')
			s_ans=sol_val[i].split('|')
			temp['type']=[]
			#for each question (not group)
			for st_val in s_type:
				if len(st_val) != 0:
					st_temp={}
					st_temp['type']=st_val
					#determine number of answer parts (user inputs)
					if st_val[0]=='i':
						st_temp['row_count']=2
					elif st_val[0]=='c':
						st_temp['row_count']=int(st_val.split(',')[1])
					elif st_val[0]=='m':
						st_temp['row_count']=int(st_val.split(',')[1])*int(st_val.split(',')[2])					
					else:
						st_temp['row_count']=1
					#assign the answer parts to question, then remove from list
					st_temp['ans']=s_ans[0:st_temp['row_count']]
					s_ans=s_ans[st_temp['row_count']:]
					temp['type'].append(st_temp)
					
			param['sol'].append(temp)
		
	param['list_type']=list_type
	param['page_no']=page_no
	param['list_id']=list_id
	
	#for new questions (additional info to select)
	param['year_list']=range(1995,datetime.datetime.now().year) #up till previous year
	topics=list(topic.objects.filter(subject_id=subj_id).order_by('id').values())
	topics.reverse()
	param['topics']=[]
	for t in topics:		
		param['topics'][0:0]=list(subtopic.objects.filter(topic_id=t['id']).values() )
		
	param['subj_id']=subj_id
	
	#for links
	param['subject']=subject.objects.all()
	
	#for csrf for preview page
	return render_to_response('add_math_admin_form.html',param,RequestContext(request))
	
#accept parameters from form to produce a preview page
def AddMaths_qPreview(request):
	
	#get values using Post
	q_id=request.POST.get('p_q_id','')
	q_content=request.POST.get('p_content','')
	q_input=request.POST.get('p_input','')
	q_type=request.POST.get('p_type','')
	q_ans=request.POST.get('p_ans','')
	
	q={'id':q_id,'content':q_content}
	q['display']=process_question(q)
	
	ans_list=q_ans.split(';')
	
	sol=[]
	count=1
	l=-1	#number of answers (in types)
	if q_input!=None:
		prompt=q_input.split(';')
		if(q_type!=None):
			qType=q_type.split(';')
			l=len(qType)
		else:
			qType=''
			l=0
		for p in prompt:
			item={}
			item['input']=p
			item['p_name']='Part'+str(count)
			item['part']=count-1
			#if no type specified
			if(qType=='' or (count-1)>=l):
				item['type']=[]
				item['type'].append({'type':'v','count':0,'unit':'','ans':ans_list[count-1]})
			else:
				item['type']=get_qType(qType[count-1])
				a_list=ans_list[count-1].replace('/','|').split('|')
				for p_item in item['type']:
					if(p_item['type']=='v' or p_item['type']=='e' or p_item['type']=='n'):
						p_item['ans']=a_list[0]
						a_list=a_list[1:]
					elif(p_item['type']=='i' or p_item['type']=='r'):
						p_item['ans']=a_list[0:2]
						a_list=a_list[2:]
					elif(p_item['type']=='c'):
						p_count=len(p_item['num'])
						p_item['num']=zip(p_item['num'],a_list[0:len(p_item['num'])])
						a_list=a_list[p_count:]
					elif(p_item['type']=='m'):
						p_count=len(p_item['num'])
						p_item['num']=zip(p_item['num'],a_list[0:len(p_item['num'])])
						a_list=a_list[p_count:]
			count=count+1
			sol.append(item)
	else:
		sol.append({'input':'','p_name':'','part':0})	
	
	param={'question':q,'sol':sol}
	
	#for links
	param['subject']=subject.objects.all()
	
	#for csrf of dajax
	return render_to_response('add_math_qPreview.html',param,RequestContext(request))

#delete question
def AddMaths_qDelete(request,list_type,page_no,subj_id):
	q_id=request.POST.get('d_q_id','')
	
	#delete question
	qn=question.objects.get(id=q_id)
	qn.delete();
	
	#delete answer
	ans=answer.objects.filter(question_id=q_id)
	ans.delete();
	
	#delete relevant tags
	tags=tag.objects.filter(question_id=q_id)
	tags.delete();
	
	return add_math_question(request,list_type,subj_id,page_no)
	
#accept values from form to insert or modify question
def AddMaths_qChange(request,list_type,page_no,subj_id):
	#subject id(replace with parameter on implementation
	#subj_id=1

	q_id=request.POST.get('a_q_id','')
	q_content=request.POST.get('a_content','')
	q_sol=request.POST.get('a_sol','')
	q_input=request.POST.get('a_input','')
	q_type=request.POST.get('a_type','')
	q_ans=request.POST.get('a_ans','')
	q_tag=request.POST.get('a_tag','')
	q_new_tag=request.POST.get('a_new_tag','')
	
	q_item=None
	if(q_id!=''):
		q_item=question.objects.get(id=q_id)
	else:
		#question number
		q_no=1
		#for new question, find or insert paper
		q_year=request.POST.get('paper_year','')
		q_month=request.POST.get('paper_month','')
		q_num=request.POST.get('paper_num','')
		q_topic=request.POST.get('paper_topic','')
		q_paper_id=q_year
		if(q_month=='6' and q_num=='1'):
			q_paper_id=q_paper_id+'01'
		elif(q_month=='6' and q_num=='2'):
			q_paper_id=q_paper_id+'02'
		elif(q_month=='11' and q_num=='1'):
			q_paper_id=q_paper_id+'03'
		elif(q_month=='11' and q_num=='2'):
			q_paper_id=q_paper_id+'04'
		q_paper_id=q_paper_id+'{0:0>3}'.format(subj_id)
		cur_paper=paper.objects.filter(id=q_paper_id)
		if(len(cur_paper)==0):
			cur_paper=paper()
			cur_paper.id=q_paper_id
			cur_paper.year=q_year
			if(q_month=='6'):
				cur_paper.month='June'
			elif(q_month=='11'):
				cur_paper.month='November'
			cur_paper.number=q_num
			cur_paper.subject_id=subject.objects.get(id=subj_id)
			cur_paper.save()
		else:
			q_no=len(question.objects.filter(paper_id=q_paper_id))+1
			
		q_item=question()
		#generate id
		q_item.id=q_year+'{0:0>3}'.format(subj_id)
		if(q_month=='6' and q_num=='1'):
			q_item.id=q_item.id+'01'
		elif(q_month=='6' and q_num=='2'):
			q_item.id=q_item.id+'02'
		elif(q_month=='11' and q_num=='1'):
			q_item.id=q_item.id+'03'
		elif(q_month=='11' and q_num=='2'):
			q_item.id=q_item.id+'04'
		q_item.id=q_item.id+'{0:0>3}'.format(q_no)
		#end
		q_item.subtopic_id_id=q_topic
		q_item.topic_id_id=subtopic.objects.get(id=q_topic).topic_id_id
		q_item.paper_id=paper.objects.get(id=q_paper_id)
		q_item.question_no=q_no
	
	q_item.content=q_content
	q_item.input=q_input
	q_item.type=q_type
	q_item.type_answer=q_ans
	
	#must include
	q_item.q_category=''
	q_item.q_type='exam'
	q_item.difficulty_level=''
	q_item.num_views='0'
	
	q_item.save()
	
	#tag update
	oldtags = tag.objects.filter(question_id=q_item.id)
	oldtags.delete()
	
	#existing tag format
	etags = q_tag.split(';') #split into tags
	for etag in etags:
		if etag != '':
			if len(tag_definitions.objects.filter(id=int(etag))) > 0: #verify tag exists
				tagdef = tag_definitions.objects.get(id=int(etag))
				new_etag_record = tag(question_id=q_item, tag=tagdef)
				new_etag_record.save()
	#new tag format
	ntags = q_new_tag.split('||') #split into tags
	for ntag in ntags:
		columns = ntag.split(';')
		if len(columns) == 3: #title, content, type
			new_ntag_record = tag_definitions(title=columns[0], content=columns[1], type=columns[2])
			new_ntag_record.save() #create the new tag first
			new_etag_record = tag(question_id=q_item, tag=new_ntag_record)
			new_etag_record.save() #save the relationship with the question
	
	#answer update
	if len(answer.objects.filter(question_id=q_item.id)) > 0: #update existing
		cur_answer = answer.objects.get(question_id=q_item.id)
		cur_answer.content = q_sol
		cur_answer.save()
	else:
		cur_answer = answer(question_id=q_item, content=q_sol)
		cur_answer.save()
		
	return add_math_question(request,list_type,subj_id,page_no)

#display questions with missing solutions
def find_missing_sol(request):
	
	param={}
	
	#get list of questions
	sel=list(topic.objects.filter(subject_id=1).only('id').order_by('id').values())
	stopic=[]
	for sel_topic in sel:
		stopic[0:0]=list(subtopic.objects.filter(topic_id=sel_topic['id']).only('id','title').order_by('id').values())
	sel=[]
	for sel_topic in stopic:
		sel[0:0]=list(question.objects.filter(subtopic_id=sel_topic['id']).only('id','paper_id_id','subtopic_id_id','type','type_answer').order_by('id').values())
	
	#list of papers
	paperlist=list(paper.objects.filter(subject_id=1,number__gt=0).only('id','year','month').order_by('id').values())
	
	#get list of questions with missing answers
	q_miss=[]
	for q in sel:
		if ((';'+q['type_answer']).find(';;')>=0):
			q_miss.append(q)
			q['s_list']=zip(q['type'].split(';'),q['type_answer'].split(';'))
			for p in paperlist:
				if (p['id']==q['paper_id_id']):
					q['cur_paper']=p['month']+' '+p['year']+' Paper'+str(p['number'])
					break
	
	param['questions']=q_miss
	
	#for links
	param['subject']=subject.objects.all()
	
	return render_to_response('add_math_admin_missing_questions.html',param,RequestContext(request))

#display tag list	
def AddMaths_Admin_TagList(request):
	param={}
	
	tag_type=request.GET.get('type')
	param['type']=tag_type
	
	if tag_type != None:
		taglist = tag_definitions.objects.filter(type=tag_type).order_by('title')
		param['taglist']=taglist
	
	return render_to_response('add_math_admin_taglist.html',param,RequestContext(request))

#regenerate keywords
def AddMaths_Admin_RegenKeyword(request):
	param={}
	
	keywords = tag_definitions.objects.filter(type='K')
	#delete old keywords relationships
	oldkeywordtags = tag.objects.filter(tag__in=keywords)
	oldkeywordtags.delete()
	
	for keyword in keywords:
		keywordfound = question.objects.filter(content__regex='[[:<:]]'+keyword.content+'[[:>:]]') #search for keyword
		for kf in keywordfound:
			#create new tag relationship
			newtag = tag(question_id=kf, tag=keyword)
			newtag.save()
	
	
	return render_to_response('add_math_admin_taglist.html',param,RequestContext(request))

#delete a tag
def AddMaths_Admin_DeleteTag(request):
	param={}
	
	tag_id = int(request.GET.get('id'))
	
	if tag_id > 0:
		tagdef = tag_definitions.objects.get(id=tag_id)
		tags = tag.objects.filter(tag=tagdef)
		tags.delete()
		tagdef.delete()
	
	return render_to_response('add_math_admin_taglist.html',param,RequestContext(request))

#create/modify a tag	
def AddMaths_Admin_TagForm(request):
	param={}
	param['topics'] = topic.objects.all()
	
	tag_id = 0
	if request.GET.get('id') != None:
		tag_id = int(request.GET.get('id'))
	
	if tag_id > 0:
		tagdef = tag_definitions.objects.get(id=tag_id)
		param['tag_def'] = tagdef
	
	return render_to_response('add_math_admin_tagform.html',param,RequestContext(request))

#save a tag	
def AddMaths_Admin_SaveTag(request):
	param={}
	
	#parameter values
	tag_id=request.POST.get('tag_id','')
	tag_title=request.POST.get('title','')
	tag_type=request.POST.get('type','')
	tag_topic=request.POST.get('topic','')
	tag_content=request.POST.get('desc','')
	
	if tag_id != '': #existing tag
		tagdef = tag_definitions.objects.get(id=tag_id) #retrieve old object
		if tag_title != '' and tag_type != '': #check mandatory attributes before modifications
			tagdef.title = tag_title
			tagdef.type = tag_type
			if int(tag_topic) == 0: #null a topic if not assigned
				tagdef.topic = None
			else:
				tagdef.topic = topic.objects.get(id=tag_topic) #assign topic
			tagdef.content = tag_content
			tagdef.save()
	else: #new tag
		if tag_title != '' and tag_type != '': #check mandatory attributes before modifications
			tpc = None
			if tag_topic > 0:
				tpc = topic.objects.get(id=tag_topic) #assign topic if found
			tagdef = tag_definitions(title=tag_title, type=tag_type, topic=tpc, content=tag_content)
			tagdef.save()
	
	return render_to_response('add_math_admin_taglist.html',param,RequestContext(request))
	
#_________________________ Analyzer section ______________________________#

#main page for analyzer. basically no computation at the moment. keep for future use to make dashboard
def analyzer_main(request,subj_id):
	param={}
	param['subj_id']=subject.objects.get(id = subj_id)
	
	return render_to_response('analyzer_main.html',param,RequestContext(request))

	
#Tag class for tags	
class Tag:
    def __init__(self, name, count):
		self.name = name
		self.count = count
		self.reference = reference
    # Return a string representation of this Point
    def __repr__(self):
        return self

#Paper Tag section		
def analyzer_paper_tag(request,subj_id):
	param={}
	
	#query list of papersets
	param['papersets']=paperset.objects.filter(subject_id=subj_id).order_by('id')
	
	#default dropdownlist options
	paperset_id = 0
	tag_type = "All"
	combi = 0
	
	if request.GET.get("paperset_id") != None: #compute only when a paperset is selected
		#get tag cloud settings
		paperset_id = request.GET.get("paperset_id")
		combi = int(request.GET.get("combi"))
		tag_type = request.GET.get("tag_type")
		
		#retrieve the questions
		paper_ids = paper.objects.filter(paperset_id=paperset_id).values('id')	
		qnlist = question.objects.filter(paper_id__in=paper_ids).values('id')
		
		if (combi == 1): #singular-tag cloud
			onetags=None
			if (tag_type == "All"): #for all tags
				onetags = tag.objects.filter(question_id__in=qnlist).values('tag__id', 'tag__title').annotate(tag_count=Count('tag')).order_by('tag__title') #get list of tags
			elif (tag_type == "CF"): #concepts and formulae only
				onetags = tag.objects.filter(question_id__in=qnlist, tag__type__in='C,F').values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
			else: #individual types
				onetags = tag.objects.filter(question_id__in=qnlist, tag__type=tag_type).values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
			
			#tag cloud settings
			f_max = 36 #font size maximum
			#font size is determined by:
			#IF the current frequency is not minimum, then its integer is int(math.ceil((f_max*(t_i - t_min))/(t_max - t_min)))
			#ELSE the minimum font size is 10
			size = lambda f_max, t_max, t_min, t_i : t_i > t_min and 10 + int(math.ceil((f_max*(t_i - t_min))/(t_max - t_min))) or 10
			#finding the t_min and t_max
			t_min = 999999 #min frequency initialized as 999999 at first
			t_max = 0 #max frequency initialized as 0 at first
			
			#calibrating the max min fonts
			for tagitem in onetags:
				tagdef = tag_definitions.objects.get(id=tagitem['tag__id'])
				tagitem['tag__content'] = tagdef.content
				tagitem['tag__type'] = tagdef.type
				if tagitem['tag_count'] < t_min:
					t_min = tagitem['tag_count']
				if tagitem['tag_count'] > t_max:
					t_max = tagitem['tag_count']	
			
			#packing the tag cloud
			onecloud=[]
			for tagitem in onetags:
				onecloud.append({'id': tagitem['tag__id'],
							  'tag': tagitem['tag__content'],
							  'type': tagitem['tag__type'],
							  'title': tagitem['tag__title'],
							  'count': tagitem['tag_count'],
							  'size': size(f_max,t_max,t_min,tagitem['tag_count'])})
			param['onecloud'] = onecloud
		else: #multi-tags cloud
			multicloud=[]
			tagcollection=[]
			c = Counter()
			questions = question.objects.filter(id__in=qnlist).prefetch_related('tags') # prefetch M2M
			for q in questions:
				# sort them so 'point' + 'curve' == 'curve' + 'point'
				tags = None
				if (tag_type == "All"): #all tags
					tags = sorted([t.tag for t in q.tags.all()])
				elif (tag_type == "CF"): #concepts and formulae only
					tags = sorted([t.tag for t in q.tags.filter(tag__type__in="C,F")])
				else: #individual types
					tags = sorted([t.tag for t in q.tags.filter(tag__type=tag_type)])
				c.update(combinations(tags,combi)) # get all combinations and update counter
			for key, value in c.most_common(50): # show the top 50
				#build the display format
				keytitle=''
				keylink=''
				for k in key:
					keytitle += k.title + ', '
					keylink += str(k.id) + '|'
				keytitle=keytitle[0:len(keytitle)-2]
				keylink=keylink[0:len(keylink)-1]
				#pack to the cloud
				multicloud.append({'tag': keytitle, 'link':keylink, 'count': value})
			param['multicloud']=multicloud
		
		#pack the tag legend
		tagset=None
		if (tag_type == "All"): #all tags
			tagset = tag.objects.filter(question_id__in=qnlist).values('tag__id', 'tag__title').annotate(tag_count=Count('tag')).order_by('tag__title') #get list of tags
		elif (tag_type == "CF"): #concept and formula only
			tagset = tag.objects.filter(question_id__in=qnlist, tag__type__in='C,F').values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
		else: #individual types
			tagset = tag.objects.filter(question_id__in=qnlist, tag__type=tag_type).values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
		
		conceptTags=[]
		formulaTags=[]
		for tagitem in tagset:
			tagdef = tag_definitions.objects.get(id=tagitem['tag__id'])
			tagitem['tag__content'] = tagdef.content
			if tagdef.type == "C":
				conceptTags.append({'title': tagitem['tag__title'],
									'content': tagitem['tag__content']})
			elif tagdef.type == "F":
				formulaTags.append({'title': tagitem['tag__title'],
									'content': tagitem['tag__content']})
		param['conceptTags'] = conceptTags
		param['formulaTags'] = formulaTags
		
	param['paperset_id'] = int(paperset_id)
	param['subj_id'] = subj_id
	param['combi'] = combi
	param['tag_type'] = tag_type
	param['subj_id_id']=subject.objects.get(id = subj_id)
	
	return render_to_response('analyzer_paper_tag.html',param,RequestContext(request))

#Topic distribution section	
def analyzer_paper_topic_distribution(request,subj_id):
	param={}
	
	#query list of papers
	param['papersets']=paperset.objects.filter(subject_id=subj_id).order_by('id')
	
	paperset_id = 0 #default
	type="percent" #default
	if request.GET.get("paperset_id") != None: #compute only if paperset is chosen
		#get distribution settings
		topics = topic.objects.filter(subject_id=subj_id).order_by('id')
		paperset_id = request.GET.get("paperset_id")
		type = request.GET.get("type")
		
		#retrieve the papers
		paper_ids = paper.objects.filter(paperset_id=paperset_id).values('id')
		
		dataset=[]
		
		#graph starts here
		total_marks=0
		topicData=[]
		sidebarData=[]
	
		for t in topics:
			if type == "percent": #by marks weightage
                                
				t_questions = question.objects.filter(topic_id=t.id, paper_id__in=paper_ids)
				
				topic_marks = 0 #each topic starts at 0 marks distribution
				
				if len(t_questions) != 0:
                               
					for t_question in t_questions:
						topic_marks += t_question.marks #accumulate the marks
					#update data point to dataset
					if topic_marks > 0:
						dataset.append({'name': t.title,
										'value': topic_marks})
				total_marks+=topic_marks #add to total marks
				
			elif type == "count": #by question count weightage
				t_questions = question.objects.filter(topic_id=t.id, paper_id__in=paper_ids)
				topic_count = len(t_questions) #topic count is number of question related to this topic
				#update data point to dataset
				if topic_count > 0:
					dataset.append({'name': t.title,
									'value': topic_count})
			#for side-bar details
			qcount = len(question.objects.filter(topic_id=t.id, paper_id__in=paper_ids))
			if qcount > 0:
				topicData.append({'topic_id': t.id,
								  'topic_name': t.title,
								  'count': qcount})
		param['dataset']=dataset
		param['total_marks']=total_marks
		
		#append each paperset's title and topic data
		pset = paperset.objects.get(id=paperset_id)
		sidebarData.append({'paperset_id': pset.id,
							'paperset': pset.title,
							'topicdata': topicData})
		param['sidebarData'] = sidebarData
	param['paperset_id'] = int(paperset_id)
	param['subj_id'] = subj_id
	param['type'] = type
	
	param['subj_id_id']=subject.objects.get(id = subj_id)	
	return render_to_response('analyzer_paper_topic_distribution.html',param,RequestContext(request))
	
#Concept Distribution Section
def analyzer_paper_concept_distribution(request, subj_id):
	param = {}
	
	#query list of papers
	param['papersets']=paperset.objects.filter(subject_id=subj_id).order_by('id')
	param['topics']=topic.objects.filter(subject_id=subj_id).order_by('id')
	
	paperset_id = 0 #default
	topic_id = 0 #default
	if request.GET.get("paperset_id") != None: #compute only if paperset is chosen
		#get distribution settings
		topic_id = request.GET.get("topic_id")
		paperset_id = request.GET.get("paperset_id")
		
		#retrieve the papers
		paper_ids = paper.objects.filter(paperset_id=paperset_id).values('id')
		
		#retrieve the concepts
		concepts = tag_definitions.objects.filter(topic_id=topic_id, type="C")
		
		dataset=[] #for graph
		conceptData=[] #for sidebar links
		sidebarData=[] #for sidebar links
		
		#graph starts here
		total_count = 0
		for c in concepts:
			concept_count = 0
			questions = question.objects.filter(paper_id__in=paper_ids)
			for q in questions:
				tag_result = tag.objects.filter(question_id=q.id, tag_id=c.id)
				if len(tag_result) > 0: #question has concept
					concept_count += 1
				total_count += 1
			if concept_count > 0:
				dataset.append({'name': c.title,
								'value': concept_count})
			conceptData.append({'concept_id': c.id,
								'concept_title': c.title,
								'count': concept_count})
		pset = paperset.objects.get(id=paperset_id)
		sidebarData.append({'paperset_id': pset.id,
							'paperset': pset.title,
							'concepts': conceptData})
		param['dataset'] = dataset
		param['totalcount'] = total_count
		param['sidebarData'] = sidebarData
	param['paperset_id'] = int(paperset_id)
	param['topic_id'] = int(topic_id)
	param['subj_id'] = subj_id	
	param['subj_id_id']=subject.objects.get(id = subj_id)
	
	return render_to_response('analyzer_paper_concept_distribution.html', param, RequestContext(request))

#Topic Trend Section	
def analyzer_paper_topic_trend(request,subj_id):
	param={}
	
	#query list of papers
	param['papersets']=paperset.objects.filter(subject_id=subj_id).order_by('id')
	
	#defaults
	start_paperset_id = -1 
	end_paperset_id = -1
	topicall = ''
	type = ''
	sel_topics = []
	
	#retrieve settings
	if request.GET.get("start_paperset") != None:
		start_paperset_id = request.GET.get("start_paperset")
	if request.GET.get("end_paperset") != None:
		end_paperset_id = request.GET.get("end_paperset")
	if request.GET.getlist("topic") != None:
		sel_topics = request.GET.getlist("topic")
	if request.GET.get("topicall") != None:
		topicall = request.GET.get("topicall")
	if request.GET.get("type") != None:
		type = request.GET.get("type")
	
	#extract the topic list from checkboxes
	topicstring = ''
	topiclist=list()
	for t in sel_topics:
		topicstring += t + ','
		topiclist.append(int(t))
	
	#for sidebar data
	sidebarData=[]
	yTitle=''
	graphData=[]
	papersets = paperset.objects.filter(id__gte=start_paperset_id,id__lte=end_paperset_id)
	for pset in papersets:
		paper_ids = paper.objects.filter(paperset_id=pset.id).values('id')
		qnlist = question.objects.filter(paper_id__in=paper_ids).values('topic_id').annotate(total_qn=Count('id')).order_by('topic_id')
		#get each topic title and number of questions
		topicData=[]
		for qn in qnlist:
			if qn['topic_id'] in topiclist:
				topicData.append({'topic_id': qn['topic_id'],
								  'topic_name': topic.objects.get(id=qn['topic_id']).title,
								  'count': qn['total_qn']})
		#append each paperset's title and topic data
		sidebarData.append({'paperset_id': pset.id,
							'paperset': pset.title,
							'topicdata': topicData})
		#graph data
		valuelist=[]
		yTitle=''
		topics = topic.objects.filter(id__in=sel_topics).order_by('id')
		param['x_axis'] = topics #x axis display
		if type ==  "percent": #by marks weightage
			yTitle="Percentage %"
			qnlist = question.objects.filter(paper_id__in=paper_ids).values('topic_id').annotate(topic_marks=Sum('marks')).order_by('topic_id')
			papertotal = question.objects.filter(paper_id__in=paper_ids).aggregate(total_marks=Sum('marks'))
			
			#find percentage for each topic
			for tpc in topics:
				percent = 0
				for qn in qnlist:
					if (qn['topic_id'] == tpc.id):
						marks = qn['topic_marks']
						percent = marks*100 / float(papertotal['total_marks'])
				valuelist.append(percent)
		elif type == "count": #by question count
			yTitle="Question Count"
			qnlist = question.objects.filter(paper_id__in=paper_ids).values('topic_id').annotate(total_qn=Count('topic_id')).order_by('topic_id')
			
			#find count for each topic
			for tpc in topics:
				totalqn = 0
				for qn in qnlist:
					if (qn['topic_id'] == tpc.id):
						totalqn = qn['total_qn']
				valuelist.append(totalqn)
		
		#update graph data point
		graphData.append({'name': pset.title,
						  'value': valuelist})
	
	param['sidebarData'] = sidebarData
	param['yTitle'] = yTitle
	param['graphData'] = graphData
	param['start_paperset_id'] = int(start_paperset_id)
	param['end_paperset_id'] = int(end_paperset_id)
	param['subj_id'] = subj_id
	param['topicall'] = topicall
	param['topicstring'] = topicstring
	param['type'] = type
	param['sel_topics'] = topiclist
	param['topics']=topic.objects.filter(subject_id_id=subj_id).order_by('id')
	param['subj_id_id']=subject.objects.get(id = subj_id)
	
	return render_to_response('analyzer_paper_topic_trend.html',param,RequestContext(request))

#Concept Trend Section
def analyzer_paper_concept_trend(request, subj_id):
	param={}
	
	#query list of papers
	param['papersets']=paperset.objects.filter(subject_id=subj_id).order_by('id')
	param['topics']=topic.objects.filter(subject_id=subj_id).order_by('id')
	
	#defaults
	start_paperset_id = -1 
	end_paperset_id = -1
	topic_id = -1
	
	#retrieve settings
	if request.GET.get("start_paperset") != None:
		start_paperset_id = request.GET.get("start_paperset")
	if request.GET.get("end_paperset") != None:
		end_paperset_id = request.GET.get("end_paperset")
	if request.GET.get("topic_id") != None:
		topic_id = request.GET.get("topic_id")
	
	#for sidebar data
	sidebarData=[]
	
	graphData=[]
	papersets = paperset.objects.filter(id__gte=start_paperset_id,id__lte=end_paperset_id)
	concepts = tag_definitions.objects.filter(topic_id=topic_id, type="C")
	
	for pset in papersets:
		valuelist=[]
		paper_ids = paper.objects.filter(paperset_id=pset.id).values('id')
		qnlist = question.objects.filter(paper_id__in=paper_ids).values('id')
		conceptData=[]
		for concept in concepts:
			concept_count = len(tag.objects.filter(question_id_id__in=qnlist, tag_id=concept.id))
			conceptData.append({'concept_id': concept.id,
								'concept_title': concept.title,
								'count': concept_count})
			valuelist.append(concept_count)
		graphData.append({'name': pset.title,
						'value': valuelist})
		sidebarData.append({'paperset_id': pset.id,
							'paperset': pset.title,
							'concept': conceptData})
	
	param['graphData'] = graphData
	param['sidebarData'] = sidebarData
	param['start_paperset_id'] = int(start_paperset_id)
	param['end_paperset_id'] = int(end_paperset_id)
	param['subj_id'] = subj_id
	param['topic_id'] = int(topic_id)
	param['concepts']=concepts
	param['subj_id_id']=subject.objects.get(id = subj_id)
	
	return render_to_response('analyzer_paper_concept_trend.html', param, RequestContext(request))
	
	
#K-Means Section
# -- The Point class represents points in n-dimensional space
class Point:
    # Instance variables
    # self.coords is a list of coordinates for this Point
    # self.n is the number of dimensions this Point lives in (ie, its space)
    # self.reference is an object bound to this Point
    # Initialize new Points
    def __init__(self, coords, reference):
		self.coords = coords
		self.n = len(coords)
		self.reference = reference
    # Return a string representation of this Point
    def __repr__(self):
        return self
# -- The Cluster class represents clusters of points in n-dimensional space
class Cluster:
    # Instance variables
    # self.points is a list of Points associated with this Cluster
    # self.n is the number of dimensions this Cluster's Points live in
    # self.centroid is the sample mean Point of this Cluster
    def __init__(self, points):
        # We forbid empty Clusters (they don't make mathematical sense!)
        if len(points) == 0: raise Exception("ILLEGAL: EMPTY CLUSTER")
        self.points = points
        self.n = points[0].n
        # We also forbid Clusters containing Points in different spaces
        # Ie, no Clusters with 2D Points and 3D Points
        for p in points:
            if p.n != self.n: raise Exception("ILLEGAL: MULTISPACE CLUSTER")
        # Figure out what the centroid of this Cluster should be
        self.centroid = self.calculateCentroid()
    # Return a string representation of this Cluster
    def __repr__(self):
        return self.points
    # Update function for the K-means algorithm
    # Assigns a new list of Points to this Cluster, returns centroid difference
    def update(self, points):
        old_centroid = self.centroid
        self.points = points
        self.centroid = self.calculateCentroid()
        return getDistance(old_centroid, self.centroid)
    # Calculates the centroid Point - the centroid is the sample mean Point
    # (in plain English, the average of all the Points in the Cluster)
    def calculateCentroid(self):
        centroid_coords = []
        # For each coordinate:
        for i in range(self.n):
            # Take the average across all Points
            centroid_coords.append(0.0)
            for p in self.points:
                centroid_coords[i] = centroid_coords[i]+p.coords[i]
            centroid_coords[i] = centroid_coords[i]/len(self.points)
        # Return a Point object using the average coordinates
        return Point(centroid_coords, None)
# -- Return Clusters of Points formed by K-means clustering
def kmeans(points, k, cutoff):

    initial = random.sample(points, k)
    clusters = [Cluster([p]) for p in initial]
    while True:
		newPoints = dict([(c,[]) for c in clusters])
		for p in points:
			cluster = min(clusters, key = lambda c:getDistance(p, c.centroid))
			newPoints[cluster].append(p)

		biggest_shift = 0.0

		for c in clusters:
			if newPoints[c]:
				shift = c.update(newPoints[c])
				biggest_shift = max(biggest_shift, shift)

		if biggest_shift < cutoff:
			break

    return clusters
# -- Get the Euclidean distance between two Points
def getDistance(a, b):
    # Forbid measurements between Points in different spaces
    if a.n != b.n: raise Exception("ILLEGAL: NON-COMPARABLE POINTS")
    # Euclidean distance between a and b is sqrt(sum((a[i]-b[i])^2) for all i)
    ret = 0.0
    for i in range(a.n):
        ret = ret+pow((a.coords[i]-b.coords[i]), 2)
    return math.sqrt(ret)

#Clustering Section	
def analyzer_topic_cluster(request,subj_id):
	param={}
	
	#list of topics for dropdownlist
	topics=list(topic.objects.filter(subject_id=subj_id).order_by('id').values())
	param['topics']=topics
	
	#kvalue dropdown choices
	kvaluelist = ['Use Default', 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
	param['kvaluelist']=kvaluelist
	
	topic_id = 13 #default None is 13
	
	if request.GET.get("topic_id") != None: #compute only if topic chosen
		#get topic object
		topic_id = request.GET.get("topic_id")
		topicObj = topic.objects.get(id=topic_id)
		
		k = 0 #initialize k
		if topicObj != None:
			kvalue = request.GET.get("k_value") #retrieve k-value if defined by user
			param['k_value'] = kvalue
			if kvalue != None: #if found
				if kvalue == "Use Default": #if told to use default
					k = topicObj.kvalue
				else: #user-defined
					k = int(kvalue)
			else: #go by default from topic
				k = topicObj.kvalue
		
			cutoff = 0.5 #by default
			points=[] #empty points
			
			#get all distinct tags
			distinctTags = tag.objects.filter(question_id__in=question.objects.filter(topic_id=topic_id).values('id')).values('tag__content','tag__title').order_by('tag__content').annotate()
			
			for q in question.objects.filter(topic_id=topic_id).values(): #all questions in selected topic
				questiontags = tag.objects.filter(question_id=q['id']).values('tag__content','tag__title').order_by('tag__content') #get tag list for the question
				
				#build document vector
				point=[]
				for t in distinctTags:
					if t in questiontags:
						point.append(1)
					else:
						point.append(0)
				
				#reference data
				paperobj = paper.objects.get(id=q['paper_id_id'])
				papertitle=str(paperobj.year) + ' ' + paperobj.month + ' Paper ' + str(paperobj.number)
				
				#add in Point with document vector, question object, paper, taglist
				pt=Point(point, q)
				pt.paper = papertitle
				tagstring=''
				for p in questiontags:
					tagstring += p['tag__title'] + ', '
				tagstring=tagstring[0:len(tagstring)-2]
				pt.taglist = tagstring
				pt.display = process_question(q)
				points.append(pt)
			
			#do the clustering
			clusters = kmeans(points, k, cutoff)
			
			#post-process to fit visualization
			for i, c in enumerate(clusters):
				group_id=[]
				for p in c.points:
					group_id.append(p.reference['id'])
				commontags = tag.objects.filter(question_id__in=group_id).values('tag__title','tag__content').annotate(tag_count=Count('tag__title')).filter(tag_count__gte=len(group_id))
				for common in commontags:
					common['tag__type']= tag_definitions.objects.get(content=common['tag__content']).type
					common['tag__id']= tag_definitions.objects.get(content=common['tag__content']).id
				c.commontags = commontags
			
			#pass the result
			param['clusters'] = enumerate(clusters)
	
	param['subj_id'] = subj_id
	param['topic_id'] = int(topic_id)
	param['subj_id_id']=subject.objects.get(id = subj_id)
	
	return render_to_response('analyzer_topic_cluster.html',param,RequestContext(request))

#Topic Tag Section	
def analyzer_topic_tag(request,subj_id):
	param={}
	
	#list of topics for dropdownlist
	topics=list(topic.objects.filter(subject_id=subj_id).order_by('id').values())
	param['topics']=topics
	
	#default options
	topic_id = 13
	tag_type = "All"
	combi = 0
	
	if request.GET.get("topic_id") != None: #compute only if topic chosen
		#get settings
		topic_id = request.GET.get("topic_id")
		combi = int(request.GET.get("combi"))
		tag_type = request.GET.get("tag_type")
		
		#get question list
		qnlist = question.objects.filter(topic_id=topic_id).values('id')
		
		if (combi == 1): #one tag cloud
			onetags = None
			if (tag_type == "All"): #all tags
				onetags = tag.objects.select_related().filter(question_id__in=qnlist).values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
			elif (tag_type == "CF"): #concept and formula
				onetags = tag.objects.select_related().filter(question_id__in=qnlist, tag__type__in='C,F').values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
			else: #individual type
				onetags = tag.objects.select_related().filter(question_id__in=qnlist, tag__type=tag_type).values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
			#tag cloud settings
			f_max = 36 #font size maximum
			#font size is determined by:
			#IF the current frequency is not minimum, then its integer is int(math.ceil((f_max*(t_i - t_min))/(t_max - t_min)))
			#ELSE the minimum font size is 10
			size = lambda f_max, t_max, t_min, t_i : t_i > t_min and 10 + int(math.ceil((f_max*(t_i - t_min))/(t_max - t_min))) or 10
			#finding the t_min and t_max
			t_min = 999999 #min frequency initialized as 999999 at first
			t_max = 0 #max frequency initialized as 0 at first
			
			#calibrating the min max font
			for tagitem in onetags:
				tagdef = tag_definitions.objects.get(id=tagitem['tag__id'])
				tagitem['tag__content'] = tagdef.content
				tagitem['tag__type'] = tagdef.type
				if tagitem['tag_count'] < t_min:
					t_min = tagitem['tag_count']
				if tagitem['tag_count'] > t_max:
					t_max = tagitem['tag_count']
					
			#packing the tag cloud
			onecloud = []
			for tagitem in onetags:
				onecloud.append({'id': tagitem['tag__id'],
							  'tag': tagitem['tag__content'],
							  'type': tagitem['tag__type'],
							  'title': tagitem['tag__title'],
							  'count': tagitem['tag_count'],
							  'size': size(f_max,t_max,t_min,tagitem['tag_count'])})
			param['onecloud'] = onecloud
		else: #multi-tag cloud
			multicloud=[]
			c = Counter()
			
			questions = question.objects.filter(id__in=qnlist).prefetch_related('tags') # prefetch M2M
			
			for q in questions:
				# sort them so 'point' + 'curve' == 'curve' + 'point'
				tags = None
				if (tag_type == "All"): #all tags
					tags = sorted([t.tag for t in q.tags.all()])
				elif (tag_type == "CF"): #concept and formula
					tags = sorted([t.tag for t in q.tags.filter(tag__type__in='C,F')])
				else: #individual type
					tags = sorted([t.tag for t in q.tags.filter(tag__type=tag_type)])
				c.update(combinations(tags,combi)) # get all combinations and update counter
			for key, value in c.most_common(50): # show the top 50
				#format the display
				keytitle=''
				keylink=''
				for k in key:
					keytitle += k.title + ', '
					keylink += str(k.id) + '|'
				keytitle=keytitle[0:len(keytitle)-2]
				keylink=keylink[0:len(keylink)-1]
				#pack to cloud
				multicloud.append({'tag': keytitle, 'link':keylink, 'count': value})
			param['multicloud']=multicloud
		
		#pack the tag legend
		tagset=None
		if (tag_type == "All"):
			tagset = tag.objects.select_related().filter(question_id__in=qnlist).values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
		elif (tag_type == "CF"):
			tagset = tag.objects.select_related().filter(question_id__in=qnlist, tag__type__in='C,F').values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
		else:
			tagset = tag.objects.select_related().filter(question_id__in=qnlist, tag__type=tag_type).values('tag__id', 'tag__title').annotate(tag_count=Count('tag__title')).order_by('tag__title') #get list of tags
		
		conceptTags=[]
		formulaTags=[]
		for tagitem in tagset:
			tagdef = tag_definitions.objects.get(id=tagitem['tag__id'])
			tagitem['tag__content'] = tagdef.content
			if tagdef.type == "C":
				conceptTags.append({'title': tagitem['tag__title'],
									'content': tagitem['tag__content']})
			elif tagdef.type == "F":
				formulaTags.append({'title': tagitem['tag__title'],
									'content': tagitem['tag__content']})
		param['conceptTags'] = conceptTags
		param['formulaTags'] = formulaTags
	
	param['topic_id'] = int(topic_id)
	param['subj_id'] = subj_id
	param['combi'] = combi
	param['tag_type'] = tag_type
	param['subj_id_id']=subject.objects.get(id = subj_id)
		
	return render_to_response('analyzer_topic_tag.html',param,RequestContext(request))

#For search result	
def result(request,page_no):
	param={}
	
	#get parameters from HTTP GET
	tags=[]
	if request.GET.getlist("tag") != None:
		tags = request.GET.getlist("tag")
	topic_id = 0
	if request.GET.get("topic") != None:
		topic_id = int(request.GET.get("topic"))
	type = "search" # default
	if request.GET.get("type") != None:
		type = request.GET.get("type")
		
	#from the type (paper or topic) passed, query for questions
	sel=[]
	image_sel=[]
	#get questions
	tag_list=list(tag.objects.filter(tag__title__in=tags).order_by('question_id').values('question_id').annotate(q_count=Count('question_id')).filter(q_count__gte=len(tags)))
	qid_set=[]
	for tagitem in tag_list:
		qid_set.append(tagitem['question_id'])
	global_sel = list(question.objects.filter(id__in=qid_set).only('id','content','question_no','marks').order_by('id').values())
	
	#get images
	global_image_sel = list(image.objects.filter(qa_id__in=qid_set).order_by('qa_id').values())
	global_image_id = list(image.objects.filter(qa_id__in=qid_set).order_by('qa_id').values('qa_id'))
	image_qid_set=[]
	for image_item in global_image_id:
		image_qid_set.append(image_item['qa_id'])
	global_image_q_sel = list(question.objects.filter(id__in=image_qid_set).only('id','content','question_no','marks').order_by('id').values())
	
	
	#pack the topic bar
	topic_bar=topic.objects.all().order_by('title').values()
	for t in topic_bar:
		t['count'] = 0
	if type == "search":
		for q in global_sel:
			for t in topic_bar:
				if q['topic_id_id'] == t['id']:
					t['count'] += 1
	elif type == "image":
		for q in global_image_sel:
			for t in topic_bar:
				if question.objects.get(id=q['qa_id']).topic_id_id == t['id']:
					t['count'] += 1
	
	param['topic_bar']=topic_bar
	
	#filter content
	if type == "search":
		if topic_id > 0: #filter by topic
			sel = list(question.objects.filter(id__in=qid_set, topic_id_id=topic_id).only('id','content','question_no','marks').order_by('id').values())
		else: #all topics
			sel = global_sel
	elif type == "image":
		if topic_id > 0: #filter by topic
			image_q_sel = list(question.objects.filter(id__in=image_qid_set, topic_id_id=topic_id).order_by('id').values('id'))
		else: #all topics
			image_q_sel = global_image_q_sel
		topic_image_qid_set=[]
		for image_item in image_q_sel:
			topic_image_qid_set.append(image_item['id'])
		image_sel = list(image.objects.filter(qa_id__in=topic_image_qid_set).order_by('qa_id').values())
	
	#to display number of questions (and assist in other operations)
	no_of_qn = 0
	if type == "search":
		no_of_qn=len(sel)
	elif type == "image":
		no_of_qn=len(image_sel)
	
	#addMaths_q_per_page is the number of questions per page
	#from the list and page number, display current page's questions
	if type == "image":
		addMaths_q_per_page = 25
	else:
		addMaths_q_per_page = 10
	page_items=[]
	for i in range(0,addMaths_q_per_page):
		if( (i + addMaths_q_per_page * (int(page_no) - 1))<no_of_qn):
			if type == "search":
				page_items.append(sel[i + addMaths_q_per_page * (int(page_no)-1)])
			elif type == "image":
				page_items.append(image_sel[i + addMaths_q_per_page * (int(page_no)-1)])
	
	#create links of pages (determine number of pages)
	no_pages=no_of_qn/addMaths_q_per_page
	if((no_of_qn % addMaths_q_per_page)!=0):
		no_pages=no_pages+1
	page_links=[]
	for i in range(1,no_pages+1):
		page_links.append(i)
	
	#call helper method to process content of each question
	if type == "search":
		for q in page_items:
			q['taglist']=[]
			q['topic']=topic.objects.get(id=q['topic_id_id']).title
			q['subtopic']=subtopic.objects.get(id=q['subtopic_id_id']).title
			p=paper.objects.get(id=q['paper_id_id'])
			q['paper']=str(p.year) + ' ' + p.month + ' Paper ' + str(p.number)
			q['display']=process_question(q)
			keywordTags = ''
			tags = request.GET.getlist("tag")
			for t in tags:
				tagdef = tag_definitions.objects.get(title=t)
				if tagdef.type == "K":
					keywordTags += tagdef.content + '|'
			keywordTags = keywordTags[0:len(keywordTags)]
			
			for qitem in q['display']:
				if qitem['type'] == 1:
					for keyword in keywordTags.split('|'):
						p = re.compile('^' + keyword + '$')
						newstring=''
						for word in qitem['value'].split():
							if word[-1:] == ',':
								word = word[0:len(word)-1]
								if p.match(word) != None:
									newstring += '<b>' + word + '</b>' + ', '
								else:
									newstring += word + ', '
							else:
								if p.match(word) != None:
									newstring += '<b>' + word + '</b>' + ' '
								else:
									newstring += word + ' '
						qitem['value']=newstring
			q['displayans']=''
			if len(answer.objects.filter(question_id=q['id'])) > 0:
				ans=list(answer.objects.filter(question_id=q['id']).values())[0]
				q['displayans']=process_solution(ans)
			taglist = tag.objects.filter(question_id=q['id']).order_by('tag__title')
			if len(taglist) != 0:
				for t in taglist:
					q['taglist'].append(t)
	
	param['questions']=page_items
	param['page_links']=page_links
	param['page_no']=int(page_no)
	param['num_q']=no_of_qn
	if type == "search":
		param['global_total']=len(global_sel)
	elif type == "image":
		param['global_total']=len(global_image_sel)
	param['topic_id']=topic_id
	#fix tags into url get
	urltag=''
	for t in tags:
		urltag += 'tag=' + t + '&'
	urltag=urltag[0:len(urltag)-1]
	param['urltags']=urltag
	param['tags']=tags
	param['type']=type
			
	return render_to_response('result.html',param)
	
	
	
	#Formula Distribution Section
def analyzer_paper_formula_distribution(request, subj_id):
	param = {}
	
	#query list of papers
	param['papersets']=paperset.objects.filter(subject_id=subj_id).order_by('id')
	param['topics']=topic.objects.filter(subject_id=subj_id).order_by('id')
	
	paperset_id = 0 #default
	topic_id = 0 #default
	if request.GET.get("paperset_id") != None: #compute only if paperset is chosen
		#get distribution settings
		topic_id = request.GET.get("topic_id")
		paperset_id = request.GET.get("paperset_id")
		
		#retrieve the papers
		paper_ids = paper.objects.filter(paperset_id=paperset_id).values('id')
		
		#retrieve the concepts
		formula = tag_definitions.objects.filter(topic_id=topic_id, type="F")
		
		dataset=[] #for graph
		formulaData=[] #for sidebar links
		sidebarData=[] #for sidebar links
		
		#graph starts here
		total_count = 0
		for f in formula:
			formula_count = 0
			questions = question.objects.filter(paper_id__in=paper_ids)
			for q in questions:
				tag_result = tag.objects.filter(question_id=q.id, tag_id=f.id)
				if len(tag_result) > 0: #question has concept
					formula_count += 1
				total_count += 1
			if formula_count > 0:
				dataset.append({'name': f.title,
								'value': formula_count})
			formulaData.append({'formula_id': f.id,
								'formula_title': f.title,
								'count': formula_count})
		pset = paperset.objects.get(id=paperset_id)
		sidebarData.append({'paperset_id': pset.id,
							'paperset': pset.title,
							'formula': formulaData})
		param['dataset'] = dataset
		param['totalcount'] = total_count
		param['sidebarData'] = sidebarData
	param['paperset_id'] = int(paperset_id)
	param['topic_id'] = int(topic_id)
	param['subj_id'] = subj_id	
	param['subj_id_id']=subject.objects.get(id = subj_id)
	
	return render_to_response('analyzer_paper_formula_distribution.html', param, RequestContext(request))
	
	
	#Formula Trend Section
def analyzer_paper_formula_trend(request, subj_id):
	param={}
	
	#query list of papers
	param['papersets']=paperset.objects.filter(subject_id=subj_id).order_by('id')
	param['topics']=topic.objects.filter(subject_id=subj_id).order_by('id')
	
	#defaults
	start_paperset_id = -1 
	end_paperset_id = -1
	topic_id = -1
	
	#retrieve settings
	if request.GET.get("start_paperset") != None:
		start_paperset_id = request.GET.get("start_paperset")
	if request.GET.get("end_paperset") != None:
		end_paperset_id = request.GET.get("end_paperset")
	if request.GET.get("topic_id") != None:
		topic_id = request.GET.get("topic_id")
	
	#for sidebar data
	sidebarData=[]
	
	graphData=[]
	papersets = paperset.objects.filter(id__gte=start_paperset_id,id__lte=end_paperset_id)
	formulas = tag_definitions.objects.filter(topic_id=topic_id, type="F")
	
	for pset in papersets:
		valuelist=[]
		paper_ids = paper.objects.filter(paperset_id=pset.id).values('id')
		qnlist = question.objects.filter(paper_id__in=paper_ids).values('id')
		formulaData=[]
		for formula in formulas:
			formula_count = len(tag.objects.filter(question_id_id__in=qnlist, tag_id=concept.id))
			formulaData.append({'formula_id': formula.id,
								'formula_title': formula.title,
								'count': formula_count})
			valuelist.append(formula_count)
		graphData.append({'name': pset.title,
						'value': valuelist})
		sidebarData.append({'paperset_id': pset.id,
							'paperset': pset.title,
							'formula': formulaData})
	
	param['graphData'] = graphData
	param['sidebarData'] = sidebarData
	param['start_paperset_id'] = int(start_paperset_id)
	param['end_paperset_id'] = int(end_paperset_id)
	param['subj_id'] = subj_id
	param['topic_id'] = int(topic_id)
	param['formula']=formulas
	param['subj_id_id']=subject.objects.get(id = subj_id)
	
	return render_to_response('analyzer_paper_formula_trend.html', param, RequestContext(request))
	
