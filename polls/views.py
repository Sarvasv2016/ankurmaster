from _ctypes import sizeof
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import sqlite3
from polls.registerform import UserForm,UserProfileForm,InterestsForm,QuizRegForm
from polls.misc_functions import mail,mail2,random_num, tablechk, intrchk
from polls.models import ProfilePicture,UserProfile
import json,datetime
import time,threading
import _thread
from django.contrib.sessions.models import Session
import time
from django.db.models.signals import post_save
from django.dispatch import receiver

otp=0
Response=''

class myThread1(threading.Thread):
    def __init__(self, eid,quizname):
        threading.Thread.__init__(self)
  #      self.threadID = threadID
        self.eid = eid
        self.quizname = quizname
    def run(self):
         mail2(self.eid,self.quizname)
  #      print ("Exiting " + self.name)

def register(request):
   registered = False


   # If it's a HTTP POST, we're interested in processing form data
   print('chk0')
   if request.method == 'POST':
     if request.POST.get('emailid')!='0':
      eidstr= request.POST.get('emailid')
     else:
      eidstr= request.POST.get('emailid2')
     vara= tablechk('polls_userprofile','emailid', eidstr )
     if(vara==1):

       print("alpha"+str(vara))
       if request.POST.get('emailid')!='0':
         ajaxstr='chk1'
        # print(ajaxstr)
         user_form = UserForm(data=request.POST)

        # print('chk2')
         response_dict={}


         if request.POST.get('password') == request.POST.get('conpassword'):

              if vara==1:

                   print("kutta")
                   otpstr=mail(request.POST.get('emailid'))

                   message='mail sent'
                   str1= request.POST.get('emailid')
                   print("ert"+otpstr+str1)


                   # Save the user's form data to the database.
                   user = user_form.save()
                   # Now we hash the password with the set_password method.
                   # Once hashed, we can update the user object.
                   #user.password(user.password)
                   user.save()
                   conn = sqlite3.connect('db.sqlite3')
                   cursor=conn.cursor()
                   cursor.execute('''UPDATE polls_users SET otp = ? where emailid = ? ''',(otpstr,str1))
                   cursor.close()
                   conn.commit()
                   ajaxstr="Email sent"
                   registered= True
                   response_dict.update({'resp1' : ajaxstr, 'gamma' : 0})

                   return HttpResponse(json.dumps(response_dict),content_type='application/javascript')

              else:
                   ajaxstr='Email id already registered'
                   response_dict.update({'resp1' : ajaxstr,'gamma':0})
                   return HttpResponse(json.dumps(response_dict))
         else:
               return HttpResponse("Password don't match")

       else :
          response_dict={}
          gamma=0
          response_dict.update({'gamma':gamma, 'resp1': 'Email has been sent'})
          return HttpResponse(json.dumps(response_dict),content_type='application/javascript')
     else:
         response_dict={}
         gamma=1
         if(request.POST.get('emailid')==request.POST.get('emailid2')):
           response_dict.update({'gamma':gamma, 'resp1': 'Email id already registered'})
         else :
           response_dict.update({'gamma':gamma, 'resp1': 'Chal gaya', })
         return HttpResponse(json.dumps(response_dict),content_type='application/javascript')

   # Not a HTTP POST, so we render our form using two ModelForm instances.
   # These forms will be blank, ready for user input.
   else:
       user_form = UserForm()
       user_profileform = UserProfileForm()
       ajaxstr='Email has been sent4545'
       print(ajaxstr)

       # Render the template depending on the context.
       return render_to_response('polls/registerform.html',{'user_form': user_form,'user_profileform' : user_profileform ,'registered':registered},context_instance=RequestContext(request))

def ajax(request):
     if ('client_response') in request.POST:
        x = request.POST['client_response']
        if(otp==int(x)):
           # print (otp)
            Response='True'
        else:
            Response='False'

        response_dict = {'Response':Response}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
     else:
        return render_to_response('registerform.html', context_instance=RequestContext(request))

