import os
from flask import Flask, render_template, request, redirect, Response, jsonify
from dotenv import load_dotenv
from peewee import *
from playhouse.shortcuts import model_to_dict
import datetime
import folium
from retry import retry


load_dotenv('./example.env')

@retry(OperationalError, tries=10, delay=2)
def connect_to_database():
    db = MySQLDatabase(
        os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306,
    )
    db.connect()
    return db

app = Flask(__name__)

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase('file:memory?mode=memory&cache=shared', uri=True)
else:
    mydb = connect_to_database()
    


class CustomDateTimeField(DateTimeField):
    def python_value(self, value):
        return value

    def db_value(self, value):
        if isinstance(value, str):
            value = datetime.datetime.strptime(value, '%a, %d %b %Y %H:%M:%S %Z')
        return value

    def __get__(self, instance, owner):
        value = super(CustomDateTimeField, self).__get__(instance, owner)
        if isinstance(value, datetime.datetime):
            value = value.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return value


class TimelinePost(Model):
    name=CharField()
    email=CharField()
    content=TextField()
    created_on=DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = mydb


mydb.create_tables([TimelinePost])

projectImageDir = os.path.join('img')
img = os.path.join('static', 'img')

# Landing page data
landing_data = [
    {
        "name": "Reginald Amedee",
        "img": "./static/img/reginald.jpeg",
        "marker_color": "green",
        "style": "pin1",
        "places": [
            {
                "coord": [43.6532, -79.3832],
                "name": "Toronto"
            },
            {
                "coord": [37.4415, 25.3667],
                "name": "Mykonos"
            },
            {
                "coord": [23.1136, -82.3666],
                "name": "Cuba"
            },
            {
                "coord": [10.6918, -61.2225],
                "name": "Trinidad"
            },
            {
                "coord": [36.3932, 25.4615],
                "name": "Santorini"
            },
            {
                "coord": [64.9631, -19.0208],
                "name": "Iceland"
            },
            {
                "coord": [18.1096, 77.2975],
                "name": "Jamaica"
            }
        ],
    }
]

def build_map():
    my_map = folium.Map()

    # Add markers for each person
    for person in landing_data:
        for p in person["places"]:
            folium.Marker(p["coord"], popup = p["name"], icon=folium.Icon(color=person["marker_color"], icon="circle", prefix="fa")).add_to(my_map)

    my_map = my_map._repr_html_()
    return my_map

pic_data = {
"Reginald Amedee": "./static/img/reginald.jpeg"
}


about_me= {
    "Reginald Amedee": """Hi, My name is Reginald and I am a developer based out 
    of New York City. I have three years of Account Management/Customer Success experience in technology. 
    I've always wanted to be an engineer and made the courageous decision to quit my job last year to pursue this passion full time! 
    I have experience with a variety of technologies and I love to build things. Always looking to collaborate!""",
}

@app.route('/')
def index():
    my_map = build_map()
    intro_message = "Welcome to my page! Click on my name to learn more about me!"
    map_title = "A map of all the places that we have been to:"
    map_desc = "Reginald (Green), Eyob (Red), Cassey (Blue)"
    return render_template('index.html', title="MLH Fellow", url=os.getenv("URL"), landing_data=landing_data, intro_message=intro_message, my_map=my_map, map_title=map_title, map_desc=map_desc)

@app.route('/<fellow>')
def fellowPage(fellow):
    full_name = fellow.split()
    image_link = full_name[0]
    
    fellow=request.args.get('fellow', fellow)
    print()
    return render_template('aboutMePage.html', fellow=fellow, name= image_link, data= pic_data, intro= about_me)

@app.route('/<fellow>/experience')
def experiencePage(fellow):
    if fellow == "Reginald Amedee":
        experience=[{"Company" : "Vimeo", "Role": "Account Manager", "JobDescription": ['Managed book of business worth $6,235,395 across 200 accounts.',
'Navigated difficult customer facing interactions by objection handling, being a subject matter expert, infusing messaging with data, and anchoring product recommendations to company objectives resulting in more than $1,000,000 in upsell.', 'Worked closely with solution engineers and technical program managers to oversee client onboarding which resulted in product implementations and projects being completed according to Vimeo’s service level agreements.'], 'Date': "Aug 2019 - Feb 2022"},{"Company" : "AFreeBird.org", "Role": "Web Enigneer", "JobDescription": ['Utilized best in class web design practices, made various web pages more web responsive on multiple screen sizes',
'Saved organization over $10,000 a year by being the lead developer on their newsletter generator application ', 'Built out data models with Python and Django according to the system design documentation given which fulfilled product requirements by the CEO.', 'Wrote technical documentation on how to use the platform and effectively communicated and demoed the application to cross functional teams who will use the product resulting in a much easier onboarding process.'], "Date": "Feb 2023 - June 2023"}, {"Company" : "B.D.P.A", "Role": "Technical Instructor", "JobDescription": ['Demonstrated an exceptional ability to teach and communicate complex coding concepts to students of varying skill levels, resulting in hihgly-engaged and knowledable learners.',
'Recreated popular website layouts with students by utilizing replit.com integrated development environment.'], "Date": "Feb 2023 - Aug 2023"}]
        data="Reginald Amedee"
    return render_template('experiencePage.html', data=data, experience=experience)

