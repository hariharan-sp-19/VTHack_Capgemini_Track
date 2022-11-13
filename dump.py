import shutil, os
import random, csv
import os, matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.patches import Shadow
from os.path import basename
import numpy as np

##############################################################################
##                            HELPER FUNCTIONS                              ##
##############################################################################

# create a pdf 
def calculate_footprint(answers):
    # create carbon calculator 

    # initialize answers 
    answer_1 = answers[0]
    answer_2 = answers[1]
    answer_3 = answers[2]
    answer_4 = answers[3]
    answer_5 = answers[4]
    answer_6 = answers[5]
    answer_7 = answers[6]
    answer_8 = answers[7]
    answer_9 = answers[8]
    answer_10 = answers[9]
    answer_11 = answers[10]

    # Electric bill = 7,252.76 kg CO2/year 
    # $0.1327/kwh/0.62 kg CO2/kwh = $0.214/kg CO2  - all we need to do is divide montly bill by this.
    # electric bill = (electric bill / people in household) / ($0.214/kgCo2)     
    
    try:
        answer_1=answer_1.replace('$','')
        electric_=(int(answer_2)/int(answer_1))*12/0.214
    except:
        print('--> error on electric CO2 calculation')

    # Flights = 602.448 kg CO2/year (if yes)
    # 286.88 kg CO2/flight 
    try:
        flight_= float(answer_3)*286.88 
    except:
        print('--> error on flight CO2 calculation')
        flight_=602.448

    # Transportation = 0.
    # 6,525.0 kg CO2/year (if drive only), 4,470.0 kg CO2/year (if mixed), 2,415.0 kg/year (if public)
    # 0.435 kg CO2/mile driving, 0.298 kg CO2/mile 50%/50% public transport and driving, and 0.161 kg CO2/mile (if public)
    # assume 220 working days/year (w/ vacation)
    try:
        transportation_=0
        if answer_4 == 'yes' and answer_6 == 'no':
            transportation_=float(answer_5)*1.61* 0.435*2*220

        elif answer_4 == 'yes' and answer_6 == 'yes':
            transportation_=float(answer_5)*1.61*0.298*2*220

        elif answer_4 == 'no' and answer_6 == 'yes':
            transportation_=float(answer_5)*1.61*0.161*2*220
        # Uber trips 
        # 45.27 kg CO2/year (average) 
        # 6 miles * 0.435 kg Co2/ mile = 2.61 kg CO2/trip 
        transportation_=transportation_+float(answer_8)*2.61*12

    except:
        print('--> error on transportation CO2 caclulation')
        # print(answer_4,answer_6,answer_8, answer_5)
        # transportation_=201.11
        transportation=4515.27

    # Vegetarian - assume footprint from food 
    try:
        if answer_9 == 'yes':
            food_=1542.21406
        # meat lover 
        elif answer_10 == 'yes':
            food_=2993.70964
        else:
            food_=2267.96185
    except:
        print('--> error on food CO2 calculation')
        food_=2267.96185

    # do you use amazon? --> retail, etc. 
    answer_11=answer_11.replace('$','').replace(' ','')
    retail_=0.1289*float(answer_11)

    footprint=electric_+flight_+transportation_+food_+retail_
    footprintbytype=[electric_, flight_, transportation_, food_, retail_]

    # compared to averages (kg Co2/year)
    footprint_avg = 14660.85
    footprintbytype_avg = [7252.76, 602.45, 4515.27, 2267.96, 22.41]

    footprint_delta=footprint-footprint_avg
    footprintbytype_delta=list(np.array(footprintbytype)-np.array(footprintbytype_avg))

    labels_footprint=['electric (kg Co2/year)', 'flight (kg Co2/year)', 'transportation (kg Co2/year)', 'food (kg Co2/year)', 'retail (kg Co2/year)']
    labels_footprintbytype = 'total kg Co2/year'

    return footprint, footprintbytype, footprint_delta, footprintbytype_delta, labels_footprint, labels_footprintbytype