def transfer_details(request,eid,otp):

     conn = sqlite3.connect('db.sqlite3')
     cursor=conn.cursor()
     cursor.execute('''Select emailid from polls_users where emailid = ? and otp = ?''',(eid,otp))
     conn.commit()
     emailid_final=cursor.fetchone()
     cursor.execute('''Select password from polls_users where emailid = ? and otp = ?''',(eid,otp))
     conn.commit()
     password_final=cursor.fetchone()
     cursor.execute('''Select college from polls_users where emailid = ? and otp = ?''',(eid,otp))
     conn.commit()
     college_final=cursor.fetchone()
     cursor.execute('''Select username from polls_users where emailid = ? and otp = ?''',(eid,otp))
     username_final=cursor.fetchone()
     conn.commit()
     cursor.execute('''DELETE FROM polls_users where emailid = ?''', (eid,))
     conn.commit()
     cursor.execute('''INSERT INTO polls_userprofile (emailid, password, college,username) values(?,?,?,?)''',(emailid_final[0],password_final[0],college_final[0],username_final[0]))
     conn.commit()
     cursor.execute('''CREATE TABLE '''+request.session['username']+'''activity (quizname TEXT NOT NULL,starttime DATETIME NOT NULL, endtime DATETIME NOT NULL, points INTEGER NOT NULL, status INTEGER NOT NULL)''')
     conn.commit()
     request.session['last_visit'] = str(time.strftime("%H:%M:%S"))
     request.session['visits'] = 1
     request.session['eid']=eid
     request.session['otp']=otp
     new_sessionid=request.session._get_new_session_key()
     cursor.execute('''INSERT INTO polls_global (emailid, username, sessionid,is_loggedin) values(?,?,?,?)''',(emailid_final[0],username_final[0],new_sessionid ,True))
     conn.commit()
     user_profileform= UserProfileForm()
     return render_to_response('polls/registerform.html',{'user_form': user_profileform, 'eid' : eid, 'otp' : otp},context_instance=RequestContext(request))



def register2(request,eid,otp):
    if request.method=='POST':
        userprofile_form=UserProfileForm(request.POST, request.FILES)
        if userprofile_form.is_valid():
            firstname=request.POST['firstname']
            #lastname=request.POST['lastname']
            dob=request.POST['dob']
            #gender=request.POST['gender']
            #fathername=request.POST['fathername']
            #permaadd=request.POST['permaadd']
            contact=request.POST['contact']
            if 'picture' in request.FILES:
               userprofile_form.picture=request.FILES['picture']

            new=ProfilePicture(emailid=eid, picture=userprofile_form.picture)
            new.save()
            conn = sqlite3.connect('db.sqlite3')
            cursor=conn.cursor()
            cursor.execute('''UPDATE polls_userprofile SET firstname=?  ,dob=? ,contact =?  where emailid = ? ''',(firstname,dob,contact,eid,))
            print ('alpha')
            conn.commit()
            interest_form=InterestsForm()
            return render_to_response('polls/interestform.html',{'interest_form': interest_form, 'eid' : eid, 'otp' : otp},context_instance=RequestContext(request))

        else:
           # Invalid form or forms - mistakes or something else?
           # Print problems to the terminal.
           # They'll also be shown to the user.
            return HttpResponse(userprofile_form.errors)

    else:
            userprofile_form = UserProfileForm()

       # Render the template depending on the context.
            return render_to_response('polls/userprofileform.html',{'userprofile_form': userprofile_form},context_instance=RequestContext(request))



def register3(request,eid,otp):
     if request.method=='POST':
         interest_form=InterestsForm(data=request.POST)
         if interest_form.is_valid():
             interest1=request.POST['interest1']
             interest2=request.POST['interest2']
             interest3=request.POST['interest3']
             interest4=request.POST['interest4']
             interest5=request.POST['interest5']
             interest1=str(interest1)
             interest2=str(interest2)
             interest3=str(interest3)
             interest4=str(interest4)
             interest5=str(interest5)
             conn=sqlite3.connect('db.sqlite3')

             cursor=conn.cursor()
             cursor.execute('''UPDATE polls_userprofile SET interest1=?,interest2=?,interest3=?,interest4=?,interest5=? where emailid=? ''',(intrchk(interest1),intrchk(interest2),intrchk(interest3),intrchk(interest4),intrchk(interest5),eid,))
             conn.commit()

             return HttpResponse(" "+str(interest1))
         else :
             return HttpResponse(interest_form.errors)

     else:
            interest_form=InterestsForm()




       # Render the template depending on the context.
            return render_to_response('polls/dashboard.html',context_instance=RequestContext(request))