@app.route('/<fellow>/projects')
def hobbiesPage(fellow):
    projectImage1=os.path.join(projectImageDir, 'PokemonCard.png')
    projectImage2=os.path.join(projectImageDir, 'register_user.png')
    projectImage3=os.path.join(projectImageDir, 'elden_ring_pic.png')

    if fellow == "Reginald Amedee":
        data="Reginald Amedee"
        projects=[{"Project_Blurb" : "YourPokedex", "Project_Image": projectImage1, "Project_Url": "https://github.com/Reggie-Amedee-Tech/pokemonreactapp"},
                {"Project_Blurb": "Calisthenics Prime", "Project_Image": projectImage2, "Project_Url": "https://github.com/Reggie-Amedee-Tech/calisthenics-prime"},{"Project_Blurb": "Reddit-Lite", "Project_Image": projectImage3, "Project_Url": "https://redditprime.netlify.app/"} ]
    return render_template('projectsPage.html', data=data, projects=projects,)


@app.route('/<fellow>/education')
def education(fellow):
    if fellow == "Reginald Amedee":
        experience=[{"Company" : "St. John's University", "Role": "Bachelor's degree, English; Business & English;", 'Date': "2010 - 2015"},{"Company" : "Coding Dojo", "Role": "Activities and societies: Certificate of completion", "JobDescription": [' Worked on projects that included Techonologies such as HTML/HTML5, CSS, MERN Stack, and JavaScript'], "Date": "March 2021 - July 2021"}]
        data="Reginald Amedee"
    

    return render_template('education.html', data = data, experience = experience)


@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    
    keys = request.form.keys()

    if "name" not in keys:
        return Response("Invalid name", status=400)
    name = request.form['name']
    if not name:
        return Response("Invalid name", status=400)

    if "email" not in keys:
        return Response("Invalid email", status=400)
    email = request.form['email']
    if not email or email.count("@") != 1:
        return Response("Invalid email",status=400)
    
    if "content" not in keys:
        return Response("Invalid content", status=400)
    content = request.form['content']
    if not content:
        return Response("Invalid content", status=400)

    timeline_post = TimelinePost.create(name=name,email=email,content=content)
    return model_to_dict(timeline_post)

@app.route('/api/timeline_post', methods=['GET'])
def get_time_line_post():
    data = TimelinePost.select().order_by(TimelinePost.created_on.desc())
    data = [model_to_dict(d) for d in data]

    return jsonify(data)

@app.route('/timeline', methods=['POST', 'GET'])
def timeline():

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        content = request.form.get("content")
        timeline_post = TimelinePost.create(name=name,email=email,content=content)
    redirect('timeline.html')

    data = TimelinePost.select().order_by(TimelinePost.created_on.desc())

    return render_template('timeline.html', title="timeline", data=data)

@app.route('/api/timeline_post/<id>', methods=['DELETE'])
def delete_time_line_post(id):
    print(id)
    try:
        timeline_post = TimelinePost.get_by_id(id)
        timeline_post.delete_instance()
        return f"Successfully deleted timeline post with id {id}\n", 200
    except TimelinePost.DoesNotExist:
        return f"Timeline post with id {id} does not exist\n", 404
    except Exception as e:
        return f"An error occurred while deleting the timeline post: {str(e)}\n", 500

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase('file:memory?mode=memory&cache=shared', uri=True)
else:
    mydb = MySQLDatabase(os.getenv("MYSQL_DATABASE"),
                        user=os.getenv("MYSQL_USER"),
                        password=os.getenv("MYSQL_PASSWORD"),
                        host=os.getenv("MYSQL_HOST"),
                        port=3306
                        )