def make_graphs(individual_means, individual_means_2):

    # bar graph compared to average in each category (2 phase bar graph)
    labels = ['Electricity consumption (kwh * 1000)', '# of flights per year', '# commute miles per year (thousands)', '# of uber trips per year', 'food choice (tons of CO2 emissions/year)']
    population_means = [11.698, 2.1, 15, 7.86, 2.5]
    population_means=list(map(int,population_means))

    print(labels)
    print(individual_means)
    print(population_means)

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, individual_means, width, label='Your score', color='#5dcf60')
    rects2 = ax.bar(x + width/2, population_means, width, label='Average score', color='#595959')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Scores')
    ax.set_title('Scores by label')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation='vertical') #rotation='vertical', fontsize='x-small',
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')


    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    # plt.show()
    plt.savefig('bar.png', format="png")


    # bar 2 
    labels = ['electricity', 'flights', 'transportation', 'food', 'retail']
    population_means = [7252.76, 602.45, 4515.27, 2267.96, 22.41]
    population_means=list(map(int,population_means))
    individual_means_2=list(map(int, individual_means_2))

    print(labels)
    print(individual_means_2)
    print(population_means)

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, individual_means_2, width, label='Your score', color='#5dcf60')
    rects2 = ax.bar(x + width/2, population_means, width, label='Average score', color='#595959')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('kg Co2/year')
    ax.set_title('Scores by label')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation='vertical') #rotation='vertical', fontsize='x-small',
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')


    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    # plt.show()
    plt.savefig('bar_2.png', format="png")

    # % of contributions to your carbon footpint
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    labels = ['electricitiy', 'flights', 'transport', 'food', 'retail']
    fracs = [individual_means_2[0], individual_means_2[1], individual_means_2[2], individual_means_2[3], individual_means_2[4]]
    colors = ['#5dcf60', '#999999', '#A4efa4', '#595959', '#c3dbc3', '#70b170']
    explode = (0, 0, 0, 0, 0)
    pies = ax.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', colors=colors)

    for w in pies[0]:
        # set the id with the label.
        w.set_gid(w.get_label())

        # we don't want to draw the edge of the pie
        w.set_edgecolor("none")

    for w in pies[0]:
        # create shadow patch
        s = Shadow(w, -0.01, -0.01)
        s.set_gid(w.get_gid() + "_shadow")
        s.set_zorder(w.get_zorder() - 0.1)
        ax.add_patch(s)

    # save
    plt.savefig('pi.png', format="png")

def clean_answer(answer):
    answer=answer.replace(' ','').replace('$','')

    if answer == 'y':
        answer='yes'
    elif answer == 'n':
        answer='no'
    # this is for intent querying 
    return answer

##############################################################################
##                            MAIN SCRIPT                                   ##
##############################################################################
masterlist=[]
for i in range(0,112345):
    email = "emailid"+str(i)
    answer_1 = clean_answer(str(random.randint(1,5)))
    answer_2 = clean_answer(str(random.randint(30,300)))
    answer_3 = clean_answer(str(random.randint(1,15)))
    answer_4 = random.randint(0,1)
    if answer_4==0:
        answer_4 = clean_answer("y")
    else:
        answer_4 = clean_answer("n")
    
    answer_5 = clean_answer(str(random.randint(5,50)))
    answer_6 = random.randint(0,1)
    if answer_6==0:
        answer_6 = clean_answer("y")
    else:
        answer_6 = clean_answer("n")
    answer_7 = random.randint(0,1)
    if answer_7==0:
        answer_7 = clean_answer("y")
        answer_8 = clean_answer(str(random.randint(1,20)))
    else:
        answer_7 = clean_answer("n")
        answer_8=clean_answer(str(0))
    answer_9 = random.randint(0,1)
    if answer_9==0:
        answer_9 = clean_answer("y")
    else:
        answer_9 = clean_answer("n")
    answer_10 = random.randint(0,1)
    if answer_10==0:
        answer_10 = clean_answer("y")
    else:
        answer_10 = clean_answer("n")
    answer_11 = clean_answer(str(random.randint(0,300)))
    answers=[answer_1, answer_2, answer_3, answer_4, answer_5,
         answer_6, answer_7, answer_8, answer_9, answer_10, answer_11]
    footprint, footprintbytype, footprint_delta, footprintbytype_delta, labels_footprint, labels_footprintbytype =calculate_footprint(answers)
    list_ = []
    list_.append(email)
    list_.extend(answers)
    list_.extend(footprintbytype)
    list_.extend(labels_footprint)
    masterlist.append(list_)