def login(request):
    if(request.method=="POST"):
        uname=request.POST.get('uname')
        pwd=request.POST.get('pwd')
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        print("cck"+uname)
        cursor.execute('''SELECT COUNT(*) FROM polls_userprofile where username=? AND password=?''',(uname,pwd,))
        conn.commit()
        c1=cursor.fetchone()
        ch1=c1[0]
        cursor.execute('''SELECT COUNT(*) FROM polls_userprofile where emailid=? AND password=?''',(uname,pwd,))
        conn.commit()
        c2=cursor.fetchone()
        ch2=c2[0]
        print("ckk"+str(ch1+ch2))
        if((ch1+ch2)!=0):
            if(ch2==1):
                cursor.execute('''SELECT username FROM polls_userprofile where emailid=? AND password=?''',(uname,pwd,))
                conn.commit()
                uname1=cursor.fetchone()
                request.session['uid']=uname1[0]
            else:
                request.session['uid']=uname
            response_dict={}
            response_dict.update({'flag':1})
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
        else:
            response_dict={}
            response_dict.update({'flag':0})
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    else:
        return render_to_response('polls/findex.htm',context_instance=RequestContext(request))

def dashboard1(request):
    if(request.session.has_key('uid')):
        username=request.session['uid']
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        cursor.execute('''SELECT firstname,dob,contact,college FROM polls_userprofile where username=?''',(username,))
        conn.commit()
        cur=cursor.fetchall()
        firstname=cur[0][0]
        dob=cur[0][1]
        contact=cur[0][2]
        college=cur[0][3]
        return render_to_response('polls/dashboard.html',{'username':username, 'name':firstname , 'dob':dob, 'contact':contact, 'college':college},context_instance=RequestContext(request))
    else:
        return HttpResponse("You are not logged in")

def selquiz(request):
    if(request.session.has_key('uid')):
        username=request.session['uid']
        utable=str(username)+"activity"
        print (utable)
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        curtime = time.strftime("%H:%M:%S", time.gmtime())
        curdate = time.strftime("%F", time.gmtime())
        cur="'"+str(curdate)+"T"+str(curtime)+"'"
        #cursor.execute('''SELECT quizname,date(endtime), time(endtime) FROM '''+utable+''' where status=? and time(starttime)<= '''+curtime+''' and time(endtime)>= '''+curtime+''' and date(starttime)<= '''+curdate+''' and date(endtime)>= '''+curdate,(username,))
        cursor.execute('''SELECT quizname,date(endtime), time(endtime) FROM '''+utable+''' where status=? and (strftime('%s', '''+cur+''') BETWEEN strftime('%s', starttime) AND strftime('%s', endtime))''',(0,))
        conn.commit()

        totalarr=cursor.fetchall()
        lim1=len(totalarr)
        print(totalarr[0][2])
        print("njkjb"+str(lim1))
        quizname1=['']*lim1
        enddate=['']*lim1
        endtime=['']*lim1

        for i in range(0,lim1):
            quizname1[i]=totalarr[i][0]
            enddate[i]=totalarr[i][1]
            endtime[i]=totalarr[i][2]

        cursor.execute('''SELECT quizname,date(starttime), time(starttime) FROM polls_quizglobal where (starttime)> ?  ''',(cur,))
        conn.commit()
        print("qwer"+str(quizname1))
        totalarr=cursor.fetchall()
        lim2=len(totalarr)
        print(cursor.fetchall())
        quizname2=['']*lim2
        startdate=['']*lim2
        starttime=['']*lim2
        for i in range(0,lim2):
            quizname2[i]=totalarr[i][0]
            startdate[i]=totalarr[i][1]
            starttime[i]=totalarr[i][2]


        return render_to_response('polls/select_quiz.html',{'username':username, 'quiz1': quizname1,'quiz2':quizname2, 'dates1':endtime, 'dates2':startdate, 'times2':starttime, 'n1':lim1, 'n2':lim2},context_instance=RequestContext(request))

    else:
        return HttpResponse("You are not logged in")

