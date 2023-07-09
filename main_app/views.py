from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import date
from sklearn.naive_bayes import MultinomialNB
from django.contrib import messages
from django.contrib.auth.models import User , auth
from .models import patient , doctor , diseaseinfo , consultation ,rating_review
from chats.models import Chat,Feedback

# Create your views here.


#loading trained_model
import joblib as jb
model = jb.load('model.joblib')




def home(request):

  if request.method == 'GET':
        
      if request.user.is_authenticated:
        return render(request,'homepage/index.html')

      else :
        return render(request,'homepage/index.html')



   

       


def admin_ui(request):

    if request.method == 'GET':

      if request.user.is_authenticated:

        auser = request.user
        Feedbackobj = Feedback.objects.all()

        return render(request,'admin/admin_ui/admin_ui.html' , {"auser":auser,"Feedback":Feedbackobj})

      else :
        return redirect('home')



    if request.method == 'POST':

       return render(request,'patient/patient_ui/profile.html')





def patient_ui(request):

    if request.method == 'GET':

      if request.user.is_authenticated:

        patientusername = request.session['patientusername']
        puser = User.objects.get(username=patientusername)

        return render(request,'patient/patient_ui/profile.html' , {"puser":puser})

      else :
        return redirect('home')



    if request.method == 'POST':

       return render(request,'patient/patient_ui/profile.html')

       


def pviewprofile(request, patientusername):

    if request.method == 'GET':

          puser = User.objects.get(username=patientusername)

          return render(request,'patient/view_profile/view_profile.html', {"puser":puser})




def checkdisease(request):

  diseaselist=['Chikungunya', 'Dengue', 'Rift Valley fever', 'Yellow Fever', 'Zika', 'Malaria', 'Japanese encephalitis', 'West Nile fever',
               'Plague', 'Tungiasis', 'Lyme disease']


  symptomslist=['sudden_fever','headache','mouth_bleed','nose_bleed','muscle_pain','joint_pain','vomiting','rash',
                'diarrhea','hypotension','pleural_effusion','ascites','gastro_bleeding','swelling','nausea','chills',
                'myalgia','digestion_trouble','fatigue','skin_lesions','stomach_pain','orbital_pain','neck_pain','weakness',
                'back_pain','weight_loss','gum_bleed','jaundice','coma','diziness','inflammation','red_eyes','loss_of_appetite',
                'urination_loss','slow_heart_rate','abdominal_pain','light_sensitivity','yellow_skin','yellow_eyes','facial_distortion',
                'microcephaly','rigor','bitter_tongue','convulsion','anemia','cocacola_urine','hypoglycemia','prostraction','hyperpyrexia',
                'stiff_neck','irritability','confusion','tremor','paralysis','lymph_swells','breathing_restriction','toe_inflammation',
                'finger_inflammation','lips_irritation','itchiness','ulcers','toenail_loss','speech_problem','bullseye_rash']

  alphabaticsymptomslist = sorted(symptomslist)

  


  if request.method == 'GET':
    
     return render(request,'patient/checkdisease/checkdisease.html', {"list2":alphabaticsymptomslist})




  elif request.method == 'POST':
       
      ## access you data by playing around with the request.POST object
      
      inputno = int(request.POST["noofsym"])
      print(inputno)
      if (inputno == 0 ) :
          return JsonResponse({'predicteddisease': "none",'confidencescore': 0 })
  
      else :

        psymptoms = []
        psymptoms = request.POST.getlist("symptoms[]")
       
        print(psymptoms)

      
        """      #main code start from here...
        """
      testingsymptoms = [0] * len(symptomslist)
      for i in range(len(symptomslist)):
         if symptomslist[i] in psymptoms:
           testingsymptoms[i] = 1

         inputtest = [testingsymptoms]
         print(inputtest)


      

      

      predicted = model.predict(inputtest)
      print("predicted disease is : ")
      print(predicted)

      y_pred_2 = model.predict_proba(inputtest)
      confidencescore=y_pred_2.max() * 100
      print(" confidence score of : = {0} ".format(confidencescore))

      confidencescore = format(confidencescore, '.0f')
      predicted_disease = predicted[0]

        

        #consult_doctor codes----------

      Allergist_Immunologist = ['Chikungunya', 'Dengue', 'Rift Valley fever', 'Yellow Fever', 'Zika', 'Malaria', 'Japanese encephalitis', 'West Nile fever',
               'Plague', 'Tungiasis', 'Lyme disease']

     
      if predicted_disease in Allergist_Immunologist :
           consultdoctor = "Allergist/Immunologist"
     
      else :
           consultdoctor = "other"


      request.session['doctortype'] = consultdoctor 

      patientusername = request.session['patientusername']
      puser = User.objects.get(username=patientusername)
     

        #saving to database.....................

      patient = puser.patient
      diseasename = predicted_disease
      no_of_symp = inputno
      symptomsname = psymptoms
      confidence = confidencescore

      diseaseinfo_new = diseaseinfo(patient=patient,diseasename=diseasename,no_of_symp=no_of_symp,symptomsname=symptomsname,confidence=confidence,consultdoctor=consultdoctor)
      diseaseinfo_new.save()
        

      request.session['diseaseinfo_id'] = diseaseinfo_new.id

      print("disease record saved sucessfully.............................")

      return JsonResponse({'predicteddisease': predicted_disease ,'confidencescore':confidencescore , "consultdoctor": consultdoctor})
   


   
    



   