with open("out.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(masterlist)


# email=input('what is your email? \n')
# answer_1 = input('How many people are in your household? (e.g. 2) \n')
# answer_1=clean_answer(answer_1)
# answer_2 = input('What is your electric bill (in dollars) monthly?  (e.g. 50) \n')
# answer_2=clean_answer(answer_2)
# answer_3 = input('How many flights do you take per year? (e.g. 10) \n')
# answer_3=clean_answer(answer_3)
# answer_4 = input('Do you own a car? (e.g. n | y) \n')
# answer_4=clean_answer(answer_4)
# answer_5 = input('What is your average distance to commute to/from work in miles - for example 21? (e.g. 10) \n')
# answer_5=clean_answer(answer_5)
# answer_6= input('Do you use public transportation? (e.g. y)\n')
# answer_6=clean_answer(answer_6)
# answer_7 = input('Do you use uber or another ride sharing platform like Lyft? (e.g. y) \n')
# answer_7=clean_answer(answer_7)
# if answer_7 == 'yes':
#     answer_8 = input("How many ride-sharing trips do you complete per month? (e.g. 10) \n")
#     answer_8=clean_answer(answer_8)
# else:
#     answer_8 = '0'
# answer_9 = input('Are you a vegetarian? (e.g. n) \n')
# answer_9=clean_answer(answer_9)
# answer_10= input('Do you eat meat more than 3 times each week? (e.g. y) \n')
# answer_10=clean_answer(answer_10)
# answer_11 = input('How much money do you spend on Amazon per month in US dollars - for example, fifty dollars? (e.g. 150) \n')
# answer_11=clean_answer(answer_11)

# answers=[answer_1, answer_2, answer_3, answer_4, answer_5,
#          answer_6, answer_7, answer_8, answer_9, answer_10, answer_11]

# ## report on recommendations pop up + saved in directory
# footprint, footprintbytype, footprint_delta, footprintbytype_delta, labels_footprint, labels_footprintbytype =calculate_footprint(answers)

# data = {'email': email,
#         #'questions': questions,
#         'answers': answers,
#         'footprint': footprint,
#         'footprintbytype': footprintbytype,
#         'footprint_delta': footprint_delta,
#         'footprintbytype_delta': footprintbytype_delta,
#         'labels_footprint': labels_footprint,
#         'labels_footprintbytype': labels_footprintbytype}

# print(data)

# curdir=os.getcwd()
# os.chdir(curdir)

# tempdir='tempdir'
# try:
#     os.mkdir(tempdir)
#     os.chdir(tempdir)
# except:
#     shutil.rmtree(tempdir)
#     os.mkdir(tempdir)
#     os.chdir(tempdir)

# if answer_4 == 'yes' and answer_6 == 'no':
#     individual_means = [(int(answer_2)/0.1327)*12/1000, int(answer_3), int(answer_5)*220*2/1000, int(answer_8)*12, footprintbytype[3]/1000]
# elif answer_4 == 'yes' and answer_6 == 'yes':
#     individual_means = [(int(answer_2)/0.1327)*12/1000, int(answer_3), int(answer_5)*220*2/1000, int(answer_8)*12,  footprintbytype[3]/1000]
# elif answer_4 == 'no' and answer_6 == 'yes':
#     individual_means = [(int(answer_2)/0.1327)*12/1000, int(answer_3), int(answer_5)*220*2/1000, int(answer_8)*12, footprintbytype[3]/1000]
# else:
#     individual_means = [(int(answer_2)/0.1327)*12/1000, int(answer_3), 0, int(answer_8)*12, footprintbytype[3]/1000]

# individual_means=list(map(int,individual_means))

# truthlist=[False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
# make_graphs(individual_means, footprintbytype)