def quizgo(request,quizname):
    if(request.session.has_key('uid')):
        username=request.session['uid']
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        curtime = time.strftime("%H:%M:%S", time.gmtime())
        curdate = time.strftime("%F", time.gmtime())
        cur="'"+str(curdate)+"T"+str(curtime)+"'"
        utable=str(username)+"activity"
        cursor.execute('''SELECT COUNT(*) FROM '''+utable+''' where quizname =  ?''',(quizname,))
        conn.commit()
        chk=cursor.fetchone()[0]
        if(chk==0):
            return HttpResponse("You have not registered for this quiz")
        cursor.execute('''SELECT status FROM '''+utable+''' where quizname =  ?''',(quizname,))
        conn.commit()
        chk=cursor.fetchone()[0]
        if(chk==1):
            return HttpResponse("You have submitted your answers")
        cursor.execute('''SELECT COUNT(*) FROM '''+utable+''' where quizname =   ? ''',(quizname,))
        conn.commit()
        chk=cursor.fetchone()[0]
        if(chk==0):
            return HttpResponse("Quiz has not yet started")
        cursor.execute('''SELECT creator FROM polls_quizglobal where quizname= ? ''',(quizname,))
        conn.commit()
        chk=cursor.fetchone()[0]
        qtable="'"+quizname+str(chk)+"'"
        cursor.execute('''SELECT quesno,ques,opt1,opt2,opt3,opt4,opt5,opt6,opt7,opt8,opt9,opt10 FROM '''+qtable+''' where qtype = ? ''',("Single Correct",))
        conn.commit()
        quizarrs=cursor.fetchall()
        nsques=len(quizarrs)
        cursor.execute('''SELECT quesno,ques,opt1,opt2,opt3,opt4,opt5,opt6,opt7,opt8,opt9,opt10 FROM '''+qtable+''' where qtype = ? ''',("Multi Correct",))
        conn.commit()
        quizarrm=cursor.fetchall()
        nmques=len(quizarrm)

        quizarrs1=[[]]
        for i in range(0,nsques):
            for j in range(0,12):
                if(quizarrs[i][j]!=""):
                    quizarrs1[i].append(quizarrs[i][j])
            if(i!=nsques-1):
                quizarrs1.append([])
        quizarrm1=[[]]
        for i in range(0,nmques):
            for j in range(0,12):
                if(quizarrm[i][j]!=""):
                    quizarrm1[i].append(quizarrm[i][j])
            if(i!=nmques-1):
                quizarrm1.append([])
        #quizarr1=[[""]*12]*nques
        #quizarr11=[[""]*12]*nques



        #for i in range(0,nques):
            #quizarr[i][0]="a0"+str(quizarr[i][0])
        return render_to_response('polls/quiz.htm',{'username':username, 'quizname':quizname, 'qds':quizarrs1, 'qdm':quizarrm1, 'nsques':nsques, 'nmques': nmques},context_instance=RequestContext(request))

    else:
        return HttpResponse('you are not logged in.')

def ChangeDate(request):
    quizname=request.POST.get['quizname']
    starttime=request.POST.get['starttime']
    endtime=request.POST.get['endtime']
    conn=sqlite3.connect('db.sqlite3')
    cursor=conn.cursor()
    cursor.execute('''UPDATE polls_quizglobal SET starttime=?,endtime=? where quizname=?''',(starttime,endtime,quizname))
    conn.commit()
    trigger={1}     ##to trigger the alert box to remind that dates have been changed
    return HttpResponse(trigger)