def pconsultation_history(request):

    if request.method == 'GET':  

      patientusername = request.session['patientusername']
      puser = User.objects.get(username=patientusername)
      patient_obj = puser.patient
        
      consultationnew = consultation.objects.filter(patient = patient_obj)
      
    
      return render(request,'patient/consultation_history/consultation_history.html',{"consultation":consultationnew})


def dconsultation_history(request):

    if request.method == 'GET':

      doctorusername = request.session['doctorusername']
      duser = User.objects.get(username=doctorusername)
      doctor_obj = duser.doctor
        
      consultationnew = consultation.objects.filter(doctor = doctor_obj)
      
    
      return render(request,'doctor/consultation_history/consultation_history.html',{"consultation":consultationnew})



def doctor_ui(request):

    if request.method == 'GET':

      doctorid = request.session['doctorusername']
      duser = User.objects.get(username=doctorid)

    
      return render(request,'doctor/doctor_ui/profile.html',{"duser":duser})



      


def dviewprofile(request, doctorusername):

    if request.method == 'GET':

         
         duser = User.objects.get(username=doctorusername)
         r = rating_review.objects.filter(doctor=duser.doctor)
       
         return render(request,'doctor/view_profile/view_profile.html', {"duser":duser, "rate":r} )








       
def  consult_a_doctor(request):


    if request.method == 'GET':

        
        doctortype = request.session['doctortype']
        print(doctortype)
        dobj = doctor.objects.all()
        #dobj = doctor.objects.filter(specialization=doctortype)


        return render(request,'patient/consult_a_doctor/consult_a_doctor.html',{"dobj":dobj})

   


def  make_consultation(request, doctorusername):

    if request.method == 'POST':
       

        patientusername = request.session['patientusername']
        puser = User.objects.get(username=patientusername)
        patient_obj = puser.patient
        
        
        #doctorusername = request.session['doctorusername']
        duser = User.objects.get(username=doctorusername)
        doctor_obj = duser.doctor
        request.session['doctorusername'] = doctorusername


        diseaseinfo_id = request.session['diseaseinfo_id']
        diseaseinfo_obj = diseaseinfo.objects.get(id=diseaseinfo_id)

        consultation_date = date.today()
        status = "active"
        
        consultation_new = consultation( patient=patient_obj, doctor=doctor_obj, diseaseinfo=diseaseinfo_obj, consultation_date=consultation_date,status=status)
        consultation_new.save()

        request.session['consultation_id'] = consultation_new.id

        print("consultation record is saved sucessfully.............................")

         
        return redirect('consultationview',consultation_new.id)



def  consultationview(request,consultation_id):
   
    if request.method == 'GET':

   
      request.session['consultation_id'] = consultation_id
      consultation_obj = consultation.objects.get(id=consultation_id)

      return render(request,'consultation/consultation.html', {"consultation":consultation_obj })

   #  if request.method == 'POST':
   #    return render(request,'consultation/consultation.html' )





def rate_review(request,consultation_id):
   if request.method == "POST":
         
         consultation_obj = consultation.objects.get(id=consultation_id)
         patient = consultation_obj.patient
         doctor1 = consultation_obj.doctor
         rating = request.POST.get('rating')
         review = request.POST.get('review')

         rating_obj = rating_review(patient=patient,doctor=doctor1,rating=rating,review=review)
         rating_obj.save()

         rate = int(rating_obj.rating_is)
         doctor.objects.filter(pk=doctor1).update(rating=rate)
         

         return redirect('consultationview',consultation_id)





def close_consultation(request,consultation_id):
   if request.method == "POST":
         
         consultation.objects.filter(pk=consultation_id).update(status="closed")
         
         return redirect('home')






#-----------------------------chatting system ---------------------------------------------------


def post(request):
    if request.method == "POST":
        msg = request.POST.get('msgbox', None)

        consultation_id = request.session['consultation_id'] 
        consultation_obj = consultation.objects.get(id=consultation_id)

        c = Chat(consultation_id=consultation_obj,sender=request.user, message=msg)

        #msg = c.user.username+": "+msg

        if msg != '':            
            c.save()
            print("msg saved"+ msg )
            return JsonResponse({ 'msg': msg })
    else:
        return HttpResponse('Request must be POST.')



def chat_messages(request):
   if request.method == "GET":

         consultation_id = request.session['consultation_id'] 

         c = Chat.objects.filter(consultation_id=consultation_id)
         return render(request, 'consultation/chat_body.html', {'chat': c})


#-----------------------------chatting system ---------------------------------------------------