def RegCheck(request,quizname):
    if(request.session.has_key('uid')):
        uname=request.session.get('uid')
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM '''+uname+'''activity where quizname=?''',(quizname,))
        conn.commit()
        cnt=(cursor.fetchone())[0]
        if(cnt==1):
            cursor.execute('''SELECT description,starttime,endtime,creator from polls_quizglobal where quizname=?''',(quizname,) )
            conn.commit()
            data1=cursor.fetchall()
            data=['']*4
            for i in range(0,4):
                data[i]=data1[i][0]
            desc=data[0]
            starttime=data[1]
            endtime=data[2]
            creator=data[3]
        #    desc=(cursor.fetchone())[0]
            flag=1       #don't show register button
            return render_to_response('polls/quiz_first.htm',{"quizname":quizname, "username":uname,"desciption":desc,"creator":creator,"starttime":starttime,"endtime":endtime,"flag":flag},context_instance=RequestContext(request))
        else:   ##render the user quiz registration page,not made yet
            cursor.execute('''SELECT description,starttime,endtime,creator from polls_quizglobal where quizname=?''',(quizname,) )
            conn.commit()
            data1=cursor.fetchall()
            data=['']*4
            for i in range(0,4):
                data[i]=data1[i][0]
            desc=data[0]
            starttime=data[1]
            endtime=data[2]
            creator=data[3]
        #    desc=(cursor.fetchone())[0]
            flag=0   ##show register button in form
            return render_to_response('polls/quiz_first.htm',{"quizname":quizname,"username":uname, "desciption":desc,"creator":creator,"starttime":starttime,"endtime":endtime,"flag":flag},context_instance=RequestContext(request))
    else:
        return HttpResponse('You are not logged in.')

def UserQuizReg(request,quizname):
    if(request.session.has_key('uid')):
        usernm=request.session.get('uid')
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
     #   conn=sqlite3.connect('db.sqlite3')
     #   cursor=conn.cursor()
        cursor.execute('''SELECT creator from polls_quizglobal where quizname=?''',(quizname))
        conn.commit()
        quizmaster=(cursor.fetchone())[0]
        cursor.execute('''SELECT COUNT(*) FROM '''+quizname+'''lboard''' )
        conn.commit()
        serial=(cursor.fetchone())[0]
        serial=serial+1
        cursor.execute('''INSERT INTO '''+quizname+quizmaster+'''lboard (sno,username,points) values=(?,?,?)''',(serial,usernm,0))
        conn.commit()
        cursor.execute('''INSERT INTO '''+usernm+'''activity (quizname,status,points) values=(?,?,?)''',(quizname,0,0))
        conn.commit()
        cursor.execute('''SELECT emailid from polls_userprofile where username=?''',(usernm))
        conn.commit()
        eid=(cursor.fetchone())[0]
        ####threading starts here
     #   Text='You have registered successfully for the quiz '+quizname
        thread1 = myThread1(eid,quizname)
        thread1.start()
        return HttpResponse('open alert box')
    else:
        return HttpResponse('you are not logged in.')

def QuizPlay(request,quizname):###here quizname refers to QUIZTABLENAME!!!!!!!!
    if(request.session.has_key('uid')):
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        cursor.execute('''SELECT creator from polls_quizglobal where quizname=?''',(quizname,))
        conn.commit()
        quizmaster=(cursor.fetchone())[0]
        if(not request.session.has_key(quizname+'starttime')):
            cursor.execute('''SELECT starttime,endtime FROM polls_quizglobal where quizname=?''',(quizname,))
            conn.commit()
            starttime=(cursor.fetchall())[0][0]
            endtime=(cursor.fetchall())[0][1]
            if(time.ctime(time.time())>=starttime and time.ctime(time.time())<=endtime):
                request.session[quizname+'starttime']=starttime
                request.session[quizname+'endtime']=endtime
                answer=request.POST.get['ans']
      #          cursor.execute('''SELECT creator from polls_quizglobal where quizname=?''',(quizname))
       #         quizmaster=(cursor.fetchone())[0]
                cursor.execute('''UPDATE '''+quizname+quizmaster+'''lboard set ansseq=? where username=?''',(answer,request.session.get('uid')))
                conn.commit()
                response_dict={}
                response_dict.update({'response':''})
                return HttpResponse(json.dumps(response_dict),content_type='application/javascript')
            else:
                response_dict={}
                response_dict.update({'response':'redirect'})
                return HttpResponse(json.dumps(response_dict),content_type='application/javascript')
        else:
            starttime=request.session.get(quizname+'starttime')
            endtime=request.session.get(quizname+'endtime')
            if(time.ctime(time.time())>=starttime&time.ctime(time.time())<=endtime):
                answer=request.POST.get['ans']
                conn=sqlite3.connect('db.sqlite3')
                cursor=conn.cursor()
                cursor.execute('''UPDATE '''+quizname+quizmaster+'''lboard set ansseq=? where username=?''',(answer,request.session.get('uid')))
                conn.commit()
                response_dict={}
                response_dict.update({'response':''})
                return HttpResponse(json.dumps(response_dict),content_type='application/javascript')
    else:
        return HttpResponse('you are not logged in.')


def func1(request):
  #conn=sqlite3.connect('db.sqlite3')
  #cursor=conn.cursor()
  #cursor.execute('''UPDATE polls_userprofile set interest1=? where emailid=?''',(intrchk(1),'vsandstorm0@gmail.com',))
  #conn.commit()
  return render_to_response('polls/quiz_first.htm',context_instance=RequestContext(request))

def QuizReg(request):
    quizregform=QuizRegForm()
    return render_to_response('polls/QuizReg.html',{'quizregform':quizregform},context_instance=RequestContext(request))

def EditOrCreate(request):
        loginid=request.POST['loginid']
        passwd=request.POST['passwd']
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        cursor.execute('''SELECT passwd from polls_quizreg where loginid=?''',(loginid,))
        passwd2=cursor.fetchone()
        passwd1=passwd2[0]
        print(passwd1)
        conn.commit()
        if(str(passwd1)==str(passwd)):
            request.session['quizmaster']=request.POST['loginid']
            cursor=conn.cursor()
            cursor.execute('''SELECT quizname from polls_quizglobal where creator=?''',(request.session['quizmaster'],))
            quiznamearray1=cursor.fetchall()
            conn.commit()
            cursor.execute('''SELECT COUNT (*) from polls_quizglobal where creator=?''',(request.session['quizmaster'],))
            asize=cursor.fetchone()
            quiznamearray=['']*asize[0]
            for i in range(0,asize[0]):
                quiznamearray[i]=quiznamearray1[i][0]
                print(quiznamearray[i]+" ")
            return render_to_response('polls/EditOrCreate.htm',{'quiznamearray':quiznamearray,'asize':asize[0],'loginid':request.session['quizmaster']},context_instance=RequestContext(request))
        else:
            return HttpResponse("passwords don't match")





def test(request):

    return render_to_response('polls/quizm.htm',context_instance=RequestContext(request))

def CreateQuiz(request):
    conn=sqlite3.connect('db.sqlite3')
    cursor=conn.cursor()
    quiztablename=request.POST['QuizTitle']
    starttime=request.POST['starttime']
    endtime=request.POST['endtime']


    cursor.execute('''CREATE TABLE '''+quiztablename+request.session.get('quizmaster')+''' (
    quesno INTEGER PRIMARY KEY AUTOINCREMENT,
    ques TEXT NOT NULL,
    qtype TEXT NOT NULL,
    options INTEGER NOT NULL,
    opt1 TEXT NOT NULL,
    opt2 TEXT NOT NULL,
    opt3 TEXT NOT NULL,
    opt4 TEXT NOT NULL,
    opt5 TEXT NOT NULL,
    opt6 TEXT NOT NULL,
    opt7 TEXT NOT NULL,
    opt8 TEXT NOT NULL,
    opt9 TEXT NOT NULL,
    opt10 TEXT NOT NULL,
    ans TEXT NOT NULL
    )''')
    conn.commit()
    cursor.execute('''CREATE TABLE '''+quiztablename+request.session.get('quizmaster')+'''lboard (
    sno INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    points INTEGER ,
    ustarttime TIME ,
    uendtime TIME ,
    duration TIME,
    ansseq TEXT

    )''')
    conn.commit()
    cursor.execute('''INSERT into polls_quizglobal (creator,quizname,starttime,endtime) values(?,?,?,?)''',(request.session.get('quizmaster'),quiztablename,starttime,endtime))
    conn.commit()
    #cursor.execute('''SELECT time(endtime),time(starttime) from polls_quizglobal where quizname= ?''',(quiztablename,))
    #conn.commit()
    #wer=((cursor.fetchall()[0]))

    return render_to_response("polls/quizm.htm",{'quizname':quiztablename},context_instance=RequestContext(request))

def quizuptab(request,quizname):
    if(request.method=='POST'):
        ques=request.POST['ques']
        options=request.POST['nq']
        qno=request.POST['qid']
        qtype=request.POST['type']
        opt1=request.POST['o1']
        opt2=request.POST['o2']
        opt3=request.POST['o3']
        opt4=request.POST['o4']
        opt5=request.POST['o5']
        opt6=request.POST['o6']
        opt7=request.POST['o7']
        opt8=request.POST['o8']
        opt9=request.POST['o9']
        opt10=request.POST['o10']
        c1=request.POST.get('c1',0)
        c2=request.POST.get('c2',0)
        c3=request.POST.get('c3',0)
        c4=request.POST.get('c4',0)
        c5=request.POST.get('c5',0)
        c6=request.POST.get('c6',0)
        c7=request.POST.get('c7',0)
        c8=request.POST.get('c8',0)
        c9=request.POST.get('c9',0)
        c10=request.POST.get('c10',0)
        if(c1!=0):
            c1='1'
        if(c2!=0):
            c2='1'
        if(c3!=0):
            c3='1'
        if(c4!=0):
            c4='1'
        if(c5!=0):
            c5='1'
        if(c6!=0):
            c6='1'
        if(c7!=0):
            c7='1'
        if(c8!=0):
            c8='1'
        if(c9!=0):
            c9='1'
        if(c10!=0):
            c10='1'
        ans=str(c1)+str(c2)+str(c3)+str(c4)+str(c5)+str(c6)+str(c7)+str(c8)+str(c9)+str(c10)
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        print("chala")
        quiztablename=quizname+request.session.get('quizmaster')
        if(qno=="0"):
            cursor.execute('''INSERT INTO '''+ quiztablename+''' (ques,qtype,options,opt1,opt2,opt3,opt4,opt5,opt6,opt7,opt8,opt9,opt10,ans) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(ques,qtype,options,opt1,opt2,opt3,opt4,opt5,opt6,opt7,opt8,opt9,opt10,ans))
            conn.commit()
        else:
            cursor.execute('''UPDATE'''+ quiztablename+''' SET ques=?, qtype=?, options=?, opt1=?, opt2=?, opt3=?, opt4=?, opt5=?, opt6=?, opt7=?, opt8=?, opt9=?, opt10=?, ans=? where quesno=?  ''',(ques,qtype,options,opt1,opt2,opt3,opt4,opt5,opt6,opt7,opt8,opt9,opt10,ans,qno))
            conn.commit()
        print(quiztablename+" "+quizname+" "+request.session.get('quizmaster'))
        cursor.execute('''Select ques from '''+ quiztablename)
        conn.commit()
        qarray=cursor.fetchall()

        tabname=quiztablename
        cursor.execute(" Select Count (*) from "+tabname)
        conn.commit()
        up=cursor.fetchone()
        i=[0]*up[0]
        arrayq=[""]*(up[0]+1)
        print(up[0])
        for k in range(0,up[0]):
            arrayq[k]=qarray[k][0]
            i[k]=k
        return render_to_response('polls/quizm.htm',{"qarray":arrayq,"quizname":quizname,"limits":i,"up":up[0]},context_instance=RequestContext(request))
        #return HttpResponse("Baad diya")


    else:
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        quiztablename=quizname+request.session.get('quizmaster')
        print(quiztablename+" "+quizname+" "+request.session.get('quizmaster'))
        cursor.execute('''Select ques from '''+ quiztablename )
        conn.commit()
        qarray=cursor.fetchall()
        tabname=quiztablename
        cursor.execute(" Select Count (*) from "+tabname)
        conn.commit()
        up=cursor.fetchone()
        i=[0]*up[0]
        arrayq=[""]*(up[0]+1)
        #print(up[0])
        for k in range(0,up[0]):
            arrayq[k]=qarray[k][0]
            i[k]=k
        #print(arrayq[1][0])
        return render_to_response('polls/quizm.htm',{"qarray":arrayq,"quizname":quizname,"limits":i,"up":up[0]},context_instance=RequestContext(request))
        #return render_to_response('polls/quizm.htm',context_instance=RequestContext(request))


def editq(request,quizname):
    if(request.method=="POST"):
        pry=request.POST.get("qid")
        pry1=pry[1:]
        pry2=int(pry1)+1
        print(pry2)
        conn=sqlite3.connect('db.sqlite3')
        cursor=conn.cursor()
        quiztablename=quizname+request.session.get('quizmaster')
        cursor.execute('''Select ques from '''+quiztablename+''' where quesno = ?''',(pry2,) )
        conn.commit()
        quesa=cursor.fetchone()
        ques=quesa[0]
        option=[""]*11
        cursor.execute('''Select opt1,opt2,opt3,opt4,opt5,opt6,opt7,opt8,opt9,opt10,qtype from '''+quiztablename+''' where quesno = ?''',(pry2,) )
        conn.commit()
        clap=cursor.fetchall()
        qtype=clap[0][10]
        print(clap[0][1])
        for i in range(1,11):
            option[i]=clap[0][i-1]
        cursor.execute('''Select options from '''+quiztablename+''' where quesno = ?''',(pry2,) )
        conn.commit()
        print(option)
        noptionsa=cursor.fetchone()
        noptions=noptionsa[0]
        cursor.execute('''Select ans from '''+quiztablename+''' where quesno = ?''',(pry2,) )
        conn.commit()
        ansa=cursor.fetchone()
        ans=ansa[0]
        print(ans)
        response_dict={}
    #response_dict.update({'ques':ques,'id':pry2, 'noptions':noptions, 'ans':ans,'opt1': option[1], 'opt2': option[2], 'opt3': option[3], 'opt4': option[4], 'opt5': option[5], 'opt6': option[6], 'opt7': option[7], 'opt8': option[8], 'opt9': option[9], 'opt10': option[10], })
        response_dict.update({'ques':ques,'id':pry2, 'type':qtype, 'noptions':noptions, 'ans':ans, 'option': option})
        return HttpResponse(json.dumps(response_dict),content_type='application/javascript')

def delq(request,quizname):
    if(request.method=="POST"):
        pry=request.POST.get("qid")
        pry1=pry[1:]
        pry2=int(pry1)+1
        print("yuio"+str(pry2))
        conn=sqlite3.connect('db.sqlite3')
        quiztablename=quizname+request.session.get('quizmaster')
        cursor=conn.cursor()
        cursor.execute('''DELETE FROM '''+quiztablename+''' WHERE quesno = ? ''',(pry2,))
        conn.commit()
        cursor.execute(" Select Count (*) from" + quiztablename )
        conn.commit()
        row=cursor.fetchone()
        for i in range(1,row[0]-pry2+3):
            cursor.execute('''UPDATE '''+quiztablename+''' SET quesno=? WHERE quesno = ?''',(pry2+i-1,pry2+i,))
            conn.commit()
        response_dict={}
        response_dict.update({'chk':1})
        request.method=""

        return HttpResponse(json.dumps(response_dict),content_type='application/javascript')

def delref(request,quizname):
    conn=sqlite3.connect('db.sqlite3')
    cursor=conn.cursor()
    quiztablename=quizname+request.session.get('quizmaster')
    print(quiztablename+" "+quizname+" "+request.session.get('quizmaster'))
    cursor.execute('''Select ques from '''+ quiztablename )
    conn.commit()
    qarray=cursor.fetchall()
    tabname=quiztablename
    cursor.execute(" Select Count (*) from "+tabname)
    conn.commit()
    up=cursor.fetchone()
    i=[0]*up[0]
    arrayq=[""]*(up[0]+1)
    #print(up[0])
    for k in range(0,up[0]):
        arrayq[k]=qarray[k][0]
        i[k]=k
    #print(arrayq[1][0])
    return render_to_response('polls/quizm.htm',{"qarray":arrayq,"quizname":quizname,"limits":i,"up":up[0]},context_instance=RequestContext(request))